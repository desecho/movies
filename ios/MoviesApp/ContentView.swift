import SwiftUI

struct ContentView: View {
    @StateObject private var apiService = APIService()
    
    var body: some View {
        Group {
            if apiService.isAuthenticated && !apiService.shouldShowLogin {
                TabView {
                    MovieListView(listType: .watched)
                        .tabItem {
                            Image(systemName: "eye.fill")
                            Text("Watched")
                        }
                    
                    MovieListView(listType: .toWatch)
                        .tabItem {
                            Image(systemName: "bookmark.fill")
                            Text("To Watch")
                        }
                    
                    SearchView()
                        .tabItem {
                            Image(systemName: "magnifyingglass")
                            Text("Search")
                        }
                }
            } else {
                LoginView()
            }
        }
        .environmentObject(apiService)
    }
}

#Preview {
    ContentView()
}