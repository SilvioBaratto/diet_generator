import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

interface UserSettingsIn {
  weight?: number;
  height?: number;
  other_data?: string;
  goals?: string;
}
interface UserSettingsOut extends UserSettingsIn {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css'],
})
export class SettingsComponent implements OnInit {
  settings: UserSettingsIn = {};
  successMessage = '';
  errorMessage = '';

  constructor(
    private http: HttpClient,
    private router: Router,
  ) { }

  ngOnInit() {
    this.http
      .get<UserSettingsOut>(
        `${environment.apiUrl}/settings/get_user_settings`
      )
      .subscribe({
        next: (data) => {
          this.settings = {
            weight: data.weight,
            height: data.height,
            other_data: data.other_data,
            goals: data.goals,
          };
        },
        error: (err) => {
          if (err.status !== 404) {
            console.error('Failed to load settings', err);
          }
        },
      });
  }

  saveSettings() {
    this.successMessage = '';
    this.errorMessage = '';

    this.http
      .post<UserSettingsOut>(
        `${environment.apiUrl}/settings/update_user_settings`,
        this.settings
      )
      .subscribe({
        next: () => {
          // Redirect to the dashboard on successful save
          this.router.navigate(['/dashboard']);
        },
        error: (err) => {
          console.error('Save error', err);
          this.errorMessage = 'Errore nel salvataggio. Riprova.';
        },
      });
  }

  cancelSettings() {
    // Navigate back to dashboard without saving
    this.router.navigate(['/dashboard']);
  }

  getBMI(): string {
    if (this.settings.weight && this.settings.height) {
      const heightInMeters = this.settings.height / 100;
      const bmi = this.settings.weight / (heightInMeters * heightInMeters);
      return bmi.toFixed(1);
    }
    return '0';
  }

  getBMICategory(): string {
    const bmi = parseFloat(this.getBMI());
    if (bmi < 18.5) {
      return 'Sottopeso';
    } else if (bmi < 25) {
      return 'Normopeso';
    } else if (bmi < 30) {
      return 'Sovrappeso';
    } else {
      return 'Obeso';
    }
  }
}
