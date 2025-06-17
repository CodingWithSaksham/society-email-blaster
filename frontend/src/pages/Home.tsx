
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import Navbar from '@/components/Navbar';
import { useAuth } from '@/contexts/AuthContext';

const Home = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        {/* Hero Section */}
        <section className="bg-gradient-to-r from-brand-blue to-brand-teal text-white py-20">
          <div className="container mx-auto px-6 text-center">
            <h1 className="text-5xl font-bold mb-6">Email Blaster</h1>
            <p className="text-xl mb-8 max-w-2xl mx-auto">
              Create personalized email templates by combining your CSV data with HTML templates. 
              Perfect for email marketing campaigns and mass communications.
            </p>
            {isAuthenticated ? (
              <Link to="/dashboard">
                <Button size="lg" className="bg-white text-brand-blue hover:bg-gray-100">
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <Link to="/login">
                <Button size="lg" className="bg-white text-brand-blue hover:bg-gray-100">
                  Get Started
                </Button>
              </Link>
            )}
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 bg-white">
          <div className="container mx-auto px-6">
            <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">How It Works</h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-gray-50 p-6 rounded-lg shadow-md">
                <div className="text-brand-blue text-2xl font-bold mb-4">1. Upload CSV</div>
                <p className="text-gray-600">Upload your CSV file containing all the data you want to include in your emails.</p>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg shadow-md">
                <div className="text-brand-blue text-2xl font-bold mb-4">2. Upload Template</div>
                <p className="text-gray-600">Upload your HTML email template with placeholders like &#123;&#123;name&#125;&#125; for dynamic content.</p>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg shadow-md">
                <div className="text-brand-blue text-2xl font-bold mb-4">3. Map & Generate</div>
                <p className="text-gray-600">Map CSV columns to your template placeholders and generate personalized emails.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="py-16 bg-gray-100">
          <div className="container mx-auto px-6 text-center">
            <h2 className="text-3xl font-bold mb-6 text-gray-800">Ready to Get Started?</h2>
            <p className="text-xl mb-8 text-gray-600 max-w-2xl mx-auto">
              Sign in with your Google account and start creating personalized emails in minutes.
            </p>
            {!isAuthenticated && (
              <Link to="/login">
                <Button size="lg" className="bg-brand-blue text-white hover:bg-opacity-90">
                  Sign In with Google
                </Button>
              </Link>
            )}
          </div>
        </section>
      </main>

      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-6 text-center">
          <p>© {new Date().getFullYear()} Email Blaster. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
