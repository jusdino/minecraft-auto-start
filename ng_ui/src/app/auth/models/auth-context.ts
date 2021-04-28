import { CognitoAccessToken, CognitoRefreshToken, CognitoUser, CognitoUserSession } from 'amazon-cognito-identity-js';
import { timer, of, Observable } from 'rxjs';
import { concatMap } from 'rxjs/operators';

export class AuthContext {
  accessToken: CognitoAccessToken;
  session: CognitoUserSession;
  user: CognitoUser;
  isAuthenticated: boolean;
  public authenticated$: Observable<boolean>;

  constructor (user?: CognitoUser, session?: CognitoUserSession) {
    console.log("Creating new AuthContext");
    console.log("User: " + user);
    console.log("Session: " + session);
    this.user = user;
    this.session = session;
    this.isAuthenticated = false;
    this.authenticated$ = timer(0, 10000).pipe(
      concatMap( _ => of(this.check_authenticated()))
    )
  }

  public check_authenticated() {
    console.log('Checking authentication');
    console.log(this.session);
    if (this.session != null) {
      console.log(this.session.getAccessToken().getExpiration());
      console.log(Date.now());
    }
    this.isAuthenticated = this.session != null && this.session.getAccessToken().getExpiration() > Date.now()/1000;
    console.log('Authenticated: ' + this.isAuthenticated);
    return this.isAuthenticated;
  }
}
