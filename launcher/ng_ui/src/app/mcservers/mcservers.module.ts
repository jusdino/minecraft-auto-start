import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MCServersComponent } from './mcservers/mcservers.component';
import { MCServerAddComponent } from './mcserver-add/mcserver-add.component';



@NgModule({
  declarations: [
    MCServersComponent,
    MCServerAddComponent
  ],
  imports: [
    CommonModule,
    FormsModule
  ]
})
export class MCServersModule { }
