import { Injectable, OnInit } from '@angular/core';
import { Observable, of, interval } from 'rxjs';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { User } from './models/user';
import { AuthContext } from './models/auth-context';
import { catchError, map, tap } from 'rxjs/operators';

@Injectable({
	providedIn: 'root'
})
export class AuthService {
	public user: User = new User();
  public authContext: AuthContext = new AuthContext({});
  private BASE_URL: string = '/auth';
	private headers: HttpHeaders = new HttpHeaders({'Content-Type': 'application/json'});

	constructor(
    private http: HttpClient
  ) {}

	login(): Observable<boolean> {
		let url: string = `${this.BASE_URL}/login`;
		return this.http.post(url, this.user, {headers: this.headers}).pipe(
			map(response => {
				this.authContext = new AuthContext(response);
				this.user = this.authContext.user;
				this.log(`Retrieved token for ${this.user.email}`);
				return true;
			}),
			catchError(this.handleError<boolean>(`User ${this.user.email} login`))
		);
	}

	private handleError<T> (operation = 'operation', result?: T) {
		return (error: any): Observable<T> => {
			console.error(error);
			this.log(`${operation} failed: ${error.message}`);
			return of(result as T);
		}
	}

	private log(message: string) {
		console.log(`AuthService: ${message}`);
	}
}
