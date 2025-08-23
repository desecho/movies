import SwiftUI
import Combine

extension Notification.Name {
    static let refreshRecords = Notification.Name("refreshRecords")
}

enum SortOption: String, CaseIterable {
    case dateAddedNewest = "Date Added (Newest)"
    case dateAddedOldest = "Date Added (Oldest)"
    case releaseDateNewest = "Release Date (Newest)"
    case releaseDateOldest = "Release Date (Oldest)"
    
    var systemImage: String {
        switch self {
        case .dateAddedNewest, .dateAddedOldest:
            return "calendar.badge.plus"
        case .releaseDateNewest, .releaseDateOldest:
            return "calendar"
        }
    }
}

struct MovieListView: View {
    let listType: ListType
    @EnvironmentObject var apiService: APIService
    @State private var records: [Record] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var cancellables = Set<AnyCancellable>()
    @State private var currentSort: SortOption = .dateAddedNewest
    @State private var showingSortPicker = false
    
    private var sortedRecords: [Record] {
        switch currentSort {
        case .dateAddedNewest:
            return records.sorted { $0.additionDate > $1.additionDate }
        case .dateAddedOldest:
            return records.sorted { $0.additionDate < $1.additionDate }
        case .releaseDateNewest:
            return records.sorted { record1, record2 in
                let date1 = record1.movie.releaseDateTimestamp
                let date2 = record2.movie.releaseDateTimestamp
                return date1 > date2
            }
        case .releaseDateOldest:
            return records.sorted { record1, record2 in
                let date1 = record1.movie.releaseDateTimestamp
                let date2 = record2.movie.releaseDateTimestamp
                return date1 < date2
            }
        }
    }
    
    var body: some View {
        NavigationView {
            VStack {
                if isLoading {
                    ProgressView("Loading movies...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if records.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: listType == .watched ? "eye.slash" : "bookmark.slash")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("No movies in your \(listType.title.lowercased()) list")
                            .font(.title2)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                        
                        Text("Use the search tab to add movies")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    List(sortedRecords) { record in
                        MovieRowView(record: record, listType: listType)
                            .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                                if listType == .toWatch {
                                    // Delete action
                                    Button(role: .destructive) {
                                        deleteRecord(record)
                                    } label: {
                                        Label("Delete", systemImage: "trash")
                                    }
                                    
                                    // Mark as watched action - only show if movie is released
                                    if record.movie.isReleased {
                                        Button {
                                            markAsWatched(record)
                                        } label: {
                                            Label("Watched", systemImage: "checkmark")
                                        }
                                        .tint(.green)
                                    }
                                } else if listType == .watched {
                                    // Delete action for watched list
                                    Button(role: .destructive) {
                                        deleteRecord(record)
                                    } label: {
                                        Label("Delete", systemImage: "trash")
                                    }
                                }
                            }
                    }
                }
            }
            .navigationTitle(listType.title)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button {
                        showingSortPicker = true
                    } label: {
                        Image(systemName: "arrow.up.arrow.down")
                            .foregroundColor(.primary)
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Logout") {
                        apiService.logout()
                    }
                }
            }
            .confirmationDialog("Sort Movies", isPresented: $showingSortPicker, titleVisibility: .visible) {
                ForEach(SortOption.allCases, id: \.self) { option in
                    Button(option.rawValue) {
                        currentSort = option
                    }
                }
                Button("Cancel", role: .cancel) { }
            }
            .onAppear {
                loadRecords()
            }
            .onReceive(NotificationCenter.default.publisher(for: .refreshRecords)) { _ in
                loadRecords()
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
    
    private func deleteRecord(_ record: Record) {
        apiService.deleteRecord(recordId: record.id)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        errorMessage = "Failed to delete movie: \(error.localizedDescription)"
                    }
                },
                receiveValue: { success in
                    if success {
                        // Refresh the list
                        loadRecords()
                    }
                }
            )
            .store(in: &cancellables)
    }
    
    private func markAsWatched(_ record: Record) {
        apiService.markAsWatched(movieId: record.movie.id)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        errorMessage = "Failed to mark as watched: \(error.localizedDescription)"
                    }
                },
                receiveValue: { success in
                    if success {
                        // Backend automatically moves the movie to Watched list
                        // Just refresh the list to show the updated state
                        loadRecords()
                    }
                }
            )
            .store(in: &cancellables)
    }
    
    private func loadRecords() {
        isLoading = true
        errorMessage = nil
        
        apiService.fetchRecords(for: listType)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case .failure(let error) = completion {
                        errorMessage = "Failed to load movies: \(error.localizedDescription)"
                    }
                },
                receiveValue: { fetchedRecords in
                    records = fetchedRecords
                }
            )
            .store(in: &cancellables)
    }
}

struct StarRatingView: View {
    let currentRating: Int
    let onRatingTap: (Int) -> Void
    let isUpdating: Bool
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(1...5, id: \.self) { star in
                Image(systemName: star <= currentRating ? "star.fill" : "star")
                    .foregroundColor(star <= currentRating ? .yellow : .gray)
                    .font(.caption)
                    .frame(width: 16, height: 16)
            }
        }
        .background(Color.clear)
        .contentShape(Rectangle())
        .gesture(
            DragGesture(minimumDistance: 0)
                .onEnded { value in
                    guard !isUpdating else { return }
                    
                    let starWidth: CGFloat = 16
                    let spacing: CGFloat = 4
                    let totalWidth = (starWidth * 5) + (spacing * 4)
                    let location = value.location.x
                    
                    // Calculate which star was tapped
                    let starIndex = Int((location / (starWidth + spacing)).rounded(.up))
                    let rating = max(1, min(5, starIndex))
                    
                    print("DEBUG: Star \(rating) tapped at location \(location)")
                    onRatingTap(rating)
                }
        )
    }
}

struct MovieRowView: View {
    let record: Record
    let listType: ListType
    @State private var currentRating: Int
    @State private var isUpdatingRating = false
    @State private var showingOptionsSheet = false
    @State private var cancellables = Set<AnyCancellable>()
    @EnvironmentObject var apiService: APIService
    
    init(record: Record, listType: ListType) {
        self.record = record
        self.listType = listType
        self._currentRating = State(initialValue: record.rating)
    }
    
    var body: some View {
        HStack(spacing: 12) {
            AsyncImage(url: record.movie.posterURL) { image in
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
                Text(record.movie.title)
                    .font(.headline)
                    .lineLimit(2)
                
                if let overview = record.movie.overview {
                    Text(overview)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(3)
                }
                
                HStack {
                    if listType == .watched {
                        // Interactive star rating for watched movies
                        StarRatingView(
                            currentRating: currentRating,
                            onRatingTap: { rating in
                                updateRating(to: rating)
                            },
                            isUpdating: isUpdatingRating
                        )
                    } else if record.rating > 0 {
                        // Static rating display for to-watch movies
                        HStack(spacing: 2) {
                            Image(systemName: "star.fill")
                                .foregroundColor(.yellow)
                                .font(.caption)
                            Text("\(record.rating)/5")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    Spacer()
                    
                    if let releaseDate = record.movie.releaseDate {
                        Text(releaseDate)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            Spacer()
            
            // Options button for watched movies
            if listType == .watched {
                VStack {
                    Button(action: {
                        showingOptionsSheet = true
                    }) {
                        Image(systemName: "gearshape")
                            .font(.caption)
                            .foregroundColor(.blue)
                    }
                    .buttonStyle(PlainButtonStyle())
                }
            }
        }
        .padding(.vertical, 4)
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
        // Prevent multiple simultaneous rating updates
        guard !isUpdatingRating else { return }
        
        print("DEBUG: Updating rating to \(rating) for record \(record.id)")
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
                        print("Successfully updated rating to \(rating)")
                    }
                }
            )
            .store(in: &cancellables)
    }
}

struct OptionsView: View {
    let record: Record
    let onSave: () -> Void
    @State private var options: Options
    @State private var isUpdating = false
    @State private var cancellables = Set<AnyCancellable>()
    @EnvironmentObject var apiService: APIService
    @Environment(\.dismiss) private var dismiss
    
    init(record: Record, onSave: @escaping () -> Void) {
        self.record = record
        self.onSave = onSave
        self._options = State(initialValue: record.options)
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Watch Options")) {
                    Toggle("Watched in Original Version", isOn: $options.original)
                    Toggle("Watched Extended Version", isOn: $options.extended)
                    Toggle("Watched in Theatre", isOn: $options.theatre)
                }
                
                Section(header: Text("Quality Options")) {
                    Toggle("Watched in HD", isOn: $options.hd)
                    Toggle("Watched in Full HD", isOn: $options.fullHd)
                    Toggle("Watched in 4K/Ultra HD", isOn: $options.ultraHd)
                }
                
                Section(header: Text("Other Options")) {
                    Toggle("Ignore for Rewatch", isOn: $options.ignoreRewatch)
                }
            }
            .navigationTitle("Movie Options")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        saveOptions()
                    }
                    .disabled(isUpdating)
                }
            }
        }
    }
    
    private func saveOptions() {
        isUpdating = true
        
        apiService.updateMovieOptions(recordId: record.id, options: options)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isUpdating = false
                    if case .failure(let error) = completion {
                        print("Failed to update options: \(error.localizedDescription)")
                    }
                },
                receiveValue: { success in
                    if success {
                        print("Successfully updated options")
                        onSave()
                        dismiss()
                    }
                }
            )
            .store(in: &cancellables)
    }
}

#Preview {
    MovieListView(listType: .watched)
        .environmentObject(APIService())
}