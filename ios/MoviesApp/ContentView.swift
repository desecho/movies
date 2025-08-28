import SwiftUI
import Combine

struct ContentView: View {
    @StateObject private var apiService = APIService()
    
    var body: some View {
        Group {
            if apiService.isAuthenticated && !apiService.shouldShowLogin {
                TabView {
                    MovieListView(listType: .watched)
                        .tabItem {
                            Image(systemName: "eye.fill")
                            Text("Watched")
                        }
                    
                    MovieListView(listType: .toWatch)
                        .tabItem {
                            Image(systemName: "bookmark.fill")
                            Text("To Watch")
                        }
                    
                    TrendingView()
                        .tabItem {
                            Image(systemName: "flame.fill")
                            Text("Trending")
                        }
                    
                    RecommendationsView()
                        .tabItem {
                            Image(systemName: "brain.head.profile")
                            Text("AI")
                        }
                    
                    SearchView()
                        .tabItem {
                            Image(systemName: "magnifyingglass")
                            Text("Search")
                        }
                }
            } else {
                LoginView()
            }
        }
        .environmentObject(apiService)
    }
}

#Preview {
    ContentView()
}

struct TrendingView: View {
    @EnvironmentObject var apiService: APIService
    @State private var movies: [SearchMovie] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var cancellables = Set<AnyCancellable>()
    
    // Callback to remove movie from trending list
    private func removeMovieFromTrending(_ movieId: Int) {
        movies.removeAll { $0.id == movieId }
    }
    
    private let columns = [
        GridItem(.adaptive(minimum: 120), spacing: 12)
    ]
    
    var body: some View {
        NavigationView {
            VStack {
                if isLoading {
                    ProgressView("Loading trending movies...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if movies.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "flame")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("No trending movies")
                            .font(.title2)
                            .foregroundColor(.gray)
                        
                        Text("Check your connection and try again")
                            .font(.body)
                            .foregroundColor(.secondary)
                        
                        Button("Retry") {
                            loadTrendingMovies()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    ScrollView {
                        LazyVGrid(columns: columns, spacing: 16) {
                            ForEach(movies) { movie in
                                TrendingMovieItemView(
                                    movie: movie,
                                    onMovieAdded: { movieId in
                                        removeMovieFromTrending(movieId)
                                    }
                                )
                            }
                        }
                        .padding()
                    }
                    .refreshable {
                        await refreshTrendingMovies()
                    }
                }
            }
            .navigationTitle("Trending")
            .navigationBarTitleDisplayMode(.large)
            .onAppear {
                if movies.isEmpty {
                    loadTrendingMovies()
                }
            }
            .alert("Error", isPresented: .constant(errorMessage != nil)) {
                Button("OK") {
                    errorMessage = nil
                }
            } message: {
                Text(errorMessage ?? "")
            }
        }
    }
    
    private func loadTrendingMovies() {
        isLoading = true
        errorMessage = nil
        
        apiService.fetchTrendingMovies()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case .failure(let error) = completion {
                        errorMessage = "Failed to load trending movies: \(error.localizedDescription)"
                    }
                },
                receiveValue: { fetchedMovies in
                    movies = fetchedMovies
                }
            )
            .store(in: &cancellables)
    }
    
    private func refreshTrendingMovies() async {
        await withCheckedContinuation { continuation in
            apiService.fetchTrendingMovies()
                .receive(on: DispatchQueue.main)
                .sink(
                    receiveCompletion: { completion in
                        if case .failure(let error) = completion {
                            errorMessage = "Failed to refresh trending movies: \(error.localizedDescription)"
                        }
                        continuation.resume()
                    },
                    receiveValue: { fetchedMovies in
                        movies = fetchedMovies
                    }
                )
                .store(in: &cancellables)
        }
    }
}

struct TrendingMovieItemView: View {
    let movie: SearchMovie
    let onMovieAdded: (Int) -> Void
    @EnvironmentObject var apiService: APIService
    @State private var showingAddToListOptions = false
    @State private var isAddingToList = false
    @State private var addToListMessage: String?
    @State private var cancellables = Set<AnyCancellable>()
    
    var body: some View {
        VStack(alignment: .center, spacing: 8) {
            // Movie Poster
            AsyncImage(url: movie.posterURL) { image in
                image
                    .resizable()
                    .aspectRatio(2/3, contentMode: .fill)
            } placeholder: {
                Rectangle()
                    .aspectRatio(2/3, contentMode: .fill)
                    .foregroundColor(.gray.opacity(0.3))
                    .overlay(
                        Image(systemName: "photo")
                            .foregroundColor(.gray)
                            .font(.title2)
                    )
            }
            .frame(maxWidth: .infinity)
            .cornerRadius(12)
            .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
            
            // Movie Info
            VStack(alignment: .center, spacing: 4) {
                Text(movie.title)
                    .font(.caption)
                    .fontWeight(.medium)
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
                
                if let releaseDate = movie.releaseDate {
                    Text(releaseDate)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                
            }
            
            // Add to List Buttons
            if apiService.isAuthenticated {
                HStack(spacing: 6) {
                    // Add to Watched button
                    Button(action: {
                        addToList(listId: 1) // Watched list
                    }) {
                        HStack(spacing: 3) {
                            if isAddingToList {
                                ProgressView()
                                    .scaleEffect(0.6)
                            } else {
                                Image(systemName: "eye.fill")
                                    .font(.system(size: 10))
                            }
                            Text("Watched")
                                .font(.system(size: 9))
                                .fontWeight(.medium)
                        }
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.green)
                        .cornerRadius(12)
                    }
                    .disabled(isAddingToList)
                    
                    // Add to To Watch button
                    Button(action: {
                        addToList(listId: 2) // To Watch list
                    }) {
                        HStack(spacing: 3) {
                            if isAddingToList {
                                ProgressView()
                                    .scaleEffect(0.6)
                            } else {
                                Image(systemName: "bookmark.fill")
                                    .font(.system(size: 10))
                            }
                            Text("To Watch")
                                .font(.system(size: 9))
                                .fontWeight(.medium)
                        }
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue)
                        .cornerRadius(12)
                    }
                    .disabled(isAddingToList)
                }
            }
        }
        .alert("Info", isPresented: .constant(addToListMessage != nil)) {
            Button("OK") {
                addToListMessage = nil
            }
        } message: {
            Text(addToListMessage ?? "")
        }
    }
    
    private func addToList(listId: Int) {
        // Prevent multiple simultaneous requests
        guard !isAddingToList else { return }
        
        isAddingToList = true
        
        apiService.addMovieFromSearch(tmdbId: movie.id, listId: listId)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isAddingToList = false
                    if case .failure(let error) = completion {
                        addToListMessage = "Failed to add movie: \(error.localizedDescription)"
                    }
                },
                receiveValue: { success in
                    if success {
                        let listName = listId == 1 ? "Watched" : "To Watch"
                        addToListMessage = "Added \(movie.title) to \(listName) list"
                        
                        // Remove movie from trending list
                        onMovieAdded(movie.id)
                        
                        // Trigger a single optimized refresh for both lists
                        apiService.fetchAllRecords(forceRefresh: true)
                            .receive(on: DispatchQueue.main)
                            .sink(receiveCompletion: { _ in }, receiveValue: { _ in 
                                // Data is already cached, notify views to update
                                NotificationCenter.default.post(name: .refreshRecords, object: nil)
                            })
                            .store(in: &cancellables)
                    }
                }
            )
            .store(in: &cancellables)
    }
}