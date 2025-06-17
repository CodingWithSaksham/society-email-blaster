
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '@/contexts/AuthContext';

const Login = () => {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleGoogleSuccess = (credentialResponse: any) => {
    // In a real app, you would verify this token on your backend
    const userData = {
      tokenId: credentialResponse.credential,
      // You can decode the JWT to get basic user info, but this should be done securely
    };
    login(userData);
    navigate('/dashboard');
  };

  const handleGoogleError = () => {
    console.error('Google login failed');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-brand-blue">Email Blaster</CardTitle>
          <CardDescription>Sign in to access your email templating tool</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center space-y-4">
          <p className="text-center mb-4">
            Create personalized email templates by combining your CSV data with HTML templates
          </p>
          <div className="w-full flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              useOneTap
            />
          </div>
        </CardContent>
        <CardFooter className="text-center text-sm text-gray-500">
          By signing in, you agree to our Terms of Service and Privacy Policy
        </CardFooter>
      </Card>
    </div>
  );
};

export default Login;
