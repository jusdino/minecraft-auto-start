import { TestBed } from '@angular/core/testing';

import { MCServersService } from './mcservers.service';

describe('MCServersService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: MCServersService = TestBed.get(MCServersService);
    expect(service).toBeTruthy();
  });
});
