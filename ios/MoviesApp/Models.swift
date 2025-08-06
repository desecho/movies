import Foundation

struct User: Codable {
    let id: Int
    let username: String
    let email: String
    let firstName: String?
    let lastName: String?
    
    enum CodingKeys: String, CodingKey {
        case id, username, email
        case firstName = "first_name"
        case lastName = "last_name"
    }
}

struct Movie: Codable, Identifiable {
    let id: Int
    let title: String
    let overview: String?
    let releaseDate: String?
    let posterPath: String?
    let backdropPath: String?
    let voteAverage: Double?
    let runtime: Int?
    let genres: [Genre]?
    
    enum CodingKeys: String, CodingKey {
        case id, title, overview, runtime, genres
        case releaseDate = "release_date"
        case posterPath = "poster_path"
        case backdropPath = "backdrop_path"
        case voteAverage = "vote_average"
    }
    
    var posterURL: URL? {
        guard let posterPath = posterPath else { return nil }
        return URL(string: "https://image.tmdb.org/t/p/w500\(posterPath)")
    }
    
    var backdropURL: URL? {
        guard let backdropPath = backdropPath else { return nil }
        return URL(string: "https://image.tmdb.org/t/p/w780\(backdropPath)")
    }
}

struct Genre: Codable, Identifiable {
    let id: Int
    let name: String
}

struct Record: Codable, Identifiable {
    let id: Int
    let movie: Movie
    let action: Action
    let rating: Int?
    let comment: String?
    let dateAdded: String
    
    enum CodingKeys: String, CodingKey {
        case id, movie, action, rating, comment
        case dateAdded = "date_added"
    }
}

struct Action: Codable {
    let id: Int
    let name: String
}

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct LoginResponse: Codable {
    let access: String
    let refresh: String
}

struct SearchResponse: Codable {
    let results: [Movie]
    let totalResults: Int
    let totalPages: Int
    
    enum CodingKeys: String, CodingKey {
        case results
        case totalResults = "total_results"
        case totalPages = "total_pages"
    }
}

enum ListType {
    case watched
    case toWatch
    
    var title: String {
        switch self {
        case .watched:
            return "Watched Movies"
        case .toWatch:
            return "To Watch"
        }
    }
    
    var actionName: String {
        switch self {
        case .watched:
            return "watched"
        case .toWatch:
            return "want_to_watch"
        }
    }
}