import { MCStatus } from './mcstatus';

export class MCServer {
  constructor(
    public id: number,
    public name: string,
    public hostname: string,
    public status: MCStatus
  ) {}
}

