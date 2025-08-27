import Foundation
import Combine

class APIService: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var shouldShowLogin = false
    
    private var cancellables = Set<AnyCancellable>()
    
    // Dynamic base URL based on build configuration
    private let baseURL: String = {
        #if DEBUG
        return "http://127.0.0.1:8000"
        #else
        return "https://api.moviemunch.org"
        #endif
    }()
    
    // Cache for records to avoid unnecessary reloads
    private var watchedRecordsCache: [Record] = []
    private var toWatchRecordsCache: [Record] = []
    private var watchedCacheTime: Date?
    private var toWatchCacheTime: Date?
    private let cacheValidityDuration: TimeInterval = 300 // 5 minutes
    
    private var accessToken: String? {
        get { UserDefaults.standard.string(forKey: "access_token") }
        set { 
            UserDefaults.standard.set(newValue, forKey: "access_token")
            isAuthenticated = newValue != nil
        }
    }
    
    private var refreshToken: String? {
        get { UserDefaults.standard.string(forKey: "refresh_token") }
        set { UserDefaults.standard.set(newValue, forKey: "refresh_token") }
    }
    
    init() {
        isAuthenticated = accessToken != nil
    }
    
    private func handleAPIError(_ error: APIError) -> APIError {
        if case .unauthorized = error {
            handleUnauthorizedAccess()
        }
        return error
    }
    
    private func handleUnauthorizedAccess() {
        DispatchQueue.main.async {
            self.accessToken = nil
            self.refreshToken = nil
            self.currentUser = nil
            self.isAuthenticated = false
            self.shouldShowLogin = true
            self.errorMessage = "Your session has expired. Please log in again."
        }
    }
    
    func login(username: String, password: String) {
        isLoading = true
        errorMessage = nil
        shouldShowLogin = false
        
        let loginRequest = LoginRequest(username: username, password: password)
        
        guard let url = URL(string: "\(baseURL)/token/") else {
            errorMessage = "Invalid URL"
            isLoading = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONEncoder().encode(loginRequest)
        } catch {
            errorMessage = "Failed to encode login request"
            isLoading = false
            return
        }
        
        URLSession.shared.apiDataTaskPublisher(for: request)
            .map(\.0)
            .decode(type: LoginResponse.self, decoder: JSONDecoder())
            .mapError { error in
                if error is DecodingError {
                    return APIError.decodingError
                }
                return error as? APIError ?? APIError.networkError
            }
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    self.isLoading = false
                    if case .failure(let error) = completion {
                        let handledError = self.handleAPIError(error)
                        self.errorMessage = "Login failed: \(handledError.localizedDescription)"
                    }
                },
                receiveValue: { response in
                    self.accessToken = response.access
                    self.refreshToken = response.refresh
                    self.isAuthenticated = true
                    // Create a simple user object with the username from login
                    self.currentUser = User(id: 0, username: username, email: "", firstName: nil, lastName: nil)
                }
            )
            .store(in: &cancellables)
    }
    
    func logout() {
        accessToken = nil
        refreshToken = nil
        currentUser = nil
        isAuthenticated = false
        shouldShowLogin = false
        errorMessage = nil
    }
    
    func loadCurrentUser() {
        guard let token = accessToken else { return }
        
        guard let url = URL(string: "\(baseURL)/user/avatar/") else { return }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        URLSession.shared.apiDataTaskPublisher(for: request)
            .map(\.0)
            .decode(type: User.self, decoder: JSONDecoder())
            .mapError { error in
                if error is DecodingError {
                    return APIError.decodingError
                }
                return error as? APIError ?? APIError.networkError
            }
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        _ = self.handleAPIError(error)
                    }
                },
                receiveValue: { user in
                    self.currentUser = user
                }
            )
            .store(in: &cancellables)
    }
    
    func fetchRecords(for listType: ListType, forceRefresh: Bool = false) -> AnyPublisher<[Record], APIError> {
        // Check cache first unless force refresh is requested
        if !forceRefresh {
            let (cache, cacheTime) = getCacheForListType(listType)
            if let cacheTime = cacheTime, 
               Date().timeIntervalSince(cacheTime) < cacheValidityDuration,
               !cache.isEmpty {
                // Return cached data
                return Just(cache)
                    .setFailureType(to: APIError.self)
                    .eraseToAnyPublisher()
            }
        }
        
        // Use optimized fetchAllRecords to populate both caches in one go
        return fetchAllRecords(forceRefresh: forceRefresh)
            .map { (watchedRecords, toWatchRecords) in
                // Return the requested list type
                switch listType {
                case .watched:
                    return watchedRecords
                case .toWatch:
                    return toWatchRecords
                }
            }
            .eraseToAnyPublisher()
    }
    
    // MARK: - Optimized All Records Fetch
    
    func fetchAllRecords(forceRefresh: Bool = false) -> AnyPublisher<([Record], [Record]), APIError> {
        // Check if both caches are valid unless force refresh is requested
        if !forceRefresh {
            let bothCachesValid = watchedCacheTime != nil && toWatchCacheTime != nil &&
                Date().timeIntervalSince(watchedCacheTime!) < cacheValidityDuration &&
                Date().timeIntervalSince(toWatchCacheTime!) < cacheValidityDuration
            
            if bothCachesValid {
                // Return cached data for both lists
                return Just((watchedRecordsCache, toWatchRecordsCache))
                    .setFailureType(to: APIError.self)
                    .eraseToAnyPublisher()
            }
        }
        
        guard let token = accessToken else {
            return Fail(error: APIError.unauthorized)
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(baseURL)/records/") else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        return URLSession.shared.apiDataTaskPublisher(for: request)
            .map(\.0)
            .decode(type: [Record].self, decoder: JSONDecoder())
            .map { allRecords in
                // Split records into watched and to-watch lists
                let watchedRecords = allRecords.filter { $0.listId == 1 }
                let toWatchRecords = allRecords.filter { $0.listId == 2 }
                
                // Update both caches with fresh data
                let now = Date()
                self.watchedRecordsCache = watchedRecords
                self.watchedCacheTime = now
                self.toWatchRecordsCache = toWatchRecords
                self.toWatchCacheTime = now
                
                print("📱 Fetched all records in one call: \(watchedRecords.count) watched, \(toWatchRecords.count) to-watch")
                
                return (watchedRecords, toWatchRecords)
            }
            .mapError { error in
                if error is DecodingError {
                    return APIError.decodingError
                }
                return error as? APIError ?? APIError.networkError
            }
            .handleEvents(receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    _ = self.handleAPIError(error)
                }
            })
            .eraseToAnyPublisher()
    }
    
    private func getCacheForListType(_ listType: ListType) -> ([Record], Date?) {
        switch listType {
        case .watched:
            return (watchedRecordsCache, watchedCacheTime)
        case .toWatch:
            return (toWatchRecordsCache, toWatchCacheTime)
        }
    }
    
    private func updateCacheForListType(_ listType: ListType, records: [Record]) {
        let now = Date()
        switch listType {
        case .watched:
            watchedRecordsCache = records
            watchedCacheTime = now
        case .toWatch:
            toWatchRecordsCache = records
            toWatchCacheTime = now
        }
    }
    
    func invalidateCache(for listType: ListType? = nil) {
        if let listType = listType {
            switch listType {
            case .watched:
                watchedCacheTime = nil
            case .toWatch:
                toWatchCacheTime = nil
            }
        } else {
            // Invalidate all caches
            watchedCacheTime = nil
            toWatchCacheTime = nil
        }
    }
    
    func updateCacheAfterDelete(recordId: Int, from listType: ListType) {
        switch listType {
        case .watched:
            watchedRecordsCache.removeAll { $0.id == recordId }
        case .toWatch:
            toWatchRecordsCache.removeAll { $0.id == recordId }
        }
    }
    
    func updateCacheAfterMoveToWatched(_ record: Record) {
        // Remove from To Watch cache
        toWatchRecordsCache.removeAll { $0.id == record.id }
        
        // Add to Watched cache with updated properties
        let watchedRecord = Record(
            id: record.id,
            order: record.order,
            movie: record.movie,
            rating: 0, // Reset rating when moved to watched
            comment: record.comment,
            commentArea: record.commentArea,
            listId: 1, // Watched list ID
            additionDate: Date().timeIntervalSince1970,
            options: record.options,
            providerRecords: record.providerRecords
        )
        watchedRecordsCache.append(watchedRecord)
    }
    
    func searchMovies(query: String) -> AnyPublisher<[SearchMovie], APIError> {
        guard let token = accessToken else {
            return Fail(error: APIError.unauthorized)
                .eraseToAnyPublisher()
        }
        
        guard let encodedQuery = query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        let options = """
        {"popularOnly":true,"sortByDate":false}
        """
        guard let encodedOptions = options.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
              let url = URL(string: "\(baseURL)/search/?query=\(encodedQuery)&type=movie&options=\(encodedOptions)") else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        return URLSession.shared.apiDataTaskPublisher(for: request)
            .map(\.0)
            .decode(type: [SearchMovie].self, decoder: JSONDecoder())
            .mapError { error in
                if error is DecodingError {
                    return APIError.decodingError
                }
                return error as? APIError ?? APIError.networkError
            }
            .handleEvents(receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    _ = self.handleAPIError(error)
                }
            })
            .eraseToAnyPublisher()
    }
    
    func addMovieToList(movieId: Int, actionName: String, rating: Int? = nil, comment: String? = nil) -> AnyPublisher<Bool, APIError> {
        guard let token = accessToken else {
            return Fail(error: APIError.unauthorized)
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(baseURL)/add-to-list/\(movieId)/") else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let listId: Int
        if actionName == "watched" {
            listId = 1 // Watched list
        } else {
            listId = 2 // To Watch list
        }
        let requestBody: [String: Any] = [
            "listId": listId
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        } catch {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        return URLSession.shared.apiDataTaskPublisher(for: request)
            .map { _ in true }
            .handleEvents(receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    _ = self.handleAPIError(error)
                }
            })
            .eraseToAnyPublisher()
    }
    
    func deleteRecord(recordId: Int) -> AnyPublisher<Bool, APIError> {
        guard let token = accessToken else {
            return Fail(error: APIError.unauthorized)
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(baseURL)/remove-record/\(recordId)/") else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        return URLSession.shared.apiDataTaskPublisher(for: request)
            .map { _ in true }
            .handleEvents(receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    _ = self.handleAPIError(error)
                }
            })
            .eraseToAnyPublisher()
    }
    
    func markAsWatched(movieId: Int) -> AnyPublisher<Bool, APIError> {
        guard let token = accessToken else {
            return Fail(error: APIError.unauthorized)
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(baseURL)/add-to-list/\(movieId)/") else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody: [String: Any] = [
            "listId": 1 // Watched list
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        } catch {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        return URLSession.shared.apiDataTaskPublisher(for: request)
            .map { _ in true }
            .handleEvents(receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    _ = self.handleAPIError(error)
                }
            })
            .eraseToAnyPublisher()
    }
    
    func addMovieFromSearch(tmdbId: Int, listId: Int) -> AnyPublisher<Bool, APIError> {
        guard let token = accessToken else {
            return Fail(error: APIError.unauthorized)
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(baseURL)/add-to-list-from-db/") else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody: [String: Any] = [
            "movieId": tmdbId,
            "listId": listId
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        } catch {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        return URLSession.shared.apiDataTaskPublisher(for: request)
            .map { _ in true }
            .handleEvents(receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    _ = self.handleAPIError(error)
                }
            })
            .eraseToAnyPublisher()
    }
    
    func updateMovieRating(recordId: Int, rating: Int) -> AnyPublisher<Bool, APIError> {
        print("DEBUG: API updateMovieRating called with recordId: \(recordId), rating: \(rating)")
        
        guard let token = accessToken else {
            return Fail(error: APIError.unauthorized)
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(baseURL)/change-rating/\(recordId)/") else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody: [String: Any] = [
            "rating": rating
        ]
        
        print("DEBUG: Request body: \(requestBody)")
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        } catch {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        return URLSession.shared.apiDataTaskPublisher(for: request)
            .map { _ in true }
            .handleEvents(receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    _ = self.handleAPIError(error)
                }
            })
            .eraseToAnyPublisher()
    }
    
    func updateMovieOptions(recordId: Int, options: Options) -> AnyPublisher<Bool, APIError> {
        guard let token = accessToken else {
            return Fail(error: APIError.unauthorized)
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(baseURL)/record/\(recordId)/options/") else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody: [String: Any] = [
            "options": [
                "original": options.original,
                "extended": options.extended,
                "theatre": options.theatre,
                "ultraHd": options.ultraHd,
                "hd": options.hd,
                "fullHd": options.fullHd,
                "ignoreRewatch": options.ignoreRewatch
            ]
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        } catch {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        return URLSession.shared.apiDataTaskPublisher(for: request)
            .map { _ in true }
            .handleEvents(receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    _ = self.handleAPIError(error)
                }
            })
            .eraseToAnyPublisher()
    }
    
    func updateCustomOrder(recordIds: [Int]) -> AnyPublisher<Bool, APIError> {
        guard let token = accessToken else {
            return Fail(error: APIError.unauthorized)
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(baseURL)/save-records-order/") else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody: [String: Any] = [
            "records": recordIds.enumerated().map { (index, recordId) in
                return [
                    "id": recordId,
                    "order": index + 1
                ]
            }
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        } catch {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        return URLSession.shared.apiDataTaskPublisher(for: request)
            .map { _ in true }
            .handleEvents(receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    _ = self.handleAPIError(error)
                }
            })
            .eraseToAnyPublisher()
    }
    
    func fetchTrendingMovies() -> AnyPublisher<[SearchMovie], APIError> {
        guard let url = URL(string: "\(baseURL)/trending/") else {
            return Fail(error: APIError.networkError)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        
        // Add authorization header if user is authenticated (for filtering)
        if let token = accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        return URLSession.shared.apiDataTaskPublisher(for: request)
            .map(\.0)
            .decode(type: [SearchMovie].self, decoder: JSONDecoder())
            .mapError { error in
                if error is DecodingError {
                    return APIError.decodingError
                }
                return error as? APIError ?? APIError.networkError
            }
            .handleEvents(receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    _ = self.handleAPIError(error)
                }
            })
            .eraseToAnyPublisher()
    }
}
