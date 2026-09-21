import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface SubmitTelemetryTestRequest {
  language: string;
  framework: string;
  testCategory: string;
  testType: string;
}

export interface SubmitTelemetryTestResponse {
  runId: string;
}

export interface TelemetryTestStatusResponse {
  runId: string;
  completed: boolean;
  error: Record<string, unknown> | null;
  metrics: Record<string, unknown> | null;
  completedAt: string | null;
}

const API_BASE_URL = import.meta.env.NG_APP_API_BASE_URL || 'http://localhost:8080';

@Injectable({ providedIn: 'root' })
export class ApiClient {
  private readonly http = inject(HttpClient);

  submitTest(request: SubmitTelemetryTestRequest): Observable<SubmitTelemetryTestResponse> {
    return this.http.post<SubmitTelemetryTestResponse>(`${API_BASE_URL}/api/telemetry-tests`, request);
  }

  getStatus(runId: string): Observable<TelemetryTestStatusResponse> {
    return this.http.get<TelemetryTestStatusResponse>(`${API_BASE_URL}/api/telemetry-tests/${runId}`);
  }
}
