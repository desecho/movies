# Movies iOS App

A basic iOS app built with SwiftUI that connects to the Django backend for movie management.

## Features

- **Authentication**: JWT-based login system
- **Movie Lists**: View "Watched" and "To Watch" movie lists
- **Search**: Search for movies and add them to lists
- **Movie Management**: Add movies to watched or to-watch lists

## Requirements

- iOS 17.0+
- Xcode 15.0+
- Swift 5.0+

## Setup

1. **Backend Configuration**: Make sure your Django backend is running on `http://localhost:8000`

2. **API Endpoints**: The app expects these Django REST API endpoints:
   - `POST /api/auth/login/` - User authentication
   - `GET /api/auth/user/` - Get current user info
   - `GET /api/records/?action=watched` - Get watched movies
   - `GET /api/records/?action=want_to_watch` - Get to-watch movies
   - `GET /api/movies/search/?q=<query>` - Search movies
   - `POST /api/records/` - Add movie to list

3. **Open Project**: Open `Movies.xcodeproj` in Xcode

4. **Run**: Build and run the project in the iOS Simulator

## Architecture

- **SwiftUI**: Modern declarative UI framework
- **Combine**: Reactive programming for API calls
- **APIService**: Centralized service for backend communication
- **ObservableObject**: State management for authentication and data

## Key Components

- `MoviesApp.swift` - App entry point
- `ContentView.swift` - Main app container with tab navigation
- `LoginView.swift` - Authentication screen
- `MovieListView.swift` - Display watched/to-watch movies
- `SearchView.swift` - Search and add movies
- `APIService.swift` - Backend API integration
- `Models.swift` - Data models matching Django backend

## Configuration

To use with a different backend URL, update the `baseURL` in `APIService.swift`:

```swift
private let baseURL = "https://your-backend-url.com/api"
```

## Notes

- The app uses JWT tokens stored in UserDefaults for authentication
- Movie posters are loaded from TMDB image URLs
- Search includes debouncing to avoid excessive API calls
- Basic error handling with user-friendly messages

This is a basic implementation that can be extended with features like:
- Movie details view
- Rating and comments
- Offline support
- Push notifications
- Social features