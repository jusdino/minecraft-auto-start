import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable()
export class AuthGuard implements CanActivate {

    constructor(
        public auth: AuthService
    ) {}

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
        if (this.auth.checkAuthenticated()) {
            // logged in so return true
            console.log('Logged in');
            return true;
        }

        // not logged in so redirect to login page with the return url
        console.log('Not logged in');
	    window.location.replace(this.auth.getLoginUrl());
        return false;
    }
}