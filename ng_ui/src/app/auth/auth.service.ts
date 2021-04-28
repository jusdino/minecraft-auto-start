import { Injectable, OnInit } from '@angular/core';
import { Observable, of, interval, Observer } from 'rxjs';
import { AuthContext } from './models/auth-context';
import { catchError, map, tap } from 'rxjs/operators';
import { CognitoUserPool, AuthenticationDetails, CognitoUser } from 'amazon-cognito-identity-js';

@Injectable({
	providedIn: 'root'
})
export class AuthService {
	public loginCredentials: any = {
		Username: '',
		Password: ''
	};
	public authContext: AuthContext = new AuthContext();
	public loginChallenge: string = 'login';
	public newPasswordCredentials: any = {
		'Password1': '',
		'Password2': ''
	}
	public challengeData: any;
	private userPool: CognitoUserPool = new CognitoUserPool({
		UserPoolId: "us-west-1_XXXXXXXXX",
		ClientId: "XXXXXXXXXXXXXXXXXXXXXXXXXX"
	});

	constructor() {}

	login(): Observable<boolean> {
		let authService = this;
		let userData = {
			Username: this.loginCredentials.Username,
			Pool: this.userPool
		};
		let authDetails = new AuthenticationDetails(this.loginCredentials);
		let cognitoUser = new CognitoUser(userData);
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
					authService.loginChallenge = 'newpassword';
				}
			});
		});
	}
	
	public newPassword() {
		this.authContext.user.completeNewPasswordChallenge('<N3w password>', this.challengeData['userAttributes'], {
			onSuccess: function(result) {
				console.log(this);
				this.authContext.session = result;
				this.log('password changed');
			},
			onFailure: function (err) {
				console.log(err);
			}
		});
	}

	private handleError<T> (operation = 'operation', result?: T) {
		return (error: any): Observable<T> => {
			console.error(error);
			this.log(`${operation} failed: ${error.message}`);
			return of(result as T);
		}
	}

	private log(message: string) {
		this.log(`AuthService: ${message}`);
	}
}
