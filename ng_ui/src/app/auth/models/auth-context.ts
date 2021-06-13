import { CognitoAccessToken, CognitoRefreshToken, CognitoUser, CognitoUserSession } from 'amazon-cognito-identity-js';
import { timer, of, Observable, BehaviorSubject } from 'rxjs';
import { concatMap } from 'rxjs/operators';

export class AuthContext {
  session: CognitoUserSession;
  user: CognitoUser;
  timer$: Observable<boolean>;
  public authenticated: BehaviorSubject<boolean> = new BehaviorSubject(false);
  public authenticated$: Observable<boolean> = this.authenticated.asObservable();

  constructor (user?: CognitoUser, session?: CognitoUserSession) {
    console.log("Creating new AuthContext");
    console.log("User: " + user);
    console.log("Session: " + session);
    this.user = user;
    this.session = session;
    timer(0, 10000).subscribe(_ => this.check_authenticated());
  }

  public check_authenticated() {
    console.log('Checking authentication');
    console.log(this.session);
    if (this.session != null) {
      console.log(this.session.getIdToken().getExpiration());
      console.log(Date.now());
    }
    let isAuthenticated = this.session != null && this.session.getIdToken().getExpiration() > Date.now()/1000;
    console.log('Authenticated: ' + isAuthenticated);
    this.authenticated.next(isAuthenticated);
    return isAuthenticated;
  }
}
