import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MCServersService } from './mcservers.service';

describe('MCServersService', () => {
  let service: MCServersService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],  // If the service makes HTTP calls
      providers: [MCServersService]        // Provide the service itself
    });
    service = TestBed.inject(MCServersService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
