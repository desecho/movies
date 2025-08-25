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
    case ratingHighest = "Rating (Highest)"
    case ratingLowest = "Rating (Lowest)"
    case custom = "Custom Order"
    
    var systemImage: String {
        switch self {
        case .dateAddedNewest, .dateAddedOldest:
            return "calendar.badge.plus"
        case .releaseDateNewest, .releaseDateOldest:
            return "calendar"
        case .ratingHighest, .ratingLowest:
            return "star.fill"
        case .custom:
            return "hand.draw"
        }
    }
}

enum ViewMode: String, CaseIterable {
    case list = "List"
    case gallery = "Gallery"
    
    var systemImage: String {
        switch self {
        case .list:
            return "list.bullet"
        case .gallery:
            return "square.grid.3x3"
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
    @State private var currentViewMode: ViewMode = .list
    @State private var searchText = ""
    
    private var filteredAndSortedRecords: [Record] {
        let filtered = filterRecords(records)
        return sortRecords(filtered)
    }
    
    private func filterRecords(_ records: [Record]) -> [Record] {
        if searchText.isEmpty {
            return records
        }
        
        let lowercasedSearchText = searchText.lowercased()
        
        return records.filter { record in
            // Search in title
            if record.movie.title.lowercased().contains(lowercasedSearchText) ||
               record.movie.titleOriginal.lowercased().contains(lowercasedSearchText) {
                return true
            }
            
            // Search in director
            if let director = record.movie.director,
               director.lowercased().contains(lowercasedSearchText) {
                return true
            }
            
            // Search in actors
            if let actors = record.movie.actors,
               actors.lowercased().contains(lowercasedSearchText) {
                return true
            }
            
            return false
        }
    }
    
    private func sortRecords(_ records: [Record]) -> [Record] {
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
        case .ratingHighest:
            if listType == .watched {
                // Sort by user rating for watched movies - unrated (0) movies go to bottom
                return records.sorted { record1, record2 in
                    if record1.rating == 0 && record2.rating == 0 {
                        return false // Both unrated, maintain original order
                    } else if record1.rating == 0 {
                        return false // record1 is unrated, goes after record2
                    } else if record2.rating == 0 {
                        return true // record2 is unrated, record1 goes first
                    } else {
                        return record1.rating > record2.rating // Both rated, normal comparison
                    }
                }
            } else {
                // Sort by IMDB rating for to-watch movies - unrated movies go to bottom
                return records.sorted { record1, record2 in
                    let rating1 = record1.movie.imdbRating ?? 0
                    let rating2 = record2.movie.imdbRating ?? 0
                    if rating1 == 0 && rating2 == 0 {
                        return false // Both unrated, maintain original order
                    } else if rating1 == 0 {
                        return false // record1 is unrated, goes after record2
                    } else if rating2 == 0 {
                        return true // record2 is unrated, record1 goes first
                    } else {
                        return rating1 > rating2 // Both rated, normal comparison
                    }
                }
            }
        case .ratingLowest:
            if listType == .watched {
                // Sort by user rating for watched movies - unrated (0) movies go to bottom
                return records.sorted { record1, record2 in
                    if record1.rating == 0 && record2.rating == 0 {
                        return false // Both unrated, maintain original order
                    } else if record1.rating == 0 {
                        return false // record1 is unrated, goes after record2
                    } else if record2.rating == 0 {
                        return true // record2 is unrated, record1 goes first
                    } else {
                        return record1.rating < record2.rating // Both rated, normal comparison
                    }
                }
            } else {
                // Sort by IMDB rating for to-watch movies - unrated movies go to bottom
                return records.sorted { record1, record2 in
                    let rating1 = record1.movie.imdbRating ?? 0
                    let rating2 = record2.movie.imdbRating ?? 0
                    if rating1 == 0 && rating2 == 0 {
                        return false // Both unrated, maintain original order
                    } else if rating1 == 0 {
                        return false // record1 is unrated, goes after record2
                    } else if rating2 == 0 {
                        return true // record2 is unrated, record1 goes first
                    } else {
                        return rating1 < rating2 // Both rated, normal comparison
                    }
                }
            }
        case .custom:
            return records.sorted { $0.order < $1.order }
        }
    }
    
    var body: some View {
        NavigationView {
            VStack {
                if isLoading {
                    ProgressView("Loading movies...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if currentViewMode == .list {
                    // List View
                    if filteredAndSortedRecords.isEmpty && !records.isEmpty {
                        // No results found for search
                        VStack(spacing: 20) {
                            Image(systemName: "magnifyingglass")
                                .font(.system(size: 60))
                                .foregroundColor(.gray)
                            
                            Text("No movies found")
                                .font(.title2)
                                .foregroundColor(.gray)
                                .multilineTextAlignment(.center)
                            
                            Text("Try adjusting your search terms")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
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
                        List(filteredAndSortedRecords) { record in
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
                } else {
                    // Gallery View
                    GalleryView(records: filteredAndSortedRecords, listType: listType, currentSort: currentSort)
                }
            }
            .searchable(text: $searchText, prompt: "Search by title, actor, or director")
            .navigationTitle(listType.title)
            .toolbar {
                ToolbarItemGroup(placement: .navigationBarLeading) {
                    Button {
                        showingSortPicker = true
                    } label: {
                        Image(systemName: "arrow.up.arrow.down")
                            .foregroundColor(.primary)
                    }
                    
                    Button {
                        currentViewMode = currentViewMode == .list ? .gallery : .list
                    } label: {
                        Image(systemName: currentViewMode.systemImage)
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
                    let tappedRating = max(1, min(5, starIndex))
                    
                    // If the same rating is tapped again, reset to 0
                    let finalRating = (tappedRating == currentRating) ? 0 : tappedRating
                    
                    print("DEBUG: Star \(tappedRating) tapped at location \(location), current: \(currentRating), final: \(finalRating)")
                    onRatingTap(finalRating)
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

struct GalleryView: View {
    @State private var records: [Record]
    let listType: ListType
    let currentSort: SortOption
    let externalRecords: [Record]
    @State private var cancellables = Set<AnyCancellable>()
    @EnvironmentObject var apiService: APIService
    
    init(records: [Record], listType: ListType, currentSort: SortOption) {
        self._records = State(initialValue: records)
        self.externalRecords = records
        self.listType = listType
        self.currentSort = currentSort
    }
    
    private let columns = [
        GridItem(.adaptive(minimum: 80), spacing: 6)
    ]
    
    var body: some View {
        ScrollView {
            if records.isEmpty {
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
                .padding()
            } else if listType == .toWatch && currentSort == .custom {
                // Drag and drop enabled for to watch list in custom sort mode
                LazyVGrid(columns: columns, spacing: 8) {
                    ForEach(records) { record in
                        GalleryItemView(record: record, listType: listType)
                            .draggable(record)
                    }
                }
                .padding(8)
                .dropDestination(for: Record.self) { items, location in
                    for item in items {
                        if let fromIndex = records.firstIndex(where: { $0.id == item.id }) {
                            let toIndex = calculateDropIndex(location: location)
                            if fromIndex != toIndex {
                                withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {
                                    records.move(fromOffsets: IndexSet(integer: fromIndex), toOffset: toIndex > fromIndex ? toIndex + 1 : toIndex)
                                }
                                updateCustomOrder()
                            }
                        }
                    }
                    return true
                }
            } else {
                // Regular grid without drag and drop
                LazyVGrid(columns: columns, spacing: 8) {
                    ForEach(records) { record in
                        GalleryItemView(record: record, listType: listType)
                    }
                }
                .padding(8)
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: .refreshRecords)) { _ in
            // Don't update records during custom sort mode to preserve drag changes
            if currentSort != .custom {
                // This will be handled by parent view
            }
        }
        .onChange(of: externalRecords) { oldValue, newValue in
            // Update internal records when parent provides new data
            if currentSort != .custom {
                records = newValue
            }
        }
    }
    
    private func calculateDropIndex(location: CGPoint) -> Int {
        // Simple calculation for drop index based on grid layout
        let itemWidth: CGFloat = 80 + 6 // minimum width + spacing
        let columnsPerRow = max(1, Int(UIScreen.main.bounds.width / itemWidth))
        let row = Int(location.y / (itemWidth * 1.5)) // approximate item height
        let column = Int(location.x / itemWidth)
        let index = min(records.count, max(0, row * columnsPerRow + column))
        return index
    }
    
    private func updateCustomOrder() {
        let recordIds = records.map { $0.id }
        apiService.updateCustomOrder(recordIds: recordIds)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to update custom order: \(error.localizedDescription)")
                    }
                },
                receiveValue: { success in
                    if success {
                        print("Successfully updated custom order")
                        // Update local records order values
                        for (index, record) in records.enumerated() {
                            if let recordIndex = records.firstIndex(where: { $0.id == record.id }) {
                                records[recordIndex] = Record(
                                    id: record.id,
                                    order: index + 1,
                                    movie: record.movie,
                                    rating: record.rating,
                                    comment: record.comment,
                                    commentArea: record.commentArea,
                                    listId: record.listId,
                                    additionDate: record.additionDate,
                                    options: record.options,
                                    providerRecords: record.providerRecords
                                )
                            }
                        }
                    }
                }
            )
            .store(in: &cancellables)
    }
}

struct GalleryItemView: View {
    let record: Record
    let listType: ListType
    
    var body: some View {
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
                        .font(.title2)
                )
        }
        .frame(maxWidth: .infinity)
        .cornerRadius(8)
        .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
    }
}

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
    MovieListView(listType: .watched)
        .environmentObject(APIService())
}