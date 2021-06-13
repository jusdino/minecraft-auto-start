import { MCDescription } from './mcdescription';
import { MCPlayers } from './mcplayers';
import { MCVersion } from './mcversion';

export class MCStatus {
  constructor(
    description: MCDescription,
    players: MCPlayers,
    version: MCVersion
  ) {}
}
