import { Routes } from '@angular/router';
import { MCServersComponent } from './mcservers/mcservers/mcservers.component';
import { AuthGuard } from './auth/auth-guard';
import { LoginComponent } from './auth/login/login.component';

export const routes: Routes = [
	{ path: '', redirectTo: '/servers', pathMatch: 'full'},
	{ path: 'login', component: LoginComponent},
	{ path: 'servers', component: MCServersComponent, canActivate: [AuthGuard] }
];
