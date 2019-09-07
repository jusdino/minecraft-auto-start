import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ServersComponent } from './servers/servers.component';
import { LoginComponent } from './auth/login/login.component';

const routes: Routes = [
	{ path: '', redirectTo: '/servers', pathMatch: 'full' },
	{ path: 'servers', component: ServersComponent },
  { path: 'login', component: LoginComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {useHash: true})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
