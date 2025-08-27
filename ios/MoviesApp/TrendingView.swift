import SwiftUI
import Combine

struct TrendingView: View {
    @EnvironmentObject var apiService: APIService
    @State private var movies: [SearchMovie] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var cancellables = Set<AnyCancellable>()
    
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
                                TrendingMovieItemView(movie: movie)
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
                
                // Trending indicator
                HStack(spacing: 4) {
                    Image(systemName: "flame.fill")
                        .foregroundColor(.orange)
                        .font(.caption2)
                    Text("Trending")
                        .font(.caption2)
                        .foregroundColor(.orange)
                        .fontWeight(.medium)
                }
            }
            
            // Add to List Button
            if apiService.isAuthenticated {
                Button(action: {
                    showingAddToListOptions = true
                }) {
                    HStack(spacing: 4) {
                        if isAddingToList {
                            ProgressView()
                                .scaleEffect(0.8)
                        } else {
                            Image(systemName: "plus.circle")
                                .font(.caption)
                        }
                        Text("Add")
                            .font(.caption)
                            .fontWeight(.medium)
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.blue)
                    .cornerRadius(16)
                }
                .disabled(isAddingToList)
                .confirmationDialog("Add to List", isPresented: $showingAddToListOptions) {
                    Button("Add to Watched") {
                        addToList(listId: 1) // Watched list
                    }
                    Button("Add to To Watch") {
                        addToList(listId: 2) // To Watch list
                    }
                    Button("Cancel", role: .cancel) { }
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
                        // Notify other views to refresh their data
                        NotificationCenter.default.post(name: .refreshRecords, object: nil)
                    }
                }
            )
            .store(in: &cancellables)
    }
}

#Preview {
    TrendingView()
        .environmentObject(APIService())
}