import Foundation
import Combine
import CoreTransferable

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

struct Trailer: Codable, Equatable {
    let name: String?
    let key: String?
    let site: String?
    let type: String?
}

// Model for search results (MovieListResult format)
struct SearchMovie: Codable, Identifiable {
    let id: Int
    let title: String
    let titleOriginal: String
    let poster: String?
    let poster2x: String?
    let tmdbLink: String
    let releaseDate: String?
    let isReleased: Bool
    
    enum CodingKeys: String, CodingKey {
        case id, title, titleOriginal, poster, poster2x, tmdbLink, releaseDate, isReleased
    }
    
    var posterURL: URL? {
        guard let poster = poster else { return nil }
        return URL(string: poster)
    }
}

struct Movie: Codable, Identifiable, Equatable {
    let id: Int
    let title: String
    let titleOriginal: String
    let isReleased: Bool
    let posterSmall: String?
    let posterNormal: String?
    let posterBig: String?
    let imdbRating: Double?
    let releaseDate: String?
    let releaseDateTimestamp: Double
    let country: String?
    let director: String?
    let writer: String?
    let genre: String?
    let actors: String?
    let overview: String?
    let homepage: String?
    let runtime: String?
    let imdbUrl: String
    let tmdbUrl: String
    let trailers: [Trailer]
    let hasPoster: Bool
    
    enum CodingKeys: String, CodingKey {
        case id, title, titleOriginal, isReleased, posterSmall, posterNormal, posterBig
        case imdbRating, releaseDate, releaseDateTimestamp, country, director, writer
        case genre, actors, overview, homepage, runtime, imdbUrl, tmdbUrl, trailers, hasPoster
    }
    
    var posterURL: URL? {
        guard let posterNormal = posterNormal else { return nil }
        return URL(string: posterNormal)
    }
    
    var backdropURL: URL? {
        guard let posterBig = posterBig else { return nil }
        return URL(string: posterBig)
    }
}

struct Genre: Codable, Identifiable {
    let id: Int
    let name: String
}

struct Options: Codable, Equatable {
    var original: Bool
    var extended: Bool
    var theatre: Bool
    var hd: Bool
    var fullHd: Bool
    var ultraHd: Bool
    var ignoreRewatch: Bool
}

struct ProviderRecord: Codable, Equatable {
    let tmdbWatchUrl: String
    let provider: Provider
}

struct Provider: Codable, Equatable {
    let logo: String
    let name: String
}

struct Record: Codable, Identifiable, Transferable, Equatable {
    let id: Int
    let order: Int
    let movie: Movie
    let rating: Int
    let comment: String
    let commentArea: Bool
    let listId: Int
    let additionDate: Double
    let options: Options
    let providerRecords: [ProviderRecord]
    
    enum CodingKeys: String, CodingKey {
        case id, order, movie, rating, comment, commentArea, listId, additionDate, options, providerRecords
    }
    
    static var transferRepresentation: some TransferRepresentation {
        CodableRepresentation(contentType: .data)
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

enum APIError: Error {
    case unauthorized
    case forbidden
    case notFound
    case serverError
    case networkError
    case decodingError
    case unknown(Int)
    
    var localizedDescription: String {
        switch self {
        case .unauthorized:
            return "Your session has expired. Please log in again."
        case .forbidden:
            return "You don't have permission to access this resource."
        case .notFound:
            return "The requested resource was not found."
        case .serverError:
            return "Server error occurred. Please try again later."
        case .networkError:
            return "Network connection error. Please check your internet connection."
        case .decodingError:
            return "Failed to process server response."
        case .unknown(let statusCode):
            return "An error occurred (Status: \(statusCode)). Please try again."
        }
    }
}

extension URLSession {
    func apiDataTaskPublisher(for request: URLRequest) -> AnyPublisher<(Data, HTTPURLResponse), APIError> {
        return self.dataTaskPublisher(for: request)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw APIError.networkError
                }
                
                switch httpResponse.statusCode {
                case 200...299:
                    return (data, httpResponse)
                case 401:
                    throw APIError.unauthorized
                case 403:
                    throw APIError.forbidden
                case 404:
                    throw APIError.notFound
                case 500...599:
                    throw APIError.serverError
                default:
                    throw APIError.unknown(httpResponse.statusCode)
                }
            }
            .mapError { error in
                if let apiError = error as? APIError {
                    return apiError
                }
                return APIError.networkError
            }
            .eraseToAnyPublisher()
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
    
    var listId: Int {
        switch self {
        case .watched:
            return 1
        case .toWatch:
            return 2
        }
    }
}