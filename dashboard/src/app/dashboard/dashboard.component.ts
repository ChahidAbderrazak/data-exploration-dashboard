import { Component } from '@angular/core';
import { NgIf, NgFor } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import axios from 'axios';
// import {
//   Component,
//   DestroyRef,
//   effect,
//   inject,
//   OnInit,
//   Renderer2,
//   signal,
//   WritableSignal,
// } from '@angular/core';

import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ChartOptions } from 'chart.js';
import {
  AvatarComponent,
  ButtonDirective,
  ButtonGroupComponent,
  CardBodyComponent,
  CardComponent,
  CardFooterComponent,
  CardHeaderComponent,
  ColComponent,
  FormCheckLabelDirective,
  GutterDirective,
  ProgressBarDirective,
  ProgressComponent,
  RowComponent,
  TableDirective,
  TextColorDirective,
} from '@coreui/angular';
import { ChartjsComponent } from '@coreui/angular-chartjs';
import { IconDirective } from '@coreui/icons-angular';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [NgIf, NgFor],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent {
  csvFile: File | null = null;
  csvDetails: any = null;
  chartData: any = null;
  errorMessage: string = '';
  chart: Chart | null = null;
  server_ip: string = 'http://0.0.0.0:8080';
  coinPrice: any = null;
  coinName: any = null;

  constructor() {
    Chart.register(...registerables);
  }

  // Handle file selection
  onFileSelected(event: any): void {
    this.csvFile = event.target.files[0];
  }

  // Function to upload CSV file
  uploadCSV(): void {
    if (!this.csvFile) {
      this.errorMessage = 'Please select a CSV file.';
      return;
    }

    const formData = new FormData();
    formData.append('file', this.csvFile);

    // Make the API call to upload the CSV file to FastAPI
    axios
      .post('http://127.0.0.1:8080/upload-csv/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((response) => {
        if (response.data.status === 'success') {
          // Update the Dashboard
          this.csvDetails = response.data.metadata;
          this.chartData = response.data;
          this.createChart();
          this.errorMessage = '';
        } else {
          // Handle error response from the backend
          this.errorMessage = 'Error: ' + response.data.message;
        }
      })
      .catch((error) => {
        console.error('Error uploading CSV:', error);
        this.errorMessage = 'Failed to upload CSV file.';
      });
  }

  // Function to create a chart using Chart.js
  createChart(): void {
    this.coinPrice = this.chartData.data.map(
      (row: any) => row[this.csvDetails.columns[1]]
      // (row: any) => row[this.csvDetails.columns[0]]
    );
    this.coinName = this.chartData.data.map(
      (row: any) => row[this.csvDetails.columns[2]]
    );

    if (this.chart) {
      this.chart.destroy(); // Destroy the existing chart if it exists
    }
    this.chart = new Chart('canvas', {
      type: 'line', // Can be 'bar', 'line', etc.
      data: {
        labels: this.coinName,
        datasets: [
          {
            label: 'test ',
            data: this.coinPrice,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }
}
