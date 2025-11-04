import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

// ─── Interfaces ─────────────────────────────────────────────────────────────
interface TipoPasto {
  tipo: 'colazione' | 'pranzo' | 'cena' | 'spuntino';
  orario?: string;
  ricetta: string;
}

interface Ingrediente {
  nome: string;
  quantita: number;
  unita: string;
}

interface Pasto {
  id: string;
  tipoPasto: TipoPasto;
  ingredienti: Ingrediente[];
  calorie: number;
  day: number;  // 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
}

interface DietaSettimanale {
  nome: string;
  dataInizio: string;  // ISO “YYYY-MM-DD”
  dataFine: string;    // ISO “YYYY-MM-DD”
  pasti: Pasto[];
}

interface ListaSpesa {
  ingredienti: Ingrediente[];
}

interface DietaConLista {
  dieta: DietaSettimanale;
  listaSpesa: ListaSpesa;
}

interface DailyGroup {
  date: string;     // “YYYY-MM-DD”
  dayName: string;  // “lunedì”, “martedì”… (it-IT)
  meals: Pasto[];
}
// ─────────────────────────────────────────────────────────────────────────────

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
})
export class DashboardComponent implements OnInit {
  dietaConLista: DietaConLista | null = null;
  dailyMeals: DailyGroup[] = [];
  error: string | null = null;
  loading = false;       // flag to disable buttons while waiting
  showGroceryList = false;
  currentGroceryList: ListaSpesa | null = null;

  constructor(
    private http: HttpClient,
    private router: Router,
  ) { }

  ngOnInit(): void {
    this.loadCurrentWeekDiet();
  }

  loadCurrentWeekDiet(): void {
    this.error = null;
    this.loading = true;
    const url = `${environment.apiUrl}/diet/current_week`;
    this.http.get<DietaConLista | null>(url)
      .subscribe({
        next: data => {
          // Null response means no diet for this week - this is normal, not an error
          this.dietaConLista = data;
          if (data) {
            this.buildDailyGroups();
          } else {
            this.dailyMeals = [];
          }
          this.loading = false;
        },
        error: err => {
          // Only show error for actual errors (not 404)
          console.error('Error fetching current week diet', err);
          this.error = err.error?.detail || 'Errore nel recupero della dieta';
          this.loading = false;
        }
      });
  }

  generateNewDiet(): void {
    this.error = null;
    this.loading = true;
    const url = `${environment.apiUrl}/diet/create_diet`;
    this.http.post<DietaConLista>(url, {})
      .subscribe({
        next: data => {
          this.dietaConLista = data;
          this.buildDailyGroups();
          this.loading = false;
        },
        error: err => {
          console.error('Error generating new diet', err);
          this.error = err.error?.detail || 'Errore nella generazione della dieta';
          this.loading = false;
        }
      });
  }

  private buildDailyGroups(): void {
    if (!this.dietaConLista) return;

    const { dataInizio, dataFine, pasti } = this.dietaConLista.dieta;
    const start = new Date(dataInizio);
    const end = new Date(dataFine);
    const dates: string[] = [];

    // build array of ISO dates from start→end inclusive
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      dates.push(d.toISOString().slice(0, 10));
    }

    // Meal type order for sorting
    const mealTypeOrder: Record<string, number> = {
      'colazione': 1,
      'spuntino': 2,
      'pranzo': 3,
      'cena': 4
    };

    // Group meals by day (0 = Monday, 1 = Tuesday, etc.)
    this.dailyMeals = dates.map((iso, dayIndex) => {
      const meals = pasti
        .filter(pasto => pasto.day === dayIndex)
        .sort((a, b) => {
          // Sort by meal type order first
          const orderDiff = (mealTypeOrder[a.tipoPasto.tipo] || 99) - (mealTypeOrder[b.tipoPasto.tipo] || 99);
          if (orderDiff !== 0) return orderDiff;

          // Then sort by time if both are same type (e.g., two spuntini)
          const timeA = a.tipoPasto.orario || '';
          const timeB = b.tipoPasto.orario || '';
          return timeA.localeCompare(timeB);
        });

      const dayName = new Date(iso)
        .toLocaleDateString('it-IT', { weekday: 'long' });
      return { date: iso, dayName, meals };
    });
  }

  navigateToRecipe(mealId: string): void {
    this.router.navigate(['/recipe', mealId]);
  }

  openGroceryList(): void {
    if (this.dietaConLista?.listaSpesa) {
      this.currentGroceryList = this.dietaConLista.listaSpesa;
      this.showGroceryList = true;
    }
  }

  closeGroceryList(): void {
    this.showGroceryList = false;
  }

  trackByNome(_index: number, ingrediente: Ingrediente): string {
    return ingrediente.nome;
  }
}
