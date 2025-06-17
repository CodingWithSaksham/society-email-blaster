
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';

const Navbar = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="bg-brand-blue text-white px-6 py-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold">Email Blaster</Link>
        
        <div className="flex space-x-4">
          <Link to="/" className="hover:text-brand-teal transition-colors">
            Home
          </Link>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="hover:text-brand-teal transition-colors">
                Dashboard
              </Link>
              <Button 
                variant="ghost" 
                className="text-white hover:text-brand-teal" 
                onClick={logout}
              >
                Logout
              </Button>
            </>
          ) : (
            <Link to="/login" className="hover:text-brand-teal transition-colors">
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
