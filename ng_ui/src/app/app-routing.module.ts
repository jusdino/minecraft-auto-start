import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { MCServersComponent } from './mcservers/mcservers/mcservers.component';
import { LoginComponent } from './auth/login/login.component';

const routes: Routes = [
	{ path: '', redirectTo: '/servers', pathMatch: 'full' },
	{ path: 'servers', component: MCServersComponent },
  { path: 'login', component: LoginComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {useHash: true})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
