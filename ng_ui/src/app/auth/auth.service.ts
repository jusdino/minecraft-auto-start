import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Observer, BehaviorSubject, of } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { AuthContext } from './models/auth-context';
import { ICognitoUserPoolData, CognitoUserPool, AuthenticationDetails, CognitoUser } from 'amazon-cognito-identity-js';
import { NotifierService } from 'angular-notifier';

@Injectable({
	providedIn: 'root'
})
export class AuthService {
	public loginCredentials: any = {
		Username: '',
		Password: ''
	};
	public authContext: AuthContext = new AuthContext();
	public loginChallenge: BehaviorSubject<string> = new BehaviorSubject('login');
	public loginChallenge$: Observable<string> = this.loginChallenge.asObservable();
	public newPasswordCredentials: any = {
		'Password1': '',
		'Password2': ''
	}
	public challengeData: any;
	private userPool: CognitoUserPool;
    private readonly notifier: NotifierService

	constructor(
		private http: HttpClient,
		notifierService: NotifierService
	) {
		this.notifier = notifierService;
		this.http.get<ICognitoUserPoolData>('../api/user_pool').pipe(
			tap(pool_data => {
				console.log('Received user_pool data');
				this.userPool = new CognitoUserPool(pool_data);
			}),
			catchError(err => {
				console.log(err);
				return of(null);
			})
		).subscribe();
	}

	login(): Observable<boolean> {
		let notifier = this.notifier;
		const authService = this;
		const userData = {
			Username: this.loginCredentials.Username,
			Pool: this.userPool
		};
		const authDetails = new AuthenticationDetails(this.loginCredentials);
		const cognitoUser = new CognitoUser(userData);
		return new Observable((observer: Observer<boolean>) => {
			cognitoUser.authenticateUser(authDetails, {
				onSuccess: function(result) {
					authService.authContext.user = cognitoUser;
					authService.authContext.session = result;
					console.log("Login successful");
					observer.next(true);
				},
				onFailure: function (err) {
					console.log(err.message);
					notifier.notify('warning', err.message);
					observer.next(false);
				},
				newPasswordRequired: function(userAttributes, requiredAttributes) {
					authService.authContext.user = cognitoUser;
					authService.challengeData = {
						userAttributes: userAttributes
					}
					notifier.notify('info', 'Time to change your password!');
					authService.loginChallenge.next('newpassword');
				}
			});
		});
	}
	
	public newPassword(): Observable<boolean> {
		const notifier = this.notifier;
		const auth = this;
		return new Observable((observer: Observer<boolean>) => {
			this.authContext.user.completeNewPasswordChallenge(this.newPasswordCredentials.Password1, {}, {
				onSuccess: function(result) {
					console.log(this);
					auth.authContext.session = result;
					console.log('password changed');
					notifier.notify('success', 'Password changed!');
					observer.next(true);
				},
				onFailure: function (err) {
					console.log(err);
					notifier.notify('warning', err.message);
					observer.next(false);
				}
			});
		});
	}
}
