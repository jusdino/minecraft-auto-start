import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../auth/auth.service';
import { MCServersService } from '../mcservers.service';

@Component({
  selector: 'app-mcserver-add',
  templateUrl: './mcserver-add.component.html',
  styleUrls: ['./mcserver-add.component.css']
})
export class MCServerAddComponent {

  constructor(
    public mcServers: MCServersService
  ) {}

}
