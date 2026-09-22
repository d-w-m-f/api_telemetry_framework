import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { BehaviorSubject, interval, of } from 'rxjs';
import { startWith, switchMap, takeWhile } from 'rxjs/operators';

import { ApiClient, TelemetryTestStatusResponse } from '../../core/api-client';

const POLL_INTERVAL_MS = 2000;

@Component({
  selector: 'app-run-test',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatTableModule,
  ],
  templateUrl: './run-test.component.html',
  styleUrl: './run-test.component.scss',
})
export class RunTestComponent {
  private readonly apiClient = inject(ApiClient);
  private readonly formBuilder = inject(FormBuilder);

  // MVP supports exactly one combination end-to-end (see spec/bootstrap.md's MVP scope) -- selects carry a
  // single option each rather than being hardcoded, so wiring up a second option later is a template change,
  // not a rewrite.
  readonly languages = ['python'];
  readonly frameworks = ['fastapi_async'];
  readonly testCategories = ['read'];
  readonly testTypes = ['simple_read'];

  readonly form = this.formBuilder.nonNullable.group({
    language: [this.languages[0]],
    framework: [this.frameworks[0]],
    testCategory: [this.testCategories[0]],
    testType: [this.testTypes[0]],
  });

  private readonly submittingSubject = new BehaviorSubject(false);
  private readonly runIdSubject = new BehaviorSubject<string | null>(null);
  private readonly errorSubject = new BehaviorSubject<string | null>(null);

  readonly isSubmitting = toSignal(this.submittingSubject, { initialValue: false });
  readonly submitError = toSignal(this.errorSubject, { initialValue: null });
  readonly runId = toSignal(this.runIdSubject, { initialValue: null });

  // Polling boundary per angular.md §1: HttpClient stays Observable-based, converted to a Signal here at
  // the point of use. runIdSubject re-triggers the whole chain each submit; takeWhile(..., true) keeps
  // polling until the run completes and includes that final, completed emission.
  readonly status = toSignal<TelemetryTestStatusResponse | null>(
    this.runIdSubject.pipe(
      switchMap((id) =>
        id === null
          ? of(null)
          : interval(POLL_INTERVAL_MS).pipe(
              startWith(0),
              switchMap(() => this.apiClient.getStatus(id)),
              takeWhile((response) => !response.completed, true),
            ),
      ),
    ),
    { initialValue: null },
  );

  submit(): void {
    if (this.form.invalid || this.submittingSubject.value) {
      return;
    }
    this.submittingSubject.next(true);
    this.errorSubject.next(null);
    this.runIdSubject.next(null);

    this.apiClient.submitTest(this.form.getRawValue()).subscribe({
      next: (response) => {
        this.submittingSubject.next(false);
        this.runIdSubject.next(response.runId);
      },
      error: () => {
        this.submittingSubject.next(false);
        this.errorSubject.next('Failed to submit the test. Is the backend running?');
      },
    });
  }

  metricsEntriesOf(status: TelemetryTestStatusResponse | null): [string, unknown][] {
    return status?.metrics ? Object.entries(status.metrics) : [];
  }
}
