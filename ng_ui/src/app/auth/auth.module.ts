import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';


import { AuthService } from './auth.service';
import { AuthGuard } from './auth-guard';


@NgModule({
  imports: [
    CommonModule,
    FormsModule,
  ],
  providers: [
    AuthService,
    AuthGuard
  ]
})
export class AuthModule { }
