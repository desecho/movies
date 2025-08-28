import Foundation

// MARK: - AI Recommendations Constants
struct AIRecommendationConstants {
    static let maxRecommendations = 50
    static let minRecommendations = 1
    static let minRating = 0
    static let maxRating = 5
    static let minYear = 1920
    static let currentYear = Calendar.current.component(.year, from: Date())
}

// MARK: - Movie Genres
enum MovieGenre: String, CaseIterable, Identifiable {
    case action = "Action"
    case adventure = "Adventure"
    case animation = "Animation"
    case biography = "Biography"
    case comedy = "Comedy"
    case crime = "Crime"
    case documentary = "Documentary"
    case drama = "Drama"
    case family = "Family"
    case fantasy = "Fantasy"
    case history = "History"
    case horror = "Horror"
    case musical = "Musical"
    case mystery = "Mystery"
    case romance = "Romance"
    case sciFi = "Sci-Fi"
    case sport = "Sport"
    case thriller = "Thriller"
    case war = "War"
    case western = "Western"
    
    var id: String { rawValue }
}

// MARK: - Recommendation Preferences Model
struct RecommendationPreferences {
    var preferredGenre: MovieGenre?
    var yearRange: ClosedRange<Int>
    var minRating: Int?
    var recommendationsNumber: Int
    
    init() {
        self.preferredGenre = nil
        self.yearRange = 2000...AIRecommendationConstants.currentYear
        self.minRating = nil
        self.recommendationsNumber = AIRecommendationConstants.maxRecommendations
    }
}

// MARK: - API Request Parameters
struct RecommendationRequestParameters {
    let preferredGenre: String?
    let yearStart: Int
    let yearEnd: Int
    let minRating: Int?
    let recommendationsNumber: Int
    
    init(from preferences: RecommendationPreferences) {
        self.preferredGenre = preferences.preferredGenre?.rawValue
        self.yearStart = preferences.yearRange.lowerBound
        self.yearEnd = preferences.yearRange.upperBound
        self.minRating = preferences.minRating
        self.recommendationsNumber = preferences.recommendationsNumber
    }
    
    func toQueryItems() -> [URLQueryItem] {
        var queryItems: [URLQueryItem] = []
        
        if let preferredGenre = preferredGenre {
            queryItems.append(URLQueryItem(name: "preferredGenre", value: preferredGenre))
        }
        
        queryItems.append(URLQueryItem(name: "yearStart", value: String(yearStart)))
        queryItems.append(URLQueryItem(name: "yearEnd", value: String(yearEnd)))
        
        if let minRating = minRating {
            queryItems.append(URLQueryItem(name: "minRating", value: String(minRating)))
        }
        
        queryItems.append(URLQueryItem(name: "recommendationsNumber", value: String(recommendationsNumber)))
        
        return queryItems
    }
}