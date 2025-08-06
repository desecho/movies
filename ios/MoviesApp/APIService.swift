import Foundation
import Combine

class APIService: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private var cancellables = Set<AnyCancellable>()
    private let baseURL = "http://127.0.0.1:8000"
    
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
    
    func login(username: String, password: String) {
        isLoading = true
        errorMessage = nil
        
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
        
        URLSession.shared.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: LoginResponse.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    self.isLoading = false
                    if case .failure(let error) = completion {
                        self.errorMessage = "Login failed: \(error.localizedDescription)"
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
    }
    
    func loadCurrentUser() {
        guard let token = accessToken else { return }
        
        guard let url = URL(string: "\(baseURL)/user/avatar/") else { return }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        URLSession.shared.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: User.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(_) = completion {
                        self.logout()
                    }
                },
                receiveValue: { user in
                    self.currentUser = user
                }
            )
            .store(in: &cancellables)
    }
    
    func fetchRecords(for listType: ListType) -> AnyPublisher<[Record], Error> {
        guard let token = accessToken else {
            return Fail(error: URLError(.userAuthenticationRequired))
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(baseURL)/records/?action=\(listType.actionName)") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        return URLSession.shared.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: [Record].self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }
    
    func searchMovies(query: String) -> AnyPublisher<[Movie], Error> {
        guard let token = accessToken else {
            return Fail(error: URLError(.userAuthenticationRequired))
                .eraseToAnyPublisher()
        }
        
        guard let encodedQuery = query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        let options = """
        {"popularOnly":true,"sortByDate":false}
        """
        guard let encodedOptions = options.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
              let url = URL(string: "\(baseURL)/search/?query=\(encodedQuery)&type=movie&options=\(encodedOptions)") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        return URLSession.shared.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: [Movie].self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }
    
    func addMovieToList(movieId: Int, actionName: String, rating: Int? = nil, comment: String? = nil) -> AnyPublisher<Bool, Error> {
        guard let token = accessToken else {
            return Fail(error: URLError(.userAuthenticationRequired))
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(baseURL)/add-to-list/\(movieId)/") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let listId = actionName == "watched" ? 1 : 2
        let requestBody: [String: Any] = [
            "listId": listId
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        } catch {
            return Fail(error: error)
                .eraseToAnyPublisher()
        }
        
        return URLSession.shared.dataTaskPublisher(for: request)
            .map { _ in true }
            .mapError { $0 as Error }
            .eraseToAnyPublisher()
    }
}