// src/app/components/weekly/recipe-details.component.ts

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
  tipoPasto: TipoPasto;
  ingredienti: Ingrediente[];
  calorie: number;
}

interface HtmlStructure {
  h1: string;
  h2: string[];
  p: string[];
  ul: string[];
  ol: string[];
}

interface RecipeResponse {
  recipe: HtmlStructure;
}

@Component({
  selector: 'app-recipe-details',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './recipe-details.component.html',
  styleUrls: ['./recipe-details.component.css']
})
export class RecipeDetailsComponent implements OnInit {
  meal?: Pasto;
  generatedRecipe?: HtmlStructure;    // the LLM-generated full recipe structure
  error = '';
  loading = true;
  generating = false;      // loading flag for recipe generation
  mealId = '';

  constructor(
    private http: HttpClient,
    private route: ActivatedRoute,
    private router: Router,
  ) { }

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('meal_id');
      if (!id) {
        this.error = 'No meal ID provided';
        this.loading = false;
        return;
      }
      this.mealId = id;
      this.fetchMeal(id);
    });
  }

  private fetchMeal(id: string) {
    this.loading = true;
    this.error = '';
    this.http
      .get<Pasto>(`${environment.apiUrl}/meals/${id}`)
      .subscribe({
        next: pasto => {
          this.meal = pasto;
          this.loading = false;
        },
        error: err => {
          console.error('Failed to load meal', err);
          this.error = err.status === 404
            ? 'Meal not found.'
            : 'Failed to load meal. Please try again.';
          this.loading = false;
        }
      });
  }

  generateRecipe() {
    if (!this.mealId) return;
    this.generating = true;
    this.http
      .get<RecipeResponse>(`${environment.apiUrl}/meals/${this.mealId}/recipe`)
      .subscribe({
        next: res => {
          this.generatedRecipe = res.recipe;
          this.generating = false;
        },
        error: err => {
          console.error('Failed to generate recipe', err);
          this.error = 'Could not generate recipe. Please try again.';
          this.generating = false;
        }
      });
  }

  goBack() {
    this.router.navigate(['../'], { relativeTo: this.route });
  }

  copyRecipe() {
    if (this.generatedRecipe) {
      // Convert structured recipe to plain text
      const recipeText = this.formatRecipeAsText(this.generatedRecipe);
      navigator.clipboard.writeText(recipeText).then(() => {
        // You could add a toast notification here
        console.log('Recipe copied to clipboard');
      }).catch(err => {
        console.error('Failed to copy recipe: ', err);
      });
    }
  }

  private formatRecipeAsText(recipe: HtmlStructure): string {
    let text = `${recipe.h1}\n\n`;

    // Add preparation and cooking times
    if (recipe.p && recipe.p.length > 0) {
      text += recipe.p.join('\n') + '\n\n';
    }

    // Add ingredients section
    if (recipe.h2 && recipe.h2.length > 0) {
      text += `${recipe.h2[0]}\n`;
      recipe.ul.forEach(item => {
        text += `• ${item}\n`;
      });
      text += '\n';
    }

    // Add instructions section
    if (recipe.h2 && recipe.h2.length > 1) {
      text += `${recipe.h2[1]}\n`;
      recipe.ol.forEach((step, index) => {
        text += `${index + 1}. ${step}\n`;
      });
    }

    return text;
  }
}
