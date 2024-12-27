import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MCServersComponent } from './mcservers.component';
import { MCServersService } from '../mcservers.service';
import { AuthService } from '../../auth/auth.service';
import { MCServer } from '../models/mcserver';
import { of } from 'rxjs';
import { MatCardModule } from '@angular/material/card';
import { By } from '@angular/platform-browser';

describe('MCServersComponent', () => {
  let component: MCServersComponent;
  let fixture: ComponentFixture<MCServersComponent>;
  let mcServersServiceMock: Partial<MCServersService>;
  let authServiceMock: jasmine.SpyObj<AuthService>;

  beforeEach(() => {
    // Create a simple mock object with just the servers$ property
    mcServersServiceMock = {
      servers$: of([]) // Default empty array
    };

    authServiceMock = jasmine.createSpyObj('AuthService', [
      'isAuthenticated'
    ]);

    TestBed.configureTestingModule({
      imports: [
        MCServersComponent,
        MatCardModule
      ],
      providers: [
        { provide: MCServersService, useValue: mcServersServiceMock },
        { provide: AuthService, useValue: authServiceMock }
      ]
    });

    fixture = TestBed.createComponent(MCServersComponent);
    component = fixture.componentInstance;

    // We need to specifically override the injected mcServers property
    // with our mock
    component.mcServers = mcServersServiceMock as MCServersService;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display servers when they are loaded', () => {
    const mockServers: MCServer[] = [
      { 
        hostname: 'test.example.org',
        name: 'test',
        status: { description: 'Online' },
        launch_time: +new Date('2024-01-24T12:00:00Z'),
        status_time: +new Date('2024-01-24T12:00:00Z'),
      } as MCServer
    ];
    
    // Update the mock observable with test data
    mcServersServiceMock.servers$ = of(mockServers);

    fixture.detectChanges();
    
    // Check that we have the mat-card we expect
    const matCards = fixture.nativeElement.querySelectorAll('mat-card');
    expect(matCards.length).toBe(1);

    // Verify that the hostname and name are displayed in our card
    const cardContent = matCards[0].textContent;
    expect(cardContent).toContain('test.example.org');
    expect(cardContent).toContain('test');
  });

  describe('isServerOnline', () => {
    it('should return true when server is online', () => {
      const server: MCServer = {
        status: { description: 'Some server that is fun' }
      } as MCServer;
      
      expect(component.isServerOnline(server)).toBeTrue();
    });

    it('should return false when server is offline', () => {
      const server: MCServer = {
        status: { description: 'Offline' }
      } as MCServer;
      
      expect(component.isServerOnline(server)).toBeFalse();
    });

    it('should return false when status is undefined', () => {
      const server: MCServer = {} as MCServer;
      
      expect(component.isServerOnline(server)).toBeFalse();
    });
  });


  describe('isServerLaunchable', () => {
    it('should return true when server is offline and not launching', () => {
      const server: MCServer = {
        status: { description: 'Offline' }
      } as MCServer;
      expect(component.isServerLaunchable(server)).toBeTrue();
    });

    it('should return false before server details are loaded', () => {
        const server: MCServer = {
  "name": "lu-tze",
  "hostname": "lu-tze.dev.frahm.space",
  "version": 446,
  "status_time": 1735099057.475343,
  "status": {
    "description": "Offline",
    "players": {
      "max": 0,
      "online": 0
    },
    "version": {
      "name": "N/A",
      "protocol": -1
    },
    "favicon": null
  },
  "launch_time": 1733728419,
  "instance_configuration": {
    "instance_type": "t3.large",
    "volume_size": 20,
    "memory_size": "6144m",
    "java_version": "17",
    "s3_schematic_prefix": "common"
  }
}
    });

    it('should return false when server is online', () => {
      const server: MCServer = {
        status: { description: 'Online' }
      } as MCServer;
      
      expect(component.isServerLaunchable(server)).toBeFalsy();
    });

    it('should return false when server is launching', () => {
      const server: MCServer = {
        status: { description: 'Offline' },
        launch_pct: 50
      } as MCServer;
      
      expect(component.isServerLaunchable(server)).toBeFalsy();
    });
  });
});
