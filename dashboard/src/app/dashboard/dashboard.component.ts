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
import { IconDirective } from '@coreui/icons-angular';


import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ChartData, Chart, ChartOptions, registerables } from 'chart.js';
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

  // -----------------------------------------------------------------

  VarIncome: any = ' dashboard 12.5';
  VarReturns: any = ' cards 152.5';

  errorMessage: string = '';
  filename: File | null = null;
  metadata: any = null;
  Data_toPlot: any = null;
  stats: any = null;
  // chart: Chart | null = null;
  server_ip: string = 'http://0.0.0.0:8080';
  Purch_Amt: any = null;
  Quantity: any = null;
  Returns: any = null;
  Churn: any = null;
  labels_vector: any = null;
  data_for_chart1: any = null;

  constructor() {
    Chart.register(...registerables);
  }

  // Handle file selection
  onFileSelected(event: any): void {
    this.filename = event.target.files[0];
  }

  // Function to upload CSV file
  uploadCSV(): void {
    if (!this.filename) {
      this.errorMessage = 'Please select a CSV file.';
      return;
    }

    const formData = new FormData();
    formData.append('file', this.filename);

    // Make the API call to upload the CSV file to FastAPI
    axios
      .post('http://127.0.0.1:8080/upload-csv/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((response) => {
        if (response.data.status === 'success') {
          // Update the Dashboard
          this.metadata = response.data.metadata;
          this.Data_toPlot = response.data.data_dict;
          this.stats = response.data.stats_dict;
          this.build_data_for_charts();
          console.log('apiStats' + this.stats);
          // this.createChart();
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
  build_data_for_charts(): void {
    this.Purch_Amt = this.Data_toPlot.data.map((row: any) => row['Purch_Amt']);
    this.Quantity = this.Data_toPlot.data.map((row: any) => row['Quantity']);
    this.Returns = this.Data_toPlot.data.map((row: any) => row['Returns']);
    this.Churn = this.Data_toPlot.data.map((row: any) => row['Churn']);
    this.labels_vector = this.Data_toPlot.data.map((row: any) => row['Date']);
    console.log('this.metadata.columns=' + this.metadata.columns);
    console.log('Quantity=' + this.Quantity);
    console.log('labels_vector=' + this.labels_vector);

    this.data_for_chart1 = {
      labels: this.labels_vector,
      datasets: [
        {
          label: 'Income',
          backgroundColor: '#f87979',
          data: this.Purch_Amt,
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
        {
          label: 'Quantity',
          backgroundColor: '#f87979',
          data: this.Quantity,
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
        {
          label: 'Returns',
          backgroundColor: '#f87979',
          data: this.Returns,
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
        {
          label: 'Churn',
          backgroundColor: '#f87979',
          data: this.Churn,
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
      ],
    };
  }

  // // Function to create a chart using Chart.js
  // createChart(): void {
  //   if (this.chart) {
  //     this.chart.destroy(); // Destroy the existing chart if it exists
  //   }
  //   this.chart = new Chart('canvas', {
  //     type: 'line', // Can be 'bar', 'line', etc.
  //     data: this.data_for_chart1,
  //     options: {
  //       scales: {
  //         y: {
  //           beginAtZero: true,
  //         },
  //       },
  //     },
  //   });
  // }
  // -----------------------------------------------------------------

  public clients: IClient[] = [
    {
      name: 'Yiorgos Avraamu',
      state: 'New',
      registered: 'Jan 1, 2021',
      country: 'Us',
      usage: 50,
      period: 'Jun 11, 2021 - Jul 10, 2021',
      payment: 'Mastercard',
      activity: '10 sec ago',
      avatar: './assets/images/avatars/1.jpg',
      status: 'success',
      color: 'success',
    },
    {
      name: 'Avram Tarasios',
      state: 'Recurring ',
      registered: 'Jan 1, 2021',
      country: 'Ie',
      usage: 10,
      period: 'Jun 11, 2021 - Jul 10, 2021',
      payment: 'Visa',
      activity: '5 minutes ago',
      avatar: './assets/images/avatars/2.jpg',
      status: 'danger',
      color: 'info',
    },
    {
      name: 'Quintin Ed',
      state: 'New',
      registered: 'Jan 1, 2021',
      country: 'Ma',
      usage: 74,
      period: 'Jun 11, 2021 - Jul 10, 2021',
      payment: 'Stripe',
      activity: '1 hour ago',
      avatar: './assets/images/avatars/3.jpg',
      status: 'warning',
      color: 'warning',
    },
    {
      name: 'Enéas Kwadwo',
      state: 'Sleep',
      registered: 'Jan 1, 2021',
      country: 'Es',
      usage: 98,
      period: 'Jun 11, 2021 - Jul 10, 2021',
      payment: 'Paypal',
      activity: 'Last month',
      avatar: './assets/images/avatars/4.jpg',
      status: 'secondary',
      color: 'danger',
    },
    {
      name: 'Agapetus Tadeáš',
      state: 'New',
      registered: 'Jan 1, 2021',
      country: 'Es',
      usage: 22,
      period: 'Jun 11, 2021 - Jul 10, 2021',
      payment: 'ApplePay',
      activity: 'Last week',
      avatar: './assets/images/avatars/5.jpg',
      status: 'success',
      color: 'primary',
    },
    {
      name: 'Friderik Dávid',
      state: 'New',
      registered: 'Jan 1, 2021',
      country: 'Co',
      usage: 43,
      period: 'Jun 11, 2021 - Jul 10, 2021',
      payment: 'Amex',
      activity: 'Yesterday',
      avatar: './assets/images/avatars/6.jpg',
      status: 'info',
      color: 'dark',
    },
  ];

  public mainChart: IChartProps = { type: 'line' };
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
    console.log('info: new this.csvData=' + this.Data_toPlot);
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
