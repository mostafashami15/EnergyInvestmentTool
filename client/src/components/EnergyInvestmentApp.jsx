import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthProvider';
import SolarMapComponent from './SolarMapComponent';
import SystemParameterForm from './SystemParameterForm';
import ResultsDashboard from './ResultsDashboard';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import ProjectList from './ProjectList';
import SaveProjectForm from './SaveProjectForm';
import SensitivityAnalysisVisualization from './SensitivityAnalysisVisualization';

const EnergyInvestmentApp = () => {
  // Authentication context
  const { isAuthenticated, user, logout } = useAuth();

  // Modal states
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [showProjectList, setShowProjectList] = useState(false);
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [showAdminPanel, setShowAdminPanel] = useState(false);

  // Project management state
  const [selectedProject, setSelectedProject] = useState(null);
  
  // Application state
  const [location, setLocation] = useState({ lat: 39.7392, lon: -104.9903 }); // Default: Denver
  const [projectParams, setProjectParams] = useState({});
  const [calculationResults, setCalculationResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Sensitivity analysis state
  const [sensitivityData, setSensitivityData] = useState(null);
  const [sensitivityLoading, setSensitivityLoading] = useState(false);

  // Fetch calculations from real API
  const fetchCalculations = async (parameters) => {
    setLoading(true);
    setError(null);
    setProjectParams(parameters); // Save parameters for project saving
    
    try {
      const response = await fetch('/api/calculate-all', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latitude: location.lat,
          longitude: location.lon,
          systemCapacity: parameters.systemCapacity,
          moduleType: parameters.moduleType,
          arrayType: parameters.arrayType,
          losses: parameters.losses,
          tilt: parameters.tilt,
          azimuth: parameters.azimuth,
          dataSource: parameters.dataSource,
          systemCostPerWatt: parameters.systemCostPerWatt,
          incentivePercent: parameters.incentivePercent,
          loanPercent: parameters.loanPercent || 0,
          loanTerm: parameters.loanTerm || 20,
          loanRate: parameters.loanRate || 5.5,
          analysisYears: parameters.analysisYears || 25,
          includeSensitivity: true
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to calculate results');
      }
      
      const data = await response.json();
      setCalculationResults(data);
      
      // Fetch sensitivity analysis data
      fetchSensitivityData();
    } catch (err) {
      console.error('Calculation error:', err);
      setError(err.message || 'Failed to calculate results. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch sensitivity analysis data
  const fetchSensitivityData = async () => {
    setSensitivityLoading(true);
    try {
      const baseParams = {
        ...projectParams,
        latitude: location.lat,
        longitude: location.lon,
      };
      
      const response = await fetch('/api/sensitivity-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          base_params: baseParams,
          analysis_type: 'tornado'
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to calculate sensitivity analysis');
      }
      
      const data = await response.json();
      setSensitivityData(data);
    } catch (err) {
      console.error('Sensitivity analysis error:', err);
      // Don't set main error - just log it
    } finally {
      setSensitivityLoading(false);
    }
  };
  
  // Handle parameter change for custom sensitivity scenario
  const handleParameterChange = async (customParams) => {
    setSensitivityLoading(true);
    try {
      const baseParams = {
        ...projectParams,
        latitude: location.lat,
        longitude: location.lon,
      };
      
      const response = await fetch('/api/sensitivity-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          base_params: baseParams,
          custom_params: customParams,
          analysis_type: 'custom'
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to calculate custom scenario');
      }
      
      const data = await response.json();
      setSensitivityData(prev => ({
        ...prev,
        customScenario: data.custom_scenario,
        base_case: data.base_case
      }));
    } catch (err) {
      console.error('Custom scenario error:', err);
    } finally {
      setSensitivityLoading(false);
    }
  };

  // Handle location selection from map
  const handleLocationSelect = (newLocation) => {
    setLocation(newLocation);
    // Clear previous calculation results when location changes
    setCalculationResults(null);
    setSensitivityData(null);
  };
  
  // Handle form submission
  const handleCalculate = (formValues) => {
    fetchCalculations(formValues);
  };
  
  // Handle project selection
  const handleProjectSelect = (project) => {
    setSelectedProject(project);
    
    // Update app state with project data
    if (project.location_lat && project.location_lon) {
      setLocation({
        lat: project.location_lat,
        lon: project.location_lon
      });
    }
    
    if (project.parameters) {
      setProjectParams(project.parameters);
    }
    
    if (project.results) {
      setCalculationResults(project.results);
    }
    
    // Close project list modal
    setShowProjectList(false);
  };
  
  // Handle saving a project
  const handleSaveProject = (savedProject) => {
    setSelectedProject(savedProject);
    setShowSaveForm(false);
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header with auth buttons */}
      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Energy Investment Decision Support System</h1>
          
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <button 
                  onClick={() => setShowProjectList(true)}
                  className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-3 rounded"
                >
                  My Projects
                </button>
                <span className="text-sm">Welcome, {user.username}</span>
                <button 
                  onClick={logout}
                  className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-3 rounded"
                >
                  Logout
                </button>
                {/* Add admin panel button if needed */}
                <button 
                  onClick={() => setShowAdminPanel(true)}
                  className="bg-purple-500 hover:bg-purple-700 text-white py-1 px-3 rounded"
                >
                  Admin
                </button>
              </>
            ) : (
              <>
                <button 
                  onClick={() => setShowLoginForm(true)}
                  className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-3 rounded"
                >
                  Login
                </button>
                <button 
                  onClick={() => setShowRegisterForm(true)}
                  className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-3 rounded"
                >
                  Register
                </button>
              </>
            )}
          </div>
        </div>
      </header>
      
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Analyze renewable energy potential and financial returns</h2>
          <p className="text-gray-600 mt-2">
            Select a location, configure your system, and calculate the results
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left column: Map */}
          <div className="lg:col-span-2">
            <SolarMapComponent 
              onLocationSelect={handleLocationSelect} 
              initialLocation={location} 
            />
          </div>
          
          {/* Right column: Parameters form */}
          <div>
            <SystemParameterForm 
              onCalculate={handleCalculate} 
              loading={loading}
              initialValues={projectParams}
            />
            
            {/* Project Save Button (when authenticated and has results) */}
            {isAuthenticated && calculationResults && (
              <div className="mt-4">
                <button
                  onClick={() => setShowSaveForm(true)}
                  className="w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                >
                  {selectedProject ? 'Update Project' : 'Save Project'}
                </button>
              </div>
            )}
          </div>
          
          {/* Full width: Results dashboard */}
          <div className="lg:col-span-3 mt-8">
            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              </div>
            )}
            
            {loading && (
              <div className="flex justify-center items-center p-12">
                <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
                <span className="ml-4 text-lg font-medium text-gray-700">Calculating results...</span>
              </div>
            )}
            
            {!loading && calculationResults && (
              <>
                <ResultsDashboard results={calculationResults} location={location} />
                
                {/* Sensitivity Analysis Section */}
                <div className="mt-12">
                  <h2 className="text-2xl font-bold mb-4">Sensitivity Analysis</h2>
                  <SensitivityAnalysisVisualization
                    sensitivityData={sensitivityData}
                    onParameterChange={handleParameterChange}
                    baselineValues={projectParams}
                    loading={sensitivityLoading}
                  />
                </div>
              </>
            )}
            
            {!loading && !calculationResults && !error && (
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1V9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-blue-700">
                      Select a location on the map and enter system parameters, then click "Calculate Results" to analyze renewable energy potential.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
      
      <footer className="mt-auto pt-8 pb-4 border-t border-gray-200 text-center text-gray-500 text-sm">
        <p>Energy Investment Decision Support System &copy; {new Date().getFullYear()}</p>
        <p className="mt-1">Powered by NREL and NASA POWER APIs</p>
      </footer>
      
      {/* Modal overlays for authentication and project management */}
      {showLoginForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-10">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-4 flex justify-end">
              <button onClick={() => setShowLoginForm(false)} className="text-gray-500 text-2xl">&times;</button>
            </div>
            <LoginForm onSuccess={() => setShowLoginForm(false)} />
          </div>
        </div>
      )}
      
      {showRegisterForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-10">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-4 flex justify-end">
              <button onClick={() => setShowRegisterForm(false)} className="text-gray-500 text-2xl">&times;</button>
            </div>
            <RegisterForm onSuccess={() => setShowRegisterForm(false)} />
          </div>
        </div>
      )}
      
      {showProjectList && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-10">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full">
            <div className="p-4 flex justify-end">
              <button onClick={() => setShowProjectList(false)} className="text-gray-500 text-2xl">&times;</button>
            </div>
            <ProjectList 
              onProjectSelect={handleProjectSelect} 
              onCreateNew={() => {
                setSelectedProject(null);
                setShowProjectList(false);
              }}
            />
          </div>
        </div>
      )}
      
      {showSaveForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-10">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
            <div className="p-4 flex justify-end">
              <button onClick={() => setShowSaveForm(false)} className="text-gray-500 text-2xl">&times;</button>
            </div>
            <SaveProjectForm 
              projectData={projectParams}
              location={location}
              calculationResults={calculationResults}
              existingProject={selectedProject}
              onSuccess={handleSaveProject}
              onCancel={() => setShowSaveForm(false)}
            />
          </div>
        </div>
      )}
      
      {showAdminPanel && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-10">
          <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full h-5/6 overflow-auto">
            <div className="p-4 flex justify-end">
              <button onClick={() => setShowAdminPanel(false)} className="text-gray-500 text-2xl">&times;</button>
            </div>
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-6">Admin Panel</h2>
              {/* Import and render the CacheMonitoring component */}
              {/* <CacheMonitoring isAdmin={true} /> */}
              <p className="text-gray-700">
                Admin functionality is coming soon. This will include cache management and system monitoring.
              </p>
              <p className="mt-4">
                <button onClick={() => setShowAdminPanel(false)} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                  Close Panel
                </button>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnergyInvestmentApp;