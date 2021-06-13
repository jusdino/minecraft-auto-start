import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { NotifierModule } from 'angular-notifier';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AuthModule } from './auth/auth.module';
import { LoginComponent } from './auth/login/login.component';
import { MCServersModule } from './mcservers/mcservers.module';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    AppRoutingModule,
    NgbModule,
    NotifierModule.withConfig({
      position: {
        horizontal: {
          position: "right"
        },
        vertical: {
          position: "top"
        }
      },
      behaviour: {
        autoHide: 5000
      }
    }),
    AuthModule,
    MCServersModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
