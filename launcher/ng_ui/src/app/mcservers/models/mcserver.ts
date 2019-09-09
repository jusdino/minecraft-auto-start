import { MCStatus } from './mcstatus';

export class MCServer {
  constructor(
    public name?: string,
    public hostname?: string,
    public id?: number,
    public status?: MCStatus
  ) {}
}

