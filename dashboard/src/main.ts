/// <reference types="@angular/localize" />

import { bootstrapApplication } from '@angular/platform-browser';

import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';

// // upload dataset
// import { UploadCsvComponent } from './app/upload-csv/upload-csv.component';

bootstrapApplication(AppComponent, appConfig).catch((err) =>
  console.error(err)
);
