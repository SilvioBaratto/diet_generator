// src/app/app.routes.ts

import { Routes } from '@angular/router';

import { DashboardComponent } from './components/dashboard/dashboard.component';
import { WeeklyComponent } from './components/weekly/weekly.component';
import { WeeklyDetailsComponent } from './components/weekly/weekly-details/weekly-details.component';
import { RecipeDetailsComponent } from './components/weekly/recipe-details/recipe-details.component';
import { SettingsComponent } from './components/settings/settings.component';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'weekly', component: WeeklyComponent },
  { path: 'weekly/:diet_id', component: WeeklyDetailsComponent },
  { path: 'recipe/:meal_id', component: RecipeDetailsComponent },
  { path: 'settings', component: SettingsComponent },
  { path: '**', redirectTo: 'dashboard' },
];
