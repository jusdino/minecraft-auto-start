import { MCStatus } from './mcstatus';

export class MCServer {
  constructor(
    public launch_time?: number,
    public launch_pct?: number,
    public name?: string,
    public hostname?: string,
    public status?: MCStatus,
    public status_time?: string,
    public version?: number
  ) {}
}
