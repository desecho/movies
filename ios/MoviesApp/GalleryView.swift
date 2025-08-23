import SwiftUI
import Combine

struct GalleryView: View {
    let records: [Record]
    let listType: ListType
    @State private var selectedRecord: Record?
    @State private var showingMovieDetail = false
    @EnvironmentObject var apiService: APIService
    
    private let columns = [
        GridItem(.adaptive(minimum: 120), spacing: 8)
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
            } else {
                LazyVGrid(columns: columns, spacing: 12) {
                    ForEach(records) { record in
                        GalleryItemView(record: record, listType: listType)
                            .onTapGesture {
                                selectedRecord = record
                                showingMovieDetail = true
                            }
                    }
                }
                .padding()
            }
        }
        .sheet(isPresented: $showingMovieDetail) {
            if let selectedRecord = selectedRecord {
                MovieDetailView(record: selectedRecord, listType: listType)
            }
        }
    }
}

struct GalleryItemView: View {
    let record: Record
    let listType: ListType
    
    var body: some View {
        VStack(alignment: .center, spacing: 4) {
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
            .frame(maxWidth: .infinity)
            .cornerRadius(12)
            .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
            
            // Movie title - truncated to fit
            Text(record.movie.title)
                .font(.caption)
                .fontWeight(.medium)
                .lineLimit(2)
                .multilineTextAlignment(.center)
                .frame(maxWidth: .infinity)
                .fixedSize(horizontal: false, vertical: true)
            
            // Rating for watched movies
            if listType == .watched && record.rating > 0 {
                HStack(spacing: 2) {
                    ForEach(1...5, id: \.self) { star in
                        Image(systemName: star <= record.rating ? "star.fill" : "star")
                            .foregroundColor(star <= record.rating ? .yellow : .gray.opacity(0.3))
                            .font(.system(size: 8))
                    }
                }
            }
            
            // Release year
            if let releaseDate = record.movie.releaseDate {
                Text(releaseDate)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
    }
}

#Preview {
    let sampleMovie = Movie(
        id: 1,
        title: "Sample Movie",
        titleOriginal: "Sample Movie",
        isReleased: true,
        posterSmall: nil,
        posterNormal: nil,
        posterBig: nil,
        imdbRating: 7.5,
        releaseDate: "2023",
        releaseDateTimestamp: 1672531200,
        country: "US",
        director: "Sample Director",
        writer: "Sample Writer",
        genre: "Action",
        actors: "Sample Actors",
        overview: "A sample movie for preview",
        homepage: nil,
        runtime: "120 min",
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
        rating: 4,
        comment: "",
        commentArea: false,
        listId: 1,
        additionDate: Date().timeIntervalSince1970,
        options: sampleOptions,
        providerRecords: []
    )
    
    GalleryView(records: [sampleRecord, sampleRecord, sampleRecord], listType: .watched)
        .environmentObject(APIService())
}