import SwiftUI
import Combine

struct SearchView: View {
    @EnvironmentObject var apiService: APIService
    @State private var searchText = ""
    @State private var movies: [SearchMovie] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var cancellables = Set<AnyCancellable>()
    @State private var searchCancellable: AnyCancellable?
    
    var body: some View {
        NavigationView {
            VStack {
                SearchBar(text: $searchText, onSearchButtonClicked: {
                    searchMovies()
                })
                
                if isLoading {
                    ProgressView("Searching movies...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if movies.isEmpty && !searchText.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "magnifyingglass")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("No movies found")
                            .font(.title2)
                            .foregroundColor(.gray)
                        
                        Text("Try a different search term")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if searchText.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "film.stack")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("Search for Movies")
                            .font(.title2)
                            .foregroundColor(.gray)
                        
                        Text("Enter a movie title to get started")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    List(movies) { movie in
                        SearchMovieRowView(movie: movie)
                    }
                }
            }
            .navigationTitle("Search")
            .alert("Error", isPresented: .constant(errorMessage != nil)) {
                Button("OK") {
                    errorMessage = nil
                }
            } message: {
                Text(errorMessage ?? "")
            }
        }
        .onChange(of: searchText) { newValue in
            searchCancellable?.cancel()
            
            if newValue.isEmpty {
                movies = []
                return
            }
            
            searchCancellable = Timer.publish(every: 0.5, on: .main, in: .common)
                .autoconnect()
                .first()
                .sink { _ in
                    searchMovies()
                }
        }
    }
    
    private func searchMovies() {
        guard !searchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            movies = []
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        apiService.searchMovies(query: searchText)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case .failure(let error) = completion {
                        errorMessage = "Search failed: \(error.localizedDescription)"
                    }
                },
                receiveValue: { searchResults in
                    movies = searchResults
                }
            )
            .store(in: &cancellables)
    }
}

struct SearchBar: View {
    @Binding var text: String
    var onSearchButtonClicked: () -> Void
    
    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)
            
            TextField("Search movies...", text: $text)
                .textFieldStyle(PlainTextFieldStyle())
                .onSubmit {
                    onSearchButtonClicked()
                }
            
            if !text.isEmpty {
                Button(action: {
                    text = ""
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(8)
        .background(Color(.systemGray6))
        .cornerRadius(10)
        .padding(.horizontal)
    }
}

struct SearchMovieRowView: View {
    let movie: SearchMovie
    @EnvironmentObject var apiService: APIService
    @State private var isAddingToWatched = false
    @State private var isAddingToWatch = false
    @State private var showingAddOptions = false
    @State private var cancellables = Set<AnyCancellable>()
    @State private var isHidden = false
    
    var body: some View {
        if !isHidden {
            HStack {
            AsyncImage(url: movie.posterURL) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Rectangle()
                    .foregroundColor(.gray.opacity(0.3))
                    .overlay(
                        Image(systemName: "photo")
                            .foregroundColor(.gray)
                    )
            }
            .frame(width: 60, height: 90)
            .cornerRadius(8)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(movie.title)
                    .font(.headline)
                    .lineLimit(2)
                
                HStack {
                    if movie.isReleased {
                        HStack(spacing: 2) {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                                .font(.caption)
                            Text("Released")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    } else {
                        HStack(spacing: 2) {
                            Image(systemName: "clock")
                                .foregroundColor(.orange)
                                .font(.caption)
                            Text("Upcoming")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    Spacer()
                    
                    if let releaseDate = movie.releaseDate {
                        Text(releaseDate)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            Spacer()
            
            VStack(spacing: 8) {
                if movie.isReleased {
                    Button(action: {
                        addToList(action: "watched")
                    }) {
                        HStack(spacing: 4) {
                            if isAddingToWatched {
                                ProgressView()
                                    .scaleEffect(0.6)
                            } else {
                                Image(systemName: "eye.fill")
                            }
                            Text("Watched")
                                .font(.caption)
                        }
                        .foregroundColor(.blue)
                    }
                    .disabled(isAddingToWatched || isAddingToWatch)
                } else {
                    // Disabled button for unreleased movies
                    HStack(spacing: 4) {
                        Image(systemName: "eye.slash")
                        Text("Not Released")
                            .font(.caption)
                    }
                    .foregroundColor(.gray)
                    .padding(.vertical, 8)
                }
                
                Button(action: {
                    addToList(action: "want_to_watch")
                }) {
                    HStack(spacing: 4) {
                        if isAddingToWatch {
                            ProgressView()
                                .scaleEffect(0.6)
                        } else {
                            Image(systemName: "bookmark.fill")
                        }
                        Text("To Watch")
                            .font(.caption)
                    }
                    .foregroundColor(.green)
                }
                .disabled(isAddingToWatched || isAddingToWatch)
            }
        }
        .padding(.vertical, 4)
        }
    }
    
    private func addToList(action: String) {
        if action == "watched" {
            isAddingToWatched = true
        } else {
            isAddingToWatch = true
        }
        
        let listId: Int
        if action == "watched" {
            listId = 1 // Watched list
        } else if action == "want_to_watch" {
            listId = 2 // To Watch list
        } else {
            listId = 2 // Default to To Watch list
        }
        
        apiService.addMovieFromSearch(tmdbId: movie.id, listId: listId)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    // Always reset loading states
                    isAddingToWatched = false
                    isAddingToWatch = false
                    
                    if case .failure(let error) = completion {
                        print("Failed to add movie: \(error.localizedDescription)")
                    }
                },
                receiveValue: { success in
                    if success {
                        print("Successfully added movie to \(action) list")
                        
                        // Hide the movie from search results
                        withAnimation(.easeOut(duration: 0.3)) {
                            isHidden = true
                        }
                        
                        // Force refresh records to show movie immediately in lists
                        apiService.invalidateCache()
                        
                        // Notify other views to refresh their data
                        NotificationCenter.default.post(name: .refreshRecords, object: nil)
                    }
                }
            )
            .store(in: &cancellables)
    }
}

#Preview {
    SearchView()
        .environmentObject(APIService())
}