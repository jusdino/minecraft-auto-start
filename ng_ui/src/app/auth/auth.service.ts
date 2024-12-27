import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, timer } from 'rxjs';
import awsconfig from '../../aws-export';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(
    private http: HttpClient
  ) {
    timer(0, 10000).subscribe(_ => this.checkAuthenticated());
  }

  public checkAuthenticated() {
    console.log('Checking authentication');
    const expiresAtString = localStorage.getItem('expiresAt')
    if (expiresAtString != null) {
      const expiresAt = Date.parse(expiresAtString);
      const now = Date.now();
      const isAuthenticated = expiresAt > now;
      if (isAuthenticated) {
        console.log('User is authenticated');
      }
      const refreshAtString = localStorage.getItem('refreshAt');
      if (refreshAtString != null) {
        const refreshAt = Date.parse(refreshAtString);
        if (refreshAt < now) {
          console.log('Refreshing tokens');
          this.refreshTokens();
        }
      }
      return isAuthenticated;
    }
    return false;
  }

  public getIdToken(): string | null {
    return localStorage.getItem('idToken');
  }
  getLoginUrl(): string {
    const loginResponseType = 'code';
    const loginUriQuery = [
      `?client_id=${awsconfig.awsUserPoolWebClientId}`,
      `&response_type=${loginResponseType}`,
      `&scope=${encodeURIComponent(awsconfig.oauth.scope.join(' '))}`,
      `&redirect_uri=${encodeURIComponent(awsconfig.oauth.redirectSignIn)}`,
    ].join('');
    const loginUri = `${awsconfig.oauth.domain}/oauth2/authorize${loginUriQuery}`;

    return loginUri;
  }

  getTokensFromCode(code: string): Observable<any> {
    const body = new URLSearchParams();
    body.set('grant_type', 'authorization_code');
    body.set('client_id', awsconfig.awsUserPoolWebClientId);
    body.set('code', code);
    body.set('redirect_uri', awsconfig.oauth.redirectSignIn);

    const options = {
      headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      },
    };

    return this.http.post<any>(`${awsconfig.oauth.domain}/oauth2/token`, body.toString(), options);
  }

  private refreshTokens() {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      const options = {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      };
  
      const body = new URLSearchParams();
      body.set('grant_type', 'refresh_token');
      body.set('client_id', awsconfig.awsUserPoolWebClientId);
      body.set('refresh_token', refreshToken);
      body.set('redirect_uri', awsconfig.oauth.redirectSignIn);
  
    this.http.post<any>(`${awsconfig.oauth.domain}/oauth2/token`, body.toString(), options)
      .subscribe({
        next: (response: any) => {
          this.setTokens(response);
        },
        error: (error) => {
          console.error('Error refreshing tokens:', error);
          this.clearTokens();
          window.location.replace(this.getLoginUrl());
        }
      });
    }
  }

  setTokens(tokens: any) {
    localStorage.setItem('idToken', tokens.id_token);
    localStorage.setItem('accessToken', tokens.access_token);
    localStorage.setItem('refreshToken', tokens.refresh_token);
    const expiresAt: Date = new Date(Date.now() + (tokens.expires_in * 1000));
    // 90% of the TTL
    const refreshAt: Date = new Date(Date.now() + (tokens.expires_in * 900));
    localStorage.setItem('expiresAt', expiresAt.toString());
    console.log('Refresh at', refreshAt);
    localStorage.setItem('refreshAt', refreshAt.toString());
  }

  clearTokens() {
  localStorage.clear();
  }
}
