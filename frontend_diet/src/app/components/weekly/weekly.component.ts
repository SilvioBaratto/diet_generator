// src/app/weekly/weekly.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';
import { environment } from '../../../environments/environment';

interface DietSummary {
  id: string;
  name?: string;
  created_at: string;
}

interface Ingrediente {
  nome: string;
  quantita: number;
  unita: string;
}

interface GroceryList {
  ingredienti: Ingrediente[];
}

@Component({
  selector: 'app-weekly',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './weekly.component.html',
  styleUrls: ['./weekly.component.css']
})
export class WeeklyComponent implements OnInit {
  diets: DietSummary[] = [];
  error = '';
  loading = true;
  showGroceryList = false;
  currentGroceryList: GroceryList | null = null;
  groceryListLoading = false;

  constructor(
    private http: HttpClient,
    public router: Router,
  ) { }

  ngOnInit() {
    this.loading = true;
    this.http
      .get<DietSummary[]>(`${environment.apiUrl}/diet/list`)
      .subscribe({
        next: (data) => {
          this.diets = data;
          this.loading = false;
        },
        error: (err) => {
          console.error('Failed to load diets', err);
          this.error = 'Could not load your diets. Please try again later.';
          this.loading = false;
        }
      });
  }

  viewDiet(dietId: string) {
    this.router.navigate(['/weekly', dietId]);
  }

  viewGroceryList(dietId: string) {
    this.groceryListLoading = true;
    this.http
      .get<GroceryList>(`${environment.apiUrl}/diet/${dietId}/grocery-list`)
      .subscribe({
        next: (data) => {
          this.currentGroceryList = data;
          this.showGroceryList = true;
          this.groceryListLoading = false;
        },
        error: (err) => {
          console.error('Failed to load grocery list', err);
          this.error = 'Could not load the grocery list. Please try again later.';
          this.groceryListLoading = false;
        }
      });
  }

  closeGroceryList() {
    this.showGroceryList = false;
    this.currentGroceryList = null;
  }

  trackByNome(_index: number, ingrediente: Ingrediente): string {
    return ingrediente.nome;
  }
}
