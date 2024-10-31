import { Component, Input, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NgTemplateOutlet } from '@angular/common';
import { NgFor } from '@angular/common';
import {
  CardComponent,
  BorderDirective,
  ButtonDirective,
  CardBodyComponent,
  CardFooterComponent,
  CardGroupComponent,
  CardHeaderComponent,
  CardImgDirective,
  CardLinkDirective,
  CardSubtitleDirective,
  CardTextDirective,
  CardTitleDirective,
  ColComponent,
  GutterDirective,
  ListGroupDirective,
  ListGroupItemDirective,
  RowComponent,
  TabDirective,
  TabPanelComponent,
  TabsComponent,
  TabsContentComponent,
  TabsListComponent,
  TextColorDirective,
} from '@coreui/angular';
import { IconDirective } from '@coreui/icons-angular';

type CardColor = {
  color: string;
  textColor?: string;
};

@Component({
  selector: 'app-cards',
  templateUrl: './cards.component.html',
  styleUrls: ['./cards.component.scss'],
  standalone: true,
  imports: [
    CardComponent,
    RowComponent,
    NgFor,
    ColComponent,
    TextColorDirective,
    CardHeaderComponent,
    CardBodyComponent,
    CardTitleDirective,
    CardTextDirective,
    ButtonDirective,
  ],
})
export class CardsComponent implements OnInit {
  @Input() inputFromParent: any = '';

  constructor() {}

  ngOnInit(): void {}

  colors: CardColor[] = [
    { color: 'primary', textColor: 'primary' },
    { color: 'secondary', textColor: 'secondary' },
    { color: 'success', textColor: 'success' },
    { color: 'danger', textColor: 'danger' },
    { color: 'warning', textColor: 'warning' },
    { color: 'info', textColor: 'info' },
    { color: 'light' },
    { color: 'dark' },
  ];

  imgContext = { $implicit: 'top', bottom: 'bottom' };

  tabs = ['Active', 'List', 'Disabled'];
}
