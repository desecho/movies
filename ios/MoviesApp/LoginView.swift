import SwiftUI

struct LoginView: View {
    @EnvironmentObject var apiService: APIService
    @State private var username = ""
    @State private var password = ""
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Image("Logo")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 120, height: 120)
                
                Text("MovieMunch")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                VStack(spacing: 15) {
                    TextField("Username", text: $username)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                .padding(.horizontal)
                
                if let errorMessage = apiService.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .font(.caption)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                
                Button(action: {
                    apiService.login(username: username, password: password)
                }) {
                    HStack {
                        if apiService.isLoading {
                            ProgressView()
                                .scaleEffect(0.8)
                        }
                        Text("Login")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                }
                .disabled(username.isEmpty || password.isEmpty || apiService.isLoading)
                .padding(.horizontal)
                
                Spacer()
            }
            .padding()
            .navigationTitle("Welcome")
        }
    }
}

#Preview {
    LoginView()
        .environmentObject(APIService())
}
