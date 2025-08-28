# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-platform movie management system with Django backend, Vue.js web frontend, and native iOS app. Users can create "Watched" and "To Watch" lists, rate movies, add comments, and get AI-powered recommendations. The application integrates with TMDB and OMDb APIs for movie data.

**Tech Stack:**
- **Backend**: Django 5.2.4, Django REST Framework, MySQL, Redis, Celery, OpenAI API
- **Web Frontend**: Vue.js 3, Vuetify 3, TypeScript, Vite
- **iOS App**: Swift, SwiftUI, Combine (iOS 17.0+)
- **Authentication**: JWT with django-rest-registration (shared across platforms)
- **APIs**: TMDB (The Movie Database), OMDb, OpenAI
- **Deployment**: Docker, Kubernetes

## Development Commands

### Project Setup
```bash
make bootstrap         # Complete project setup (install deps, create DB, migrate, fixtures, build)
make create-venvs      # Create Python virtual environments (poetry + tox)
make create-db         # Create local database
make load-initial-fixtures  # Load required data (lists, actions, providers)
make create-env-files  # Create environment configuration files from templates
```

### Development Server
```bash
make run               # Run Django development server (alias for runserver)
make runserver         # Run Django development server on 0.0.0.0:8000
make dev               # Run Vite frontend development server
make celery            # Run Celery worker for background tasks
```

### Building and Dependencies
```bash
make build             # Build frontend assets with Vite
make yarn-install      # Install frontend dependencies
make poetry-update     # Update Python packages
make yarn-upgrade      # Interactive upgrade of frontend packages
```

### Database Operations
```bash
make migrate           # Run Django migrations
make makemigrations    # Create new migrations
make manage [command]  # Run any Django management command
make shell             # Django shell
make createsuperuser   # Create Django admin superuser
make drop-db           # Drop local database
make load-db           # Load database from backup
```

### Testing and Linting
```bash
make test              # Run all tests and linting (comprehensive)
make test2             # Run frontend tests and linting only
make tox               # Run all Python tests via tox
make pytest            # Run pytest specifically
make eslint            # Run ESLint on frontend
make fl                # Format and lint all code (shortcut for development)
```

### Code Formatting
```bash
make format            # Format Python code (autoflake, isort, black)
make format-frontend   # Format frontend code (prettier, eslint --fix)
make format-all        # Format all code (Python, frontend, configs)
make f                 # Format Python code (alias)
make ff                # Format frontend (alias)
make fa                # Format all (alias)
```

### Python Linting (Individual Tools)
```bash
make pylint            # Python linting
make mypy              # Type checking
make flake8            # Python style checking
make black             # Python code formatting
make isort             # Python import sorting
make bandit            # Security linting
make safety            # Security vulnerability checking
```

### Docker Commands
```bash
make docker-build-dev  # Build development Docker images
make docker-run        # Run application in Docker
make docker-sh         # Access Docker container shell
```

### Production Commands
```bash
make prod-manage [command]     # Run Django command in production
make prod-shell               # Production Django shell
make prod-migrate             # Production database migration
make prod-create-db           # Create production database
make prod-load-db             # Load production database from backup
```

## Architecture

### Backend Structure
- **Django Project**: `src/movies/` - Main Django configuration, settings, URLs, WSGI
- **Django App**: `src/moviesapp/` - Core application logic

**Core Components:**
- **Models**: `models.py` - User, Movie, Record, List, Action, Provider, Follow
- **Views**: `views/` - Modular API endpoints (search, trending, recommendations, etc.)
- **Serializers**: `serializers.py` - REST API data serialization
- **Middleware**: `middleware.py` - Custom request/response processing
- **Admin**: `admin.py` - Django admin interface customizations
- **Tasks**: `tasks.py` - Celery background tasks for async operations

**API Endpoints** (`src/moviesapp/views/`):
- `search.py` - Movie search functionality
- `trending.py` - Trending movies
- `recommendations.py` - AI-powered movie recommendations
- `list.py` - Movie list management
- `user.py` - User profile and authentication
- `feed.py` - Activity feed
- `follow.py` - User following system
- `stats.py` - Statistics and analytics
- `health.py` - System health checks

**External Integrations**:
- `tmdb/` - TMDB API client with types and error handling
- `omdb/` - OMDb API client with types and error handling
- `openai/` - OpenAI API client for AI recommendations

**Management Commands** (`management/commands/`):
- `update_movie_data.py` - Sync movie data from external APIs
- `update_imdb_ratings.py` - Update movie ratings
- `load_providers.py` - Load streaming provider data
- `remove_unused_movies.py` - Database cleanup

**Testing**: `tests/` - Comprehensive test suite with fixtures and mocks
**Fixtures**: `fixtures/` - Initial data for development and testing

### Frontend Structure
- **Framework**: Vue.js 3 with Composition API and TypeScript
- **UI Library**: Vuetify 3 (Material Design components)
- **Build Tool**: Vite with hot module replacement
- **Package Manager**: Yarn with workspace support
- **State Management**: Pinia with persistence plugin
- **HTTP Client**: Axios with progress bar and interceptors

**Views** (`frontend/src/views/`):
- `LoginView.vue` / `RegistrationView.vue` - Authentication
- `ListView.vue` - Movie lists (Watched/To Watch)
- `SearchView.vue` - Movie search interface
- `TrendingView.vue` - Trending movies
- `RecommendationsView.vue` - AI recommendations
- `MovieDetailView.vue` - Individual movie details
- `FeedView.vue` - Activity feed
- `UserPreferencesView.vue` - User settings
- `StatsView.vue` - User statistics
- `UsersView.vue` - User directory
- `FollowersView.vue` / `FollowingView.vue` - Social features
- `NetworkView.vue` - Social network visualization
- `AboutView.vue` - Application information

**Components** (`frontend/src/components/`):
- `MoviesList.vue` - Reusable movie grid/list
- `UserAvatarComponent.vue` - User profile pictures
- `ThemeToggle.vue` - Dark/light mode switching
- `YearSelectorComponent.vue` - Year filtering
- `LoadingIndicator.vue` - Loading states

**Composables** (`frontend/src/composables/`):
- `useRecordsData.ts` - Movie records management
- `useMovieOperations.ts` - Movie CRUD operations
- `useListViewService.ts` - List view functionality
- `useSEO.ts` - Search engine optimization
- `useAsyncOperation.ts` - Async operation handling
- `formValidation.ts` - Form validation utilities

**Stores** (`frontend/src/stores/`):
- `auth.ts` - Authentication state
- `records.ts` - Movie records state
- `theme.ts` - UI theme state
- `listView.ts` - List view preferences
- `feed.ts` - Activity feed state

### Key Directories
- `src/moviesapp/views/` - API endpoints (including AI recommendations)
- `src/moviesapp/openai/` - OpenAI integration for movie recommendations
- `src/moviesapp/management/commands/` - Custom Django commands
- `frontend/src/views/` - Vue page components (including RecommendationsView)
- `frontend/src/components/` - Reusable Vue components
- `ios/MoviesApp/` - iOS app source code
- `deployment/` - Kubernetes manifests

## Database Models

**Core Models:**
- `User` - Extended Django user with profile fields
- `Movie` - Movie data from TMDB/OMDb
- `Record` - User's interaction with a movie (watched/to watch)
- `List` - Movie lists (Watched, To Watch)
- `Action` - Types of actions users can take
- `Provider` - Streaming service providers

## AI Recommendations System

**Overview:**
The application features AI-powered movie recommendations using OpenAI's API. Users can get personalized suggestions based on their viewing history and preferences.

**Components:**
- **Backend**: `src/moviesapp/openai/` - OpenAI client, types, and exceptions
- **API Endpoint**: `/recommendations/` - RESTful endpoint for getting recommendations
- **Web Frontend**: `frontend/src/views/RecommendationsView.vue` - Vue component with preference controls
- **iOS App**: `RecommendationsView.swift` - Native SwiftUI interface

**Parameters:**
- Genre preferences (Action, Comedy, Drama, etc.)
- Year range filtering
- Minimum rating threshold
- Number of desired recommendations
- User's watch history (liked, disliked, unrated movies)

**Process:**
1. System analyzes user's watched movies and ratings
2. Builds personalized prompt for OpenAI
3. Returns IMDB IDs which are converted to TMDB movie data
4. Filters out movies already in user's lists
5. Presents recommendations with "Add to List" functionality

## Development Tools & Configuration

### Python Environment
- **Package Manager**: Poetry (pyproject.toml)
- **Python Version**: 3.11
- **Virtual Environment**: Poetry + Tox for testing
- **Dependencies**: Django 5.2.4, DRF, Celery, Redis, OpenAI, Pillow

### Frontend Environment
- **Package Manager**: Yarn (package.json)
- **Build Tool**: Vite with TypeScript support
- **Vue Version**: 3.5+ with Composition API
- **UI Framework**: Vuetify 3.8+ with Material Design

### Environment Configuration
- `env.sh` - Base environment variables
- `env_custom.sh` - Custom local overrides  
- `env_secrets.sh` - Secret keys and tokens
- `docker.env` / `docker_secrets.env` - Docker environment

### Testing Infrastructure

**Python Testing**:
- **Test Runner**: pytest with django-test-without-migrations
- **Coverage**: pytest-cov with HTML reports
- **Test Environment**: Tox for isolated testing
- **Mock Framework**: pytest-mock, requests-mock
- **Test Structure**: 
  - Unit tests for models, views, utilities
  - Integration tests for API endpoints
  - External API mocking (TMDB, OMDb, OpenAI)

**Code Quality Tools**:
- **Linting**: pylint, flake8, bandit (security), mypy (types)
- **Formatting**: black, isort, autoflake
- **Frontend**: ESLint, Prettier, TypeScript compiler
- **Documentation**: pydocstyle, restructuredtext-lint

**Testing Commands**:
```bash
make test              # All tests + linting
make tox               # Python tests in isolated environments  
make pytest            # Quick Python tests
make eslint            # Frontend linting
```

### Docker & Deployment
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: docker-compose for local development
- **Production**: Kubernetes manifests in `deployment/`
- **Web Server**: Gunicorn + Nginx for static files
- **Database**: MySQL with connection pooling

## Common Workflows

1. **Adding a new feature**: Update Django backend, Vue.js frontend, and iOS app as needed
2. **Database changes**: Create migrations with `make makemigrations`, then `make migrate`
3. **API changes**: Update Django serializers, Vue.js TypeScript types, and iOS Swift models
4. **External API updates**: Modify TMDB/OMDb clients in respective modules (backend, frontend, iOS)
5. **iOS development**: Update Swift models to match backend changes, test in iOS Simulator

## iOS App (MovieMunch)

The iOS app is a native SwiftUI application that provides a mobile interface for the movie management system.

### **App Information**
- **Display Name**: MovieMunch
- **Bundle Identifier**: moviemunch
- **Minimum iOS Version**: 17.0+
- **Architecture**: Native SwiftUI with Combine
- **Location**: `ios/MoviesApp/`

### **Development Commands**
```bash
# Build the iOS app
xcodebuild -project MoviesApp.xcodeproj -scheme MovieMunchApp -configuration Debug -destination "platform=iOS Simulator,name=iPhone 16" build

# List available schemes and targets
xcodebuild -project MoviesApp.xcodeproj -list

# Clean build
xcodebuild -project MoviesApp.xcodeproj -scheme MovieMunchApp clean
```

### **iOS App Architecture**

**Core Files:**
- `MoviesAppApp.swift` - App entry point and configuration
- `ContentView.swift` - Main tab navigation container
- `APIService.swift` - Backend API integration with authentication
- `Models.swift` - Data models matching Django backend

**Views:**
- `LoginView.swift` - JWT authentication interface
- `MovieListView.swift` - Watched/To Watch lists with infinite scroll
- `SearchView.swift` - Movie search with TMDB integration
- `TrendingView.swift` - Trending movies from backend
- `RecommendationsView.swift` - AI-powered movie recommendations
- `MovieDetailView.swift` - Individual movie details
- `GalleryView.swift` - Movie gallery/grid view

**Models & Configuration:**
- `RecommendationPreferences.swift` - AI recommendation settings and types

### **Features**

**Core Features:**
- JWT-based authentication with token management
- Watched and To Watch movie list management
- Movie search powered by TMDB API
- Add movies directly to lists from search/trending
- Optimized caching for improved performance
- Pull-to-refresh and infinite scroll

**Advanced Features:**
- **AI Recommendations**: Personalized movie suggestions using OpenAI
- **Trending Movies**: Curated trending content from backend
- **Movie Details**: Comprehensive movie information with posters
- **Smart Caching**: Efficient data loading and offline capabilities

### **Backend Integration**

**API Endpoints Used:**
- `POST /token/` - JWT authentication
- `GET /user/avatar/` - User profile information
- `GET /records/` - Movie lists (optimized single call)
- `GET /search/` - Movie search with TMDB data
- `GET /trending/` - Trending movies
- `GET /recommendations/` - AI-powered movie recommendations
- `POST /add-to-list/` - Add movies to lists
- `DELETE /remove-record/` - Remove movies from lists
- `PUT /change-rating/` - Update movie ratings

**Configuration:**
- Debug builds connect to `http://127.0.0.1:8000`
- Production builds connect to `https://api.moviemunch.org`
- Dynamic base URL based on build configuration

### **Technical Details**

**State Management:**
- `@StateObject` and `@ObservableObject` for reactive UI updates
- Combine publishers for asynchronous API operations
- Centralized `APIService` with error handling

**Performance:**
- Records caching system (5-minute validity)
- Optimized single API call for both Watched/To Watch lists
- Background refresh with cache invalidation
- Efficient image loading for movie posters

**Error Handling:**
- Comprehensive API error types
- Automatic token refresh on authentication failure
- User-friendly error messages and retry mechanisms

### **Development Notes**

1. **Adding New Views**: Follow the existing pattern with `@EnvironmentObject` for `APIService`
2. **API Changes**: Update both `APIService.swift` and corresponding models
3. **New Features**: Consider both authenticated and unauthenticated states
4. **Testing**: Build in iOS Simulator for development testing

## Scripts & Utilities

The project includes comprehensive scripts in the `scripts/` directory:

### Database Scripts
```bash
scripts/create_db.sh          # Create database
scripts/drop_db.sh            # Drop database  
scripts/connect_db.sh         # Connect to database shell
scripts/backup_db.sh          # Backup database to S3
scripts/load_db.sh            # Load database from backup
```

### Production Scripts
```bash
scripts/run_management_command_prod.sh        # Run Django commands in production
scripts/run_management_command_interactive_prod.sh  # Interactive production commands
scripts/run_shell_prod.sh                     # Production Django shell
```

### Utility Scripts  
```bash
scripts/flush_cdn_cache.sh    # Clear CDN cache
scripts/pydiatra.sh          # Advanced Python linting
scripts/djhtml.sh            # Django HTML template formatting
```

### Makefile Utilities
The project uses a sophisticated Makefile system with modular includes:

- `makefiles/colors.mk` - Terminal color definitions
- `makefiles/help.mk` - Auto-generated help system  
- `makefiles/macros.mk` - Reusable command macros

**Key Makefile Features**:
- Auto-discovery of environment files
- Parallel test execution
- Production deployment automation
- Multi-stage Docker builds
- Comprehensive code formatting pipeline

## Project Features

### Core Features
- **Movie Management**: Watched/To Watch lists with ratings and comments
- **Search**: TMDB-powered movie search with advanced filtering
- **AI Recommendations**: OpenAI-powered personalized suggestions
- **Social Features**: Follow users, activity feeds, user statistics
- **Multi-Platform**: Web (Vue.js), Mobile (iOS), API-first architecture

### Advanced Features  
- **Performance**: Caching, lazy loading, pagination (50 items/page)
- **SEO**: Comprehensive meta tag management, JSON-LD structured data for movies/lists/users
- **Analytics**: User behavior tracking, performance monitoring
- **Security**: JWT authentication, CORS headers, Django security middleware
- **Localization**: Django LocaleMiddleware with basic multi-language infrastructure

## Additional instructions

- Run pytest individually like this if you have to: `.tox/py-pytest/bin/python -m pytest`
- To run pytest - run `make pytest`
- After you done coding, in the testing phase - always run command `make fl`. It will format the code and also lint it.
