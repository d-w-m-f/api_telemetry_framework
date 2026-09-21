import { Component } from '@angular/core';

import { RunTestComponent } from './features/run-test/run-test.component';

@Component({
  selector: 'app-root',
  imports: [RunTestComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {}
