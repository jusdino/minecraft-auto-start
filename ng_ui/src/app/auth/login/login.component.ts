import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
	selector: 'login',
	templateUrl: './login.component.html',
	styleUrls: ['./login.component.css']
})
export class LoginComponent {

	constructor(
		private router: Router, 
		public auth: AuthService,
	) {}

	onLogin() {
		this.auth.login().subscribe(success => {
			if (success === true) {
				this.auth.authContext.check_authenticated();
			}
			console.log('login component recieved login success: ' + success);
		})
	}

	onNewPassword() {
		console.log('onNewPassword()');
		this.auth.newPassword().subscribe(success => {
			if (success === true) {
				this.auth.authContext.check_authenticated();
			}
			console.log('login component recieved new password success: ' + success);
		})
	}
}
