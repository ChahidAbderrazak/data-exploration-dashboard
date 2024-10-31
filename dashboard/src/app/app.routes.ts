// import { Routes } from '@angular/router';

// export const routes: Routes = [];

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HeaderComponent } from './header/header.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { FooterComponent } from './footer/footer.component';
import { CardsComponent } from './cards/cards.component';

// export const routes: Routes = [
//   { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
//   // { path: 'header', component: HeaderComponent },
//   // { path: 'dashboard', component: DashboardComponent },
//   // { path: 'footer', component: FooterComponent },
//   // { path: 'cards', component: CardsComponent },
// ];

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
  },
  {
    path: '',
    component: DashboardComponent,
    data: {
      title: 'Dashboard Home',
    },
    children: [
      {
        path: 'dashboard',
        loadChildren: () =>
          import('./dashboard/routes').then((m) => m.routes),
      },
      // {
      //   path: 'theme',
      //   loadChildren: () =>
      //     import('./views/theme/routes').then((m) => m.routes),
      // },
      // {
      //   path: 'base',
      //   loadChildren: () => import('./views/base/routes').then((m) => m.routes),
      // },
      // {
      //   path: 'buttons',
      //   loadChildren: () =>
      //     import('./views/buttons/routes').then((m) => m.routes),
      // },
      // {
      //   path: 'forms',
      //   loadChildren: () =>
      //     import('./views/forms/routes').then((m) => m.routes),
      // },
      {
        path: 'icons',
        loadChildren: () => import('./views/icons/routes').then((m) => m.routes),
      },
      // {
      //   path: 'notifications',
      //   loadChildren: () =>
      //     import('./views/notifications/routes').then((m) => m.routes),
      // },
      {
        path: 'widgets',
        loadChildren: () => import('./widgets/routes').then((m) => m.routes),
      },
      // {
      //   path: 'charts',
      //   loadChildren: () =>
      //     import('./views/charts/routes').then((m) => m.routes),
      // },
      {
        path: 'pages',
        loadChildren: () => import('./pages/routes').then((m) => m.routes),
      },
    ],
  },
  {
    path: '404',
    loadComponent: () =>
      import('./pages/page404/page404.component').then(
        (m) => m.Page404Component
      ),
    data: {
      title: 'Page 404',
    },
  },
  {
    path: '500',
    loadComponent: () =>
      import('./pages/page500/page500.component').then(
        (m) => m.Page500Component
      ),
    data: {
      title: 'Page 500',
    },
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./pages/login/login.component').then((m) => m.LoginComponent),
    data: {
      title: 'Login Page',
    },
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./pages/register/register.component').then(
        (m) => m.RegisterComponent
      ),
    data: {
      title: 'Register Page',
    },
  },
  { path: '**', redirectTo: 'dashboard' },
];



// @NgModule({
//   imports: [RouterModule.forRoot(routes)],
//   exports: [RouterModule],
// })
// export class AppRoutingModule {}
