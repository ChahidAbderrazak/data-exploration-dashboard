import { DOCUMENT, NgStyle } from '@angular/common';
import {
  Component,
  DestroyRef,
  effect,
  inject,
  OnInit,
  Renderer2,
  signal,
  WritableSignal,
} from '@angular/core';
import { NgIf, NgFor } from '@angular/common';

import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Chart, registerables, ChartOptions, ChartType } from 'chart.js';

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

import { WidgetsBrandComponent } from '../widgets/widgets-brand/widgets-brand.component';
import { WidgetsDropdownComponent } from '../widgets/widgets-dropdown/widgets-dropdown.component';
import { DashboardChartsData, IChartProps } from './dashboard-charts-data';

import axios from 'axios';

interface IClient {
  name: string;
  state: string;
  registered: string;
  country: string;
  usage: number;
  period: string;
  payment: string;
  activity: string;
  avatar: string;
  status: string;
  color: string;
}

@Component({
  templateUrl: 'dashboard.component.html',
  styleUrls: ['dashboard.component.scss'],
  standalone: true,
  imports: [
    WidgetsDropdownComponent,
    TextColorDirective,
    CardComponent,
    CardBodyComponent,
    RowComponent,
    ColComponent,
    ButtonDirective,
    IconDirective,
    ReactiveFormsModule,
    ButtonGroupComponent,
    FormCheckLabelDirective,
    ChartjsComponent,
    NgStyle,
    CardFooterComponent,
    GutterDirective,
    ProgressBarDirective,
    ProgressComponent,
    WidgetsBrandComponent,
    CardHeaderComponent,
    TableDirective,
    AvatarComponent,
    NgIf,
    NgFor,
  ],
})
export class DashboardComponent implements OnInit {
  readonly #destroyRef: DestroyRef = inject(DestroyRef);
  readonly #document: Document = inject(DOCUMENT);
  readonly #renderer: Renderer2 = inject(Renderer2);
  readonly #chartsData: DashboardChartsData = inject(DashboardChartsData);

  // upload csv file

  csvFile: File | null = null;
  UseCaseDetails: any = null;
  csvData: any = null;
  val: any = null;
  type_graph: ChartType = 'bar';
  errorMessage: string = '';
  chartData: any = null;
  chart_purchase_activity: Chart | null = null;
  server_ip: string = 'http://0.0.0.0:8080';
  //  API data format
  DateByMonth: any = null;
  IncomeByMonth: any = null;

  constructor() {
    Chart.register(...registerables);
  }

  // Handle file selection event
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
          this.UseCaseDetails = response.data.metadata;
          this.chartData = response.data;
          this.val = this.UseCaseDetails.num_rows;
          console.log('chartData=' + this.chartData);
          this.DateByMonth = this.chartData.data.map(
            (row: any) => row['DateByMonth']
          );
          this.IncomeByMonth = this.chartData.data.map(
            (row: any) => row['IncomeByMonth']
          );

          //  Update the dashboard data
          this.update_dashboard_data();

          //  Create the chart using Chart.js
          this.create_Chart_purchase_activity();

          //  report error if any
          this.errorMessage = 'Done!';
        } else {
          // Handle error response from the backend
          this.errorMessage = ' Error: ' + response.data.message;
        }
      })
      .catch((error) => {
        console.error(' Error uploading CSV:', error);
        this.errorMessage = ' Failed to upload CSV file.';
      });
  }
  // Function to update dashboard data
  update_dashboard_data(): void {
    console.log('chart labels'); // + this.mainChart.data.labels);
  }
  // Function to create a chart using Chart.js
  create_Chart_purchase_activity(): void {
    if (this.chart_purchase_activity) {
      this.chart_purchase_activity.destroy(); // Destroy the existing chart if it exists
    }
    this.chart_purchase_activity = new Chart('canvas', {
      type: 'line', // Can be 'bar', 'line', etc.
      data: {
        labels: this.DateByMonth,
        datasets: [
          {
            label: 'test ',
            data: this.IncomeByMonth,
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

  public clients: IClient[] = [
    {
      name: 'Katelyn Clark',
      state: '',
      registered: 'ID= 48382',
      country: 'Us',
      usage: 0.01,
      period: '15 transactions',
      payment: 'Mastercard',
      activity: '2023-04-01 13:02:11',
      avatar: './assets/images/avatars/1.jpg',
      status: 'success',
      color: 'success',
    },
    {
      name: 'Lori Taylor',
      state: 'Recurring ',
      registered: 'ID= 6347',
      country: 'Ie',
      usage: 0.01,
      period: '14 transactions',
      payment: 'Mastercard',
      activity: '2022-08-26 16:18:07',
      avatar: './assets/images/avatars/2.jpg',
      status: 'success',
      color: 'info',
    },
    {
      name: 'Roberto Rogers',
      state: 'Recurring ',
      registered: 'ID= 35294',
      country: 'Ma',
      usage: 0.01,
      period: '14 transactions',
      payment: 'Mastercard',
      activity: '2023-08-24 07:18:33',
      avatar: './assets/images/avatars/3.jpg',
      status: 'success',
      color: 'info',
    },
    
  ];

  public mainChart: IChartProps = { type: this.type_graph };
  public mainChartRef: WritableSignal<any> = signal(undefined);
  #mainChartRefEffect = effect(() => {
    if (this.mainChartRef()) {
      this.setChartStyles();
    }
  });
  public chart: Array<IChartProps> = [];
  public trafficRadioGroup = new FormGroup({
    trafficRadio: new FormControl('Month'),
  });

  ngOnInit(): void {
    this.initCharts();
    this.updateChartOnColorModeChange();
  }

  initCharts(): void {
    this.mainChart = this.#chartsData.mainChart;
  }

  setTrafficPeriod(value: string): void {
    this.trafficRadioGroup.setValue({ trafficRadio: value });
    this.#chartsData.initMainChart(value);
    console.log('info: new this.csvData=' + this.csvData);
    this.initCharts();
  }

  handleChartRef($chartRef: any) {
    if ($chartRef) {
      this.mainChartRef.set($chartRef);
    }
  }

  updateChartOnColorModeChange() {
    const unListen = this.#renderer.listen(
      this.#document.documentElement,
      'ColorSchemeChange',
      () => {
        this.setChartStyles();
      }
    );

    this.#destroyRef.onDestroy(() => {
      unListen();
    });
  }

  setChartStyles() {
    if (this.mainChartRef()) {
      setTimeout(() => {
        const options: ChartOptions = { ...this.mainChart.options };
        const scales = this.#chartsData.getScales();
        this.mainChartRef().options.scales = { ...options.scales, ...scales };
        this.mainChartRef().update();
      });
    }
  }
}
