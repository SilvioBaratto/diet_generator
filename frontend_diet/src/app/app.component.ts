import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './shared/sidebar/sidebar.component';

@Component({
  selector: 'app-root',
  imports: [
    CommonModule,
    RouterOutlet,
    SidebarComponent
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  host: {
    '(window:resize)': 'onResize()'
  }
})
export class AppComponent {
  sidebarOpen = false;

  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  }

  onSidebarLinkClick() {
    // if on mobile (below Tailwind's lg breakpoint of 1024px), close it
    if (window.innerWidth < 1024) {
      this.sidebarOpen = false;
    }
  }

  // Close sidebar on mobile when window is resized to desktop
  onResize() {
    if (window.innerWidth >= 1024) {
      // ensure sidebar closes on desktop since it's always visible
      this.sidebarOpen = false;
    }
  }
}