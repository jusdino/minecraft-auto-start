import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Observer, BehaviorSubject, of } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { AuthContext } from './models/auth-context';
import { ICognitoUserPoolData, CognitoUserPool, AuthenticationDetails, CognitoUser } from 'amazon-cognito-identity-js';

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

	constructor(
		private http: HttpClient
	) {
		console.log('AuthService contstructor');
		this.http.get<ICognitoUserPoolData>('../api/user_pool').pipe(
			tap(pool_data => {
				console.log('Received user_pool data: ' + pool_data);
				this.userPool = new CognitoUserPool(pool_data);
			}),
			catchError(err => {
				console.log(err);
				return of(null);
			})
		).subscribe();
	}

	login(): Observable<boolean> {
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
					console.log(this);
					authService.authContext.user = cognitoUser;
					authService.authContext.session = result;
					console.log("Login successful");
					observer.next(true);
				},
				onFailure: function (err) {
					console.log(err.message);
					console.log(err.message);
					observer.next(false);
				},
				newPasswordRequired: function(userAttributes, requiredAttributes) {
					authService.authContext.user = cognitoUser;
					authService.challengeData = {
						userAttributes: userAttributes
					}
					authService.loginChallenge.next('newpassword');
				}
			});
		});
	}
	
	public newPassword(): Observable<boolean> {
		const auth = this;
		return new Observable((observer: Observer<boolean>) => {
			this.authContext.user.completeNewPasswordChallenge(this.newPasswordCredentials.Password1, {}, {
				onSuccess: function(result) {
					console.log(this);
					auth.authContext.session = result;
					console.log('password changed');
					observer.next(true);
				},
				onFailure: function (err) {
					console.log(err);
					observer.next(false);
				}
			});
		});
	}
}
