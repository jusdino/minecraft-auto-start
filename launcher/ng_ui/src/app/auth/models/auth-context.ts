import { OnInit } from '@angular/core';
import { timer, of, Observable } from 'rxjs';
import { concatMap, merge } from 'rxjs/operators';
import { User } from './user';

export class AuthContext {
  expires: number
  token: string
  user: User
  isAuthenticated: boolean
  public authenticated$: Observable<boolean>;

  constructor (obj: any) {
    this.user = obj.user;
    this.token = obj.token;
    this.expires = obj.expires;
    this.isAuthenticated = false;
    this.authenticated$ = timer(0, 10000).pipe(
      concatMap( _ => of(this.check_authenticated()))
    )
  }

  public check_authenticated() {
    console.log('Checking authentication');
    this.isAuthenticated = this.expires != undefined && this.expires > Date.now();
    return this.isAuthenticated;
  }
}
