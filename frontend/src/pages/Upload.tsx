
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import Navbar from '@/components/Navbar';
import { useAuth } from '@/contexts/AuthContext';
import Papa from 'papaparse';

const Upload = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [htmlFile, setHtmlFile] = useState<File | null>(null);
  const [csvData, setCsvData] = useState<any[]>([]);
  const [csvColumns, setCsvColumns] = useState<string[]>([]);
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [placeholders, setPlaceholders] = useState<string[]>([]);
  const [placeholderMappings, setPlaceholderMappings] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState('upload');
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [previewIndex, setPreviewIndex] = useState(0);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Extract placeholders from HTML content (matches {{anytext}})
  const extractPlaceholders = (html: string) => {
    const regex = /\{\{([^}]+)\}\}/g;
    const matches = [];
    let match;
    
    while ((match = regex.exec(html)) !== null) {
      matches.push(match[0]); // The full placeholder with brackets
    }
    
    return matches;
  };

  // Handle CSV file upload
  const handleCsvUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setCsvFile(file);
      
      Papa.parse(file, {
        header: true,
        complete: (results) => {
          setCsvData(results.data);
          // Extract column headers
          if (results.data.length > 0) {
            setCsvColumns(Object.keys(results.data[0]));
          }
        },
        error: (error) => {
          console.error('Error parsing CSV:', error);
        }
      });
    }
  };

  // Handle HTML file upload
  const handleHtmlUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setHtmlFile(file);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setHtmlContent(content);
        
        // Extract placeholders
        const extractedPlaceholders = extractPlaceholders(content);
        setPlaceholders(extractedPlaceholders);
        
        // Initialize mappings
        const initialMappings: Record<string, string> = {};
        extractedPlaceholders.forEach(placeholder => {
          initialMappings[placeholder] = '';
        });
        setPlaceholderMappings(initialMappings);
      };
      reader.readAsText(file);
    }
  };

  // Handle placeholder mapping changes
  const handleMappingChange = (placeholder: string, columnName: string) => {
    setPlaceholderMappings(prev => ({
      ...prev,
      [placeholder]: columnName
    }));
  };

  // Generate preview with mapped placeholders
  const generatePreview = () => {
    if (csvData.length === 0 || !htmlContent) return;
    
    let preview = htmlContent;
    const dataRow = csvData[previewIndex];
    
    Object.entries(placeholderMappings).forEach(([placeholder, columnName]) => {
      if (columnName && dataRow[columnName]) {
        preview = preview.replace(
          new RegExp(escapeRegExp(placeholder), 'g'), 
          dataRow[columnName]
        );
      }
    });
    
    setPreviewHtml(preview);
    setActiveTab('preview');
  };

  // Utility to escape special regex characters
  const escapeRegExp = (string: string) => {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  };

  // Go to next/previous preview
  const navigatePreview = (direction: 'next' | 'prev') => {
    let newIndex = previewIndex;
    
    if (direction === 'next' && previewIndex < csvData.length - 1) {
      newIndex += 1;
    } else if (direction === 'prev' && previewIndex > 0) {
      newIndex -= 1;
    }
    
    setPreviewIndex(newIndex);
    
    // Regenerate preview with new index
    let preview = htmlContent;
    const dataRow = csvData[newIndex];
    
    Object.entries(placeholderMappings).forEach(([placeholder, columnName]) => {
      if (columnName && dataRow[columnName]) {
        preview = preview.replace(
          new RegExp(escapeRegExp(placeholder), 'g'), 
          dataRow[columnName]
        );
      }
    });
    
    setPreviewHtml(preview);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      <main className="flex-1 container mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold mb-8 text-gray-800">Create Email Template</h1>
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="upload">Upload Files</TabsTrigger>
            <TabsTrigger 
              value="map" 
              disabled={!csvFile || !htmlFile || placeholders.length === 0}
            >
              Map Fields
            </TabsTrigger>
            <TabsTrigger 
              value="preview" 
              disabled={!csvData.length || Object.values(placeholderMappings).some(val => !val)}
            >
              Preview
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="upload" className="mt-6">
            <div className="grid md:grid-cols-2 gap-8">
              <Card>
                <CardHeader>
                  <CardTitle>Upload CSV Data</CardTitle>
                  <CardDescription>Upload the CSV file containing your data</CardDescription>
                </CardHeader>
                <CardContent>
                  <Label htmlFor="csv-upload">CSV File</Label>
                  <Input 
                    id="csv-upload" 
                    type="file" 
                    accept=".csv" 
                    onChange={handleCsvUpload}
                    className="mt-2"
                  />
                  
                  {csvFile && (
                    <div className="mt-4">
                      <p className="text-sm text-green-600">✓ {csvFile.name} uploaded</p>
                      {csvColumns.length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm font-medium">Detected columns:</p>
                          <div className="text-sm text-gray-600 mt-1">
                            {csvColumns.join(', ')}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Upload HTML Template</CardTitle>
                  <CardDescription>Upload your HTML email template with placeholders</CardDescription>
                </CardHeader>
                <CardContent>
                  <Label htmlFor="html-upload">HTML File</Label>
                  <Input 
                    id="html-upload" 
                    type="file" 
                    accept=".html,.htm" 
                    onChange={handleHtmlUpload}
                    className="mt-2"
                  />
                  
                  {htmlFile && (
                    <div className="mt-4">
                      <p className="text-sm text-green-600">✓ {htmlFile.name} uploaded</p>
                      {placeholders.length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm font-medium">Detected placeholders:</p>
                          <div className="text-sm text-gray-600 mt-1">
                            {placeholders.join(', ')}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
            
            {csvFile && htmlFile && placeholders.length > 0 && (
              <div className="mt-6 flex justify-end">
                <Button 
                  className="bg-brand-blue hover:bg-opacity-90"
                  onClick={() => setActiveTab('map')}
                >
                  Continue to Mapping
                </Button>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="map" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Map Placeholders to CSV Columns</CardTitle>
                <CardDescription>
                  For each placeholder in your HTML template, select the corresponding CSV column
                </CardDescription>
              </CardHeader>
              <CardContent>
                {placeholders.length > 0 ? (
                  <div className="space-y-4">
                    {placeholders.map((placeholder, index) => (
                      <div key={index} className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
                        <div>
                          <Label className="text-gray-700">Placeholder: {placeholder}</Label>
                        </div>
                        <div>
                          <select
                            className="w-full p-2 border rounded-md"
                            value={placeholderMappings[placeholder] || ''}
                            onChange={(e) => handleMappingChange(placeholder, e.target.value)}
                          >
                            <option value="">Select CSV column</option>
                            {csvColumns.map((column, i) => (
                              <option key={i} value={column}>
                                {column}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    ))}
                    
                    <div className="mt-6 flex justify-end">
                      <Button 
                        className="bg-brand-blue hover:bg-opacity-90"
                        onClick={generatePreview}
                        disabled={Object.values(placeholderMappings).some(val => !val)}
                      >
                        Generate Preview
                      </Button>
                    </div>
                  </div>
                ) : (
                  <p>No placeholders detected in the HTML template.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="preview" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Preview Generated Email</CardTitle>
                <CardDescription>
                  Preview {previewIndex + 1} of {csvData.length} entries
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-white border rounded-md p-4 overflow-auto max-h-[60vh]">
                  <div dangerouslySetInnerHTML={{ __html: previewHtml }} />
                </div>
                
                <div className="mt-6 flex justify-between">
                  <Button 
                    variant="outline" 
                    onClick={() => navigatePreview('prev')}
                    disabled={previewIndex === 0}
                  >
                    Previous
                  </Button>
                  
                  <div className="flex space-x-2">
                    <Button
                      className="bg-brand-teal hover:bg-opacity-90"
                    >
                      Download All
                    </Button>
                    <Button
                      className="bg-brand-blue hover:bg-opacity-90"
                    >
                      Save Template
                    </Button>
                  </div>
                  
                  <Button 
                    variant="outline" 
                    onClick={() => navigatePreview('next')}
                    disabled={previewIndex === csvData.length - 1}
                  >
                    Next
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Upload;
