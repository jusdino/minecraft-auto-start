import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { MCServersComponent } from './mcservers/mcservers.component';
import { MCServerAddComponent } from './mcserver-add/mcserver-add.component';



@NgModule({
  declarations: [
    MCServersComponent,
    MCServerAddComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatProgressBarModule,
    MatDividerModule
  ]
})
export class MCServersModule { }
