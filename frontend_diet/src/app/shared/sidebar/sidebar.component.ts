import { Component, Output, EventEmitter } from '@angular/core';
import { RouterModule } from '@angular/router';


interface NavLink {
  label: string
  path: string
  icon?: string
  description?: string
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css'],
})
export class SidebarComponent {
  @Output() closeSidebar = new EventEmitter<void>();
  
  navLinks: NavLink[] = [
    { 
      path: '/dashboard', 
      label: 'Dashboard',
      description: 'Panoramica generale'
    },
    { 
      path: '/weekly', 
      label: 'Piani Settimanali',
      description: 'Gestisci le tue diete'
    },
    // { 
    //   path: '/grocery', 
    //   label: 'Lista Spesa',
    //   description: 'Organizza gli acquisti'
    // },
    { 
      path: '/settings', 
      label: 'Impostazioni',
      description: 'Configura il profilo'
    },
  ]

  onLinkClick() {
    this.closeSidebar.emit();
  }

  // TrackBy function for optimal performance with *ngFor
  trackByPath(_index: number, item: NavLink): string {
    return item.path;
  }

  // Determine if exact matching should be used for a route
  isExactRoute(path: string): boolean {
    // Weekly should use non-exact matching to highlight for /weekly/:id
    // Dashboard and Settings use exact matching
    return path !== '/weekly';
  }
}