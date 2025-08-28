import SwiftUI
import Combine

struct RecommendationsView: View {
    @EnvironmentObject var apiService: APIService
    @State private var movies: [SearchMovie] = []
    @State private var preferences = RecommendationPreferences()
    @State private var isLoading = false
    @State private var hasSearched = false
    @State private var errorMessage: String?
    @State private var showingPreferences = false
    @State private var cancellables = Set<AnyCancellable>()
    
    private let columns = [
        GridItem(.adaptive(minimum: 120), spacing: 12)
    ]
    
    var body: some View {
        NavigationView {
            VStack {
                if hasSearched && movies.isEmpty && !isLoading {
                    emptyStateView
                } else if hasSearched && !movies.isEmpty {
                    recommendationsListView
                } else if isLoading {
                    loadingView
                } else {
                    gettingStartedView
                }
            }
            .navigationTitle("AI Recommendations")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Preferences") {
                        showingPreferences = true
                    }
                    .disabled(isLoading)
                }
            }
            .sheet(isPresented: $showingPreferences) {
                PreferencesSheetView(preferences: $preferences) {
                    getRecommendations()
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
    
    private var gettingStartedView: some View {
        VStack(spacing: 20) {
            Image(systemName: "brain.head.profile")
                .font(.system(size: 60))
                .foregroundColor(.blue)
            
            Text("Ready to discover new movies?")
                .font(.title2)
                .fontWeight(.semibold)
            
            Text("Let AI analyze your viewing history and preferences to recommend movies tailored just for you!")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            Button("Get AI Recommendations") {
                showingPreferences = true
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
        .padding()
    }
    
    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.5)
            
            Text("AI is analyzing your preferences...")
                .font(.headline)
                .foregroundColor(.primary)
            
            Text("This may take a few moments")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private var emptyStateView: some View {
        VStack(spacing: 20) {
            Image(systemName: "brain.head.profile")
                .font(.system(size: 60))
                .foregroundColor(.gray)
            
            Text("No recommendations found")
                .font(.title2)
                .fontWeight(.semibold)
            
            Text("Try adjusting your preferences and search again")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            
            Button("Adjust Preferences") {
                showingPreferences = true
            }
            .buttonStyle(.bordered)
        }
        .padding()
    }
    
    private var recommendationsListView: some View {
        VStack(alignment: .leading) {
            HStack {
                Text("\(movies.count) AI Recommendations")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                Spacer()
                
                Button("New Search") {
                    showingPreferences = true
                }
                .font(.caption)
                .buttonStyle(.bordered)
                .controlSize(.small)
            }
            .padding(.horizontal)
            
            ScrollView {
                LazyVGrid(columns: columns, spacing: 16) {
                    ForEach(movies) { movie in
                        RecommendationItemView(
                            movie: movie,
                            onMovieAdded: { movieId in
                                removeMovieFromRecommendations(movieId)
                            }
                        )
                    }
                }
                .padding()
            }
            .refreshable {
                await refreshRecommendations()
            }
        }
    }
    
    private func getRecommendations() {
        isLoading = true
        hasSearched = true
        errorMessage = nil
        movies = []
        
        apiService.fetchAIRecommendations(preferences: preferences)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case .failure(let error) = completion {
                        errorMessage = "Failed to get AI recommendations: \(error.localizedDescription)"
                    }
                },
                receiveValue: { fetchedMovies in
                    movies = fetchedMovies
                    if movies.isEmpty {
                        errorMessage = "No recommendations found for your preferences. Try adjusting them!"
                    }
                }
            )
            .store(in: &cancellables)
    }
    
    private func refreshRecommendations() async {
        await withCheckedContinuation { continuation in
            apiService.fetchAIRecommendations(preferences: preferences)
                .receive(on: DispatchQueue.main)
                .sink(
                    receiveCompletion: { completion in
                        if case .failure(let error) = completion {
                            errorMessage = "Failed to refresh recommendations: \(error.localizedDescription)"
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
    
    private func removeMovieFromRecommendations(_ movieId: Int) {
        movies.removeAll { $0.id == movieId }
    }
}

struct PreferencesSheetView: View {
    @Binding var preferences: RecommendationPreferences
    @Environment(\.dismiss) private var dismiss
    let onGetRecommendations: () -> Void
    
    var body: some View {
        NavigationView {
            Form {
                Section("Movie Preferences") {
                    Picker("Preferred Genre", selection: $preferences.preferredGenre) {
                        Text("Any Genre").tag(MovieGenre?.none)
                        ForEach(MovieGenre.allCases) { genre in
                            Text(genre.rawValue).tag(MovieGenre?.some(genre))
                        }
                    }
                    .pickerStyle(.menu)
                }
                
                Section("Rating & Count") {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Minimum Rating: \(preferences.minRating != nil ? "\(preferences.minRating!) stars" : "Any")")
                        
                        HStack {
                            Text("Any")
                                .font(.caption)
                            
                            Slider(
                                value: Binding(
                                    get: { Double(preferences.minRating ?? 0) },
                                    set: { preferences.minRating = $0 == 0 ? nil : Int($0) }
                                ),
                                in: 0...Double(AIRecommendationConstants.maxRating),
                                step: 1
                            )
                            
                            Text("\(AIRecommendationConstants.maxRating) stars")
                                .font(.caption)
                        }
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Number of Recommendations: \(preferences.recommendationsNumber)")
                        
                        Slider(
                            value: Binding(
                                get: { Double(preferences.recommendationsNumber) },
                                set: { preferences.recommendationsNumber = Int($0) }
                            ),
                            in: Double(AIRecommendationConstants.minRecommendations)...Double(AIRecommendationConstants.maxRecommendations),
                            step: 1
                        )
                    }
                }
                
                Section("Year Range") {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Year Range: \(preferences.yearRange.lowerBound) - \(preferences.yearRange.upperBound)")
                        
                        // Custom range slider implementation using two separate sliders
                        VStack {
                            HStack {
                                Text("From:")
                                Slider(
                                    value: Binding(
                                        get: { Double(preferences.yearRange.lowerBound) },
                                        set: { newValue in
                                            let startYear = Int(newValue)
                                            let endYear = max(startYear, preferences.yearRange.upperBound)
                                            preferences.yearRange = startYear...endYear
                                        }
                                    ),
                                    in: Double(AIRecommendationConstants.minYear)...Double(AIRecommendationConstants.currentYear),
                                    step: 1
                                )
                                Text("\(preferences.yearRange.lowerBound)")
                                    .frame(width: 50)
                            }
                            
                            HStack {
                                Text("To:")
                                Slider(
                                    value: Binding(
                                        get: { Double(preferences.yearRange.upperBound) },
                                        set: { newValue in
                                            let endYear = Int(newValue)
                                            let startYear = min(endYear, preferences.yearRange.lowerBound)
                                            preferences.yearRange = startYear...endYear
                                        }
                                    ),
                                    in: Double(AIRecommendationConstants.minYear)...Double(AIRecommendationConstants.currentYear),
                                    step: 1
                                )
                                Text("\(preferences.yearRange.upperBound)")
                                    .frame(width: 50)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Preferences")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Get Recommendations") {
                        dismiss()
                        onGetRecommendations()
                    }
                    .fontWeight(.semibold)
                }
            }
        }
    }
}

struct RecommendationItemView: View {
    let movie: SearchMovie
    let onMovieAdded: (Int) -> Void
    @EnvironmentObject var apiService: APIService
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
                        
                        // Remove movie from recommendations list
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

#Preview {
    RecommendationsView()
        .environmentObject(APIService())
}