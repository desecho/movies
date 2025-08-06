import SwiftUI
import Combine

struct MovieListView: View {
    let listType: ListType
    @EnvironmentObject var apiService: APIService
    @State private var records: [Record] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var cancellables = Set<AnyCancellable>()
    
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
                    List(records) { record in
                        MovieRowView(record: record)
                    }
                }
            }
            .navigationTitle(listType.title)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Logout") {
                        apiService.logout()
                    }
                }
            }
            .onAppear {
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

struct MovieRowView: View {
    let record: Record
    
    var body: some View {
        HStack {
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
                    if let rating = record.rating {
                        HStack(spacing: 2) {
                            Image(systemName: "star.fill")
                                .foregroundColor(.yellow)
                                .font(.caption)
                            Text("\(rating)/10")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    Spacer()
                    
                    if let releaseDate = record.movie.releaseDate {
                        Text(String(releaseDate.prefix(4)))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            Spacer()
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    MovieListView(listType: .watched)
        .environmentObject(APIService())
}