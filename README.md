# DietologoAI - AI-Powered Diet Generator

> **Smart weekly meal planning powered by OpenAI.** Generate personalized diet plans, get detailed recipes, and automatic shopping lists - all with a beautiful, responsive interface.

<div align="center">
  <img src="video.gif" alt="DietologoAI Demo" width="100%">
</div>

---

## What is DietologoAI?

DietologoAI is a full-stack web application that uses AI to create personalized weekly meal plans based on your nutritional needs. Simply input your daily calorie target, and the AI generates a complete 7-day diet plan with:

- 5 balanced meals per day (breakfast, snacks, lunch, dinner)
- Detailed nutritional information (calories, proteins, carbs, fats)
- Complete recipes with step-by-step instructions
- Automatic shopping list generation with quantities
- Beautiful, mobile-responsive interface

Perfect for nutritionists, fitness enthusiasts, or anyone looking to plan their meals efficiently.

---

## 🚀 Try It Online

**Don't want to self-host? Try the live version!**

Visit **[diet.silviobaratto.com](https://diet.silviobaratto.com)** and start using DietologoAI immediately:

- ✅ **1 Week Free Trial** - Full access to all features
- 🔐 **Login with Google** - Quick and secure authentication
- 💰 **Only €0.99/month after trial** - Affordable meal planning

**After your free trial, continue using the service for just €0.99/month via PayPal:**
👉 [Subscribe via PayPal](https://www.paypal.me/silviobaratto)

*Prefer to self-host? Follow the installation instructions below to run DietologoAI on your own infrastructure.*

---

## Features

- **AI-Powered Generation**: Uses OpenAI GPT to create personalized meal plans
- **Complete Meal Plans**: 7 days × 5 meals = 35 perfectly balanced meals
- **Detailed Recipes**: Click any meal to get a full recipe with ingredients and instructions
- **Smart Shopping Lists**: Automatically generates grocery lists with proper quantities
- **Nutritional Tracking**: View calories and macros for every meal and day
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Modern UI**: Built with Angular 19 and Tailwind CSS

---

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Reliable SQL database
- **SQLAlchemy** - ORM for database operations
- **BAML** - Type-safe LLM integration
- **Pydantic** - Data validation

### Frontend
- **Angular 19** - Modern web framework
- **Tailwind CSS** - Utility-first CSS framework
- **TypeScript** - Type-safe JavaScript

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Reverse proxy for frontend
- **Alembic** - Database migrations

---

## Requirements

Before you begin, make sure you have:

1. **Docker Desktop** installed ([Download here](https://www.docker.com/products/docker-desktop/))
   - Windows: Docker Desktop for Windows
   - macOS: Docker Desktop for Mac
   - Linux: Docker Engine + Docker Compose

2. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
   - You'll need this to power the AI diet generation

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/diet_generator.git
cd diet_generator
```

### Step 2: Set Up Your OpenAI API Key

Create a `.env` file in the project root:

```bash
echo "MY_OPENAI_KEY=your_openai_api_key_here" > .env
```

Or set it as an environment variable:

```bash
export MY_OPENAI_KEY=your_openai_api_key_here
```

### Step 3: Start the Application

```bash
docker compose up --build
```

This command will:
- Build all Docker containers (frontend, backend, database)
- Start all services
- Initialize the database with migrations

**First-time setup takes 2-5 minutes** as Docker downloads images and builds containers.

### Step 4: Access the Application

Once you see "Application startup complete", open your browser:

| Service | URL | Description |
|---------|-----|-------------|
| **Web App** | http://localhost:4200 | Main application |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Backend** | http://localhost:8000 | REST API |

---

## Usage

### Creating Your First Diet Plan

1. **Open the app** at http://localhost:4200
2. **Click "Rigenera"** (Regenerate) button in the dashboard
3. **Enter your daily calorie target** (e.g., 2000)
4. **Wait 30-60 seconds** while AI generates your personalized plan
5. **View your weekly plan** with all meals and nutritional info

### Viewing Recipes

1. Click on any meal card in your weekly plan
2. View detailed recipe with:
   - Ingredients list
   - Preparation time
   - Cooking time
   - Step-by-step instructions
   - Serving suggestions

### Shopping List

1. Click **"Lista Spesa"** (Shopping List) button
2. View all ingredients needed for the week
3. Organized by category with proper quantities

---

## Project Structure

```
diet_generator/
├── api_diet/              # Backend (FastAPI)
│   ├── app/
│   │   ├── main.py        # FastAPI application entry point
│   │   ├── models/        # SQLAlchemy database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── routers/       # API endpoints
│   ├── baml_src/          # BAML AI prompts
│   └── Dockerfile
│
├── frontend_diet/         # Frontend (Angular 19)
│   ├── src/app/
│   │   ├── components/    # UI components
│   │   ├── services/      # API services
│   │   └── shared/        # Shared utilities
│   ├── nginx.conf         # Nginx configuration
│   └── Dockerfile
│
├── docker-compose.yml     # Docker orchestration
└── .env                   # Environment variables (you create this)
```

---

## Stopping the Application

To stop all services:

```bash
docker compose down
```

To stop and remove all data (including database):

```bash
docker compose down -v
```

---

## Common Issues

### Port Already in Use

If port 4200 or 8000 is already in use, edit `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "4201:80"  # Changed from 4200
  api:
    ports:
      - "8001:8000"  # Changed from 8000
```

### OpenAI API Errors

If you see "API key not found" errors:
1. Check your `.env` file exists in the project root
2. Verify the API key is correct
3. Restart containers: `docker compose restart`

### 504 Gateway Timeout

Diet generation can take 30-60 seconds. This is normal. If it times out:
1. Check your internet connection
2. Verify your OpenAI API key has credits
3. Check API logs: `docker compose logs api`

### Clean Start

If things aren't working, try a clean restart:

```bash
# Stop everything and remove volumes
docker compose down -v

# Rebuild and start fresh
docker compose up --build
```

---

## Development

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f frontend
```

### Database Operations

```bash
# Run migrations
docker compose exec api alembic upgrade head

# Create new migration
docker compose exec api alembic revision --autogenerate -m "description"

# Access database directly
docker compose exec db psql -U postgres -d diet_db
```

### Hot Reload

- **Backend**: Code changes automatically reload (FastAPI `--reload`)
- **Frontend**: Requires rebuild: `docker compose up -d --build frontend`

---

## API Documentation

Once the application is running, you can explore the API:

- **Swagger UI**: http://localhost:8000/docs (interactive docs)
- **ReDoc**: http://localhost:8000/redoc (alternative docs)

Key endpoints:
- `POST /api/v1/diet/create_diet` - Generate new diet plan
- `GET /api/v1/diet/` - Get all user's diets
- `GET /api/v1/diet/{diet_id}` - Get specific diet with meals
- `GET /api/v1/meals/{meal_id}/recipe` - Generate recipe for a meal
- `POST /api/v1/diet/{diet_id}/shopping_list` - Generate shopping list

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## Support

If you encounter any issues or have questions:

1. Check the [Common Issues](#common-issues) section
2. Review [API Documentation](#api-documentation)
3. Open an issue on GitHub

---

<div align="center">
  <p>Made with ❤️ using OpenAI, FastAPI, and Angular</p>
  <p>
    <a href="https://fastapi.tiangolo.com/">FastAPI</a> •
    <a href="https://angular.io/">Angular</a> •
    <a href="https://www.docker.com/">Docker</a> •
    <a href="https://tailwindcss.com/">Tailwind CSS</a>
  </p>
</div>
