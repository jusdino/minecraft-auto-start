import { MCPlayers } from './mcplayers';
import { MCVersion } from './mcversion';

export interface MCServer {
    name: string;
    hostname: string;
    description: string;
    online?: boolean;
    launching?: boolean;
    mc_version: MCVersion
    favicon?: string | null;
    players: MCPlayers;
    status_time: number;
    launch_time: number;
    launch_pct?: number;
    version?: number;
    instance_configuration?: any;
}
