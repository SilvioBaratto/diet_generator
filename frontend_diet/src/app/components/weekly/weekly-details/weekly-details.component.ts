// src/app/weekly-details/weekly-details.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { environment } from '../../../../environments/environment';

interface Ingrediente {
  nome: string;
  quantita: number;
  unita: string;
}

interface TipoPasto {
  tipo: 'colazione' | 'pranzo' | 'cena' | 'spuntino';
  orario?: string;
  ricetta: string;
}

interface Pasto {
  id: string;
  tipoPasto: TipoPasto;
  ingredienti: Ingrediente[];
  calorie: number;
}

interface Dieta {
  nome?: string;
  dataInizio: string;
  dataFine: string;
  pasti: Pasto[];
}

@Component({
  selector: 'app-weekly-details',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './weekly-details.component.html',
  styleUrls: ['./weekly-details.component.css']
})
export class WeeklyDetailsComponent implements OnInit {
  diet?: Dieta;
  error = '';
  loading = true;

  constructor(
    private http: HttpClient,
    private route: ActivatedRoute,
    private router: Router,
  ) { }

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const dietId = params.get('diet_id');
      if (!dietId) {
        this.error = 'No diet ID provided';
        this.loading = false;
        return;
      }
      this.fetchDiet(dietId);
    });
  }

  private fetchDiet(id: string) {
    this.loading = true;
    this.http
      .get<Dieta>(`${environment.apiUrl}/diet/${id}`)
      .subscribe({
        next: diet => {
          this.diet = diet;
          this.loading = false;
        },
        error: err => {
          console.error('Could not load diet', err);
          this.error = err.status === 404
            ? 'Diet not found.'
            : 'Failed to load diet. Please try again.';
          this.loading = false;
        }
      });
  }

  viewRecipe(mealId: string) {
    this.router.navigate(['/recipe', mealId]);
  }

  getTotalCalories(): number {
    return this.diet?.pasti.reduce((total, pasto) => total + pasto.calorie, 0) || 0;
  }

  getUniqueDays(): number {
    // This is a simplified calculation - in a real app you might want to track actual days
    // For now, assuming roughly 3-4 meals per day
    return Math.ceil((this.diet?.pasti.length || 0) / 3.5);
  }

  getUniqueIngredients(): number {
    if (!this.diet) return 0;
    
    const uniqueIngredients = new Set();
    this.diet.pasti.forEach(pasto => {
      pasto.ingredienti.forEach(ing => {
        uniqueIngredients.add(ing.nome.toLowerCase());
      });
    });
    
    return uniqueIngredients.size;
  }
}
