# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django 5.2.4 and Vue.js 3 web application for movie management. Users can create "Watched" and "To Watch" lists, rate movies, and add comments. The application integrates with TMDB and OMDb APIs for movie data.

**Tech Stack:**
- Backend: Django 5.2.4, Django REST Framework, MySQL, Redis, Celery
- Frontend: Vue.js 3, Vuetify 3, TypeScript, Vite
- Authentication: JWT with django-rest-registration
- APIs: TMDB (The Movie Database), OMDb
- Deployment: Docker, Kubernetes

## Development Commands

### Initial Setup
```bash
make bootstrap          # Full project setup (dependencies, DB, migrations, build)
make createsuperuser   # Create Django admin user
```

### Development Servers
```bash
make run               # Start Django development server (localhost:8000)
make dev               # Start frontend development server (Vite)
make celery            # Start Celery worker for background tasks
```

### Building and Dependencies
```bash
make build             # Build frontend assets with Vite
make yarn-install      # Install frontend dependencies
make poetry-update     # Update Python dependencies
```

### Database Operations
```bash
make migrate           # Run Django migrations
make create-db         # Create database
make drop-db           # Drop database
make load-db           # Load database from backup
```

### Testing and Linting
```bash
make test              # Run all tests (Python + frontend linting)
make tox               # Run Python tests via tox
make pytest            # Run pytest specifically
make eslint            # Run ESLint on frontend
```

### Code Formatting
```bash
make format            # Format Python code (autoflake, isort, black)
make format-frontend   # Format frontend code (prettier, eslint --fix)
make format-all        # Format all code (backend + frontend + misc)
```

### Python Linting (Individual Tools)
```bash
make pylint            # Python linting
make flake8            # Style checking
make mypy              # Type checking
make bandit            # Security analysis
make black             # Code formatting check
make isort             # Import sorting check
```

### Management Commands
```bash
make manage [command] arguments="[args]"  # Run Django management commands
make shell                                # Django shell
make makemigrations arguments="[args]"    # Create migrations
```

## Architecture

### Backend Structure
- **Django Project**: `src/movies/` - Main Django configuration
- **Django App**: `src/moviesapp/` - Core application logic
- **Models**: User, Movie, Record (watch status), List, Action, Provider
- **APIs**: REST API using Django REST Framework with JWT authentication
- **External Integrations**: 
  - `src/moviesapp/tmdb/` - TMDB API client
  - `src/moviesapp/omdb/` - OMDb API client
- **Background Tasks**: Celery tasks in `src/moviesapp/tasks.py`

### Frontend Structure
- **Framework**: Vue.js 3 with Composition API
- **UI**: Vuetify 3 (Material Design components)
- **State Management**: Pinia stores in `frontend/src/stores/`
- **Routing**: Vue Router in `frontend/src/router.ts`
- **Build Tool**: Vite
- **HTTP Client**: Axios with interceptors

### Key Directories
- `src/moviesapp/views/` - API endpoints
- `src/moviesapp/management/commands/` - Custom Django commands
- `frontend/src/views/` - Vue page components
- `frontend/src/components/` - Reusable Vue components
- `deployment/` - Kubernetes manifests

## Environment Configuration

The project uses multiple environment files:
- `env.sh` - Base environment variables
- `env_custom.sh` - Local customizations (created from template)
- `env_secrets.sh` - Secret keys and tokens (created from template)
- `docker_secrets.env` - Docker secrets (created from template)

Always source environment files before running commands:
```bash
source env.sh && source env_custom.sh && source env_secrets.sh
```

## Database Models

**Core Models:**
- `User` - Extended Django user with profile fields
- `Movie` - Movie data from TMDB/OMDb
- `Record` - User's interaction with a movie (watched/to watch)
- `List` - Movie lists (Watched, To Watch)
- `Action` - Types of actions users can take
- `Provider` - Streaming service providers

## Testing

- **Python Tests**: Located in `src/moviesapp/tests/` using pytest
- **Test Database**: Uses `django-test-without-migrations` for speed
- **Frontend**: ESLint for code quality, Prettier for formatting
- **Type Checking**: MyPy for Python, TypeScript for frontend

## Deployment

- **Development**: `make run` + `make dev` + `make celery`
- **Docker**: `make docker-build-dev` and `make docker-run`
- **Production**: Kubernetes deployment with separate backend/frontend containers

## Common Workflows

1. **Adding a new feature**: Update both Django views/models and Vue components
2. **Database changes**: Create migrations with `make makemigrations`, then `make migrate`
3. **API changes**: Update both backend serializers and frontend TypeScript types
4. **External API updates**: Modify TMDB/OMDb clients in respective modules

## Development Memories

- Always run tests with `make pytest` command