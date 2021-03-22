import { MCStatus } from './mcstatus';

export class MCServer {
  constructor(
    public launch_time?: boolean,
    public name?: string,
    public hostname?: string,
    public status?: MCStatus,
    public status_time?: string,
    public version?: number
  ) {}
}
