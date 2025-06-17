
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import { useAuth } from '@/contexts/AuthContext';

const Dashboard = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      <main className="flex-1 container mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold mb-8 text-gray-800">Dashboard</h1>
        
        <div className="grid md:grid-cols-2 gap-8">
          <Card className="shadow-md hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-xl text-brand-blue">Create New Template</CardTitle>
              <CardDescription>Upload CSV and HTML template to create personalized emails</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="mb-4 text-gray-600">
                Start a new project by uploading your CSV data file and HTML template with placeholders.
              </p>
              <Link to="/upload">
                <Button className="w-full bg-brand-blue hover:bg-opacity-90">
                  New Project
                </Button>
              </Link>
            </CardContent>
          </Card>
          
          <Card className="shadow-md hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-xl text-brand-blue">Your Templates</CardTitle>
              <CardDescription>View and manage your saved templates</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="mb-4 text-gray-600">
                Access your previously created templates and generated email content.
              </p>
              <Button className="w-full" variant="outline">
                View Templates
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
