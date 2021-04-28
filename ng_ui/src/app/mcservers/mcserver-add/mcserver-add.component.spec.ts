import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MCServerAddComponent } from './mcserver-add.component';

describe('MCServerAddComponent', () => {
  let component: MCServerAddComponent;
  let fixture: ComponentFixture<MCServerAddComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MCServerAddComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MCServerAddComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
