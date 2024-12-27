import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LocationStrategy, PathLocationStrategy } from '@angular/common';

import { AuthModule } from './auth/auth.module';
import { AuthService } from './auth/auth.service';
import { AuthGuard } from './auth/auth-guard';
import { MCServersComponent } from './mcservers/mcservers/mcservers.component';


@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    AuthModule,
    MCServersComponent
],
  providers: [
    { provide: LocationStrategy, useClass: PathLocationStrategy },
    AuthGuard,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'minecraft-auto-start';

  constructor (
    public auth: AuthService
  ) {}
}
