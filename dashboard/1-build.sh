#!/bin/bash
#### -----------------------   BUILDING THE ANGULAR.JS PROJECT  -------------------------------
ng new angular-dashboard

cd angular-dashboard
npm install bootstrap

npm install chart.js
npm install ng2-charts

#  generate the components
ng generate component header
ng generate component footer
ng generate component dashboard

