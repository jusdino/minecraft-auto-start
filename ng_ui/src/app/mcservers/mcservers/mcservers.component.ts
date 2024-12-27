import { Component } from '@angular/core';
import { AuthService } from '../../auth/auth.service';
import { MCServersService } from '../mcservers.service';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MCServer } from '../models/mcserver';

@Component({
  selector: 'app-mcservers',
  templateUrl: './mcservers.component.html',
  styleUrls: ['./mcservers.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    MatCardModule,
    MatProgressBarModule,
    MatDividerModule
  ],
  providers: [MCServersService]
})
export class MCServersComponent {
  constructor(
    public mcServers: MCServersService,
    public auth: AuthService
  ) {}

  isServerLaunchable(server: MCServer): boolean {
      console.log('Server:', server);
      return server.online === false && 
        server.launching === false
  }
}
