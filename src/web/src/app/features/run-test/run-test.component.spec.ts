import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { RunTestComponent } from './run-test.component';

const BASE_URL = 'http://localhost:8080';

describe('RunTestComponent', () => {
  let fixture: ComponentFixture<RunTestComponent>;
  let component: RunTestComponent;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RunTestComponent, NoopAnimationsModule],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(RunTestComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('submits the form and polls until the run completes', fakeAsync(() => {
    component.submit();

    const submitReq = httpMock.expectOne(`${BASE_URL}/api/telemetry-tests`);
    expect(submitReq.request.method).toBe('POST');
    submitReq.flush({ runId: 'run-1' });
    tick();

    const firstStatus = httpMock.expectOne(`${BASE_URL}/api/telemetry-tests/run-1`);
    firstStatus.flush({ runId: 'run-1', completed: false, error: null, metrics: null, completedAt: null });

    tick(2000);
    const secondStatus = httpMock.expectOne(`${BASE_URL}/api/telemetry-tests/run-1`);
    secondStatus.flush({
      runId: 'run-1',
      completed: true,
      error: null,
      metrics: { p50_ms: 12.3 },
      completedAt: '2026-01-01T00:00:00Z',
    });
    tick();

    expect(component.status()?.completed).toBeTrue();
    expect(component.metricsEntriesOf(component.status())).toEqual([['p50_ms', 12.3]]);

    // Polling must stop once the run is completed -- no further request within another interval tick.
    tick(2000);
    httpMock.expectNone(`${BASE_URL}/api/telemetry-tests/run-1`);
  }));

  it('surfaces a submit error without starting to poll', fakeAsync(() => {
    component.submit();

    const submitReq = httpMock.expectOne(`${BASE_URL}/api/telemetry-tests`);
    submitReq.flush('boom', { status: 500, statusText: 'Server Error' });
    tick();

    expect(component.submitError()).toContain('Failed to submit');
    expect(component.runId()).toBeNull();
  }));
});
