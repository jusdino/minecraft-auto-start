import { Component, OnInit, OnDestroy } from '@angular/core';
import { MCServersService } from './mcservers.service';

@Component({
  selector: 'app-mcservers',
  templateUrl: './mcservers.component.html',
  styleUrls: ['./mcservers.component.css']
})
export class MCServersComponent {
  constructor(
    public mcServers: MCServersService
  ) {}
}
