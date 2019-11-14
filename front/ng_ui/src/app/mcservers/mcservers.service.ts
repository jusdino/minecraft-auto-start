import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Observable, timer, of } from 'rxjs';
import { concatMap, tap, catchError } from 'rxjs/operators';
import { AuthService } from '../auth/auth.service';

import { MCServer } from './models/mcserver';

@Injectable({
  providedIn: 'root'
})
export class MCServersService {
  public servers: MCServer[];
  public newServer: MCServer = new MCServer();
  public servers$: Observable<MCServer[]>;
  private BASE_URL: string = '/servers';

  constructor(
    private http: HttpClient,
    private auth: AuthService
  ) {
    this.servers$ = timer(0, 5000).pipe(
      concatMap( _ => this.getServers())
    );
  }

  getServers(): Observable<MCServer[]> {
    console.log('Checking servers');
    const url: string = `${this.BASE_URL}/`;
    const headers = this.getHeaders();
    return this.http.get<MCServer[]>(url, {headers: headers}).pipe(
      tap( servers => this.servers = servers),
      catchError(err => {
        console.log(err);
        return of([]);
      })
    );
  }

  public submitNew() {
    console.log('Submitting new server');
    const url: string = `${this.BASE_URL}/`;
    const headers = this.getHeaders();
    this.http.post<MCServer>(url, this.newServer, {headers: headers}).pipe(
      tap( server => {
        this.newServer = new MCServer();
        this.getServers().subscribe();
      }),
      catchError(err => {
        console.log(err);
        return null;
      })
    ).subscribe();
  }

  getHeaders() {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authentication': `Bearer ${this.auth.authContext.token}`
    });

  }
}
