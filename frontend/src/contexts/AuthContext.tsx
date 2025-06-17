import React, { createContext, useContext, useState, useEffect } from "react";
import {
  GoogleOAuthProvider,
  GoogleLogin,
  googleLogout,
} from "@react-oauth/google";
import Cookies from "js-cookie";

// Define the shape of our auth context
interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
  login: (userData: any) => void;
  logout: () => void;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  user: null,
  login: () => {},
  logout: () => {},
});

const GOOGLE_CLIENT_ID ="";

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<any | null>(null);

  // Check for existing session on component mount
  useEffect(() => {
    const userFromCookie = Cookies.get();
    if (userFromCookie) {
      try {
        const parsedUser = JSON.parse(userFromCookie);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error("Failed to parse user data from cookie", error);
        Cookies.remove("user");
      }
    }
  }, []);

  const login = (userData: any) => {
    setUser(userData);
    setIsAuthenticated(true);
    // Store user data in a cookie
    Cookies.set("user", JSON.stringify(userData), { expires: 7 }); // Expires in 7 days
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    Cookies.remove("user");
    googleLogout();
  };

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
        {children}
      </AuthContext.Provider>
    </GoogleOAuthProvider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);
