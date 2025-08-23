import SwiftUI
import Combine

struct MovieDetailView: View {
    let record: Record
    let listType: ListType
    @State private var currentRating: Int
    @State private var isUpdatingRating = false
    @State private var showingOptionsSheet = false
    @State private var cancellables = Set<AnyCancellable>()
    @EnvironmentObject var apiService: APIService
    @Environment(\.dismiss) private var dismiss
    
    init(record: Record, listType: ListType) {
        self.record = record
        self.listType = listType
        self._currentRating = State(initialValue: record.rating)
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Header with poster and basic info
                    HStack(alignment: .top, spacing: 16) {
                        AsyncImage(url: record.movie.posterURL) { image in
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
                                        .font(.title)
                                )
                        }
                        .frame(width: 120, height: 180)
                        .cornerRadius(12)
                        .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
                        
                        VStack(alignment: .leading, spacing: 8) {
                            Text(record.movie.title)
                                .font(.title2)
                                .fontWeight(.bold)
                                .fixedSize(horizontal: false, vertical: true)
                            
                            if record.movie.titleOriginal != record.movie.title {
                                Text(record.movie.titleOriginal)
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                            
                            if let releaseDate = record.movie.releaseDate {
                                Label(releaseDate, systemImage: "calendar")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            
                            if let runtime = record.movie.runtime {
                                Label(runtime, systemImage: "clock")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            
                            if let imdbRating = record.movie.imdbRating {
                                Label(String(format: "%.1f", imdbRating), systemImage: "star.circle")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        }
                        
                        Spacer()
                    }
                    
                    // User rating section
                    if listType == .watched {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Your Rating")
                                .font(.headline)
                            
                            StarRatingView(
                                currentRating: currentRating,
                                onRatingTap: { rating in
                                    updateRating(to: rating)
                                },
                                isUpdating: isUpdatingRating
                            )
                        }
                        .padding(.vertical, 8)
                        .padding(.horizontal, 16)
                        .background(Color(.systemGray6))
                        .cornerRadius(12)
                    } else if record.rating > 0 {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Rating")
                                .font(.headline)
                            
                            HStack(spacing: 4) {
                                ForEach(1...5, id: \.self) { star in
                                    Image(systemName: star <= record.rating ? "star.fill" : "star")
                                        .foregroundColor(star <= record.rating ? .yellow : .gray)
                                        .font(.title3)
                                }
                                Text("(\(record.rating)/5)")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.vertical, 8)
                        .padding(.horizontal, 16)
                        .background(Color(.systemGray6))
                        .cornerRadius(12)
                    }
                    
                    // Movie details
                    if let overview = record.movie.overview, !overview.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Overview")
                                .font(.headline)
                            Text(overview)
                                .font(.body)
                        }
                    }
                    
                    if let genre = record.movie.genre, !genre.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Genre")
                                .font(.headline)
                            Text(genre)
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    if let director = record.movie.director, !director.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Director")
                                .font(.headline)
                            Text(director)
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    if let actors = record.movie.actors, !actors.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Cast")
                                .font(.headline)
                            Text(actors)
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    // Action buttons
                    if listType == .watched {
                        Button("Movie Options") {
                            showingOptionsSheet = true
                        }
                        .buttonStyle(.borderedProminent)
                        .frame(maxWidth: .infinity)
                    }
                }
                .padding()
            }
            .navigationTitle("Movie Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
        .sheet(isPresented: $showingOptionsSheet) {
            if listType == .watched {
                OptionsView(record: record, onSave: {
                    // Notify parent to refresh data
                    NotificationCenter.default.post(name: .refreshRecords, object: nil)
                })
            }
        }
    }
    
    private func updateRating(to rating: Int) {
        guard !isUpdatingRating else { return }
        
        isUpdatingRating = true
        
        apiService.updateMovieRating(recordId: record.id, rating: rating)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isUpdatingRating = false
                    if case .failure(let error) = completion {
                        print("Failed to update rating: \(error.localizedDescription)")
                    }
                },
                receiveValue: { success in
                    if success {
                        currentRating = rating
                        // Notify parent to refresh data
                        NotificationCenter.default.post(name: .refreshRecords, object: nil)
                    }
                }
            )
            .store(in: &cancellables)
    }
}

#Preview {
    let sampleMovie = Movie(
        id: 1,
        title: "The Dark Knight",
        titleOriginal: "The Dark Knight",
        isReleased: true,
        posterSmall: nil,
        posterNormal: nil,
        posterBig: nil,
        imdbRating: 9.0,
        releaseDate: "2008",
        releaseDateTimestamp: 1215648000,
        country: "US",
        director: "Christopher Nolan",
        writer: "Jonathan Nolan, Christopher Nolan",
        genre: "Action, Crime, Drama",
        actors: "Christian Bale, Heath Ledger, Aaron Eckhart",
        overview: "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        homepage: nil,
        runtime: "152 min",
        imdbUrl: "",
        tmdbUrl: "",
        trailers: [],
        hasPoster: true
    )
    
    let sampleOptions = Options(
        original: false,
        extended: false,
        theatre: false,
        hd: false,
        fullHd: false,
        ultraHd: false,
        ignoreRewatch: false
    )
    
    let sampleRecord = Record(
        id: 1,
        order: 1,
        movie: sampleMovie,
        rating: 5,
        comment: "",
        commentArea: false,
        listId: 1,
        additionDate: Date().timeIntervalSince1970,
        options: sampleOptions,
        providerRecords: []
    )
    
    MovieDetailView(record: sampleRecord, listType: .watched)
        .environmentObject(APIService())
}