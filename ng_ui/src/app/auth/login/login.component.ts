import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent implements OnInit {

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.handleAuthCodeCallback();
  }

  handleAuthCodeCallback() {
    console.log('Handling auth code callback');
    this.route.queryParams.subscribe(params => {
      const code = params['code'];
      console.log('Code:', code);
      if (code) {
        this.authService.getTokensFromCode(code).subscribe({
          next: tokens => {
            console.log('Tokens:', tokens);
            this.authService.setTokens(tokens);
            this.router.navigate(['/']);
          },
          error: error => {
            console.error('Error getting tokens from code:', error);
          }
        });
      }
    });
  }
}
