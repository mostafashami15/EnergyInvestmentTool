import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useAuth } from './AuthProvider';

/**
 * SaveProjectForm component provides a form for saving or updating projects
 */
const SaveProjectForm = ({ 
  projectData,
  location,
  calculationResults,
  onSuccess,
  onCancel,
  existingProject = null
}) => {
  const { authFetch, isAuthenticated } = useAuth();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Set initial form values when editing an existing project
  useEffect(() => {
    if (existingProject) {
      setName(existingProject.name || '');
      setDescription(existingProject.description || '');
    }
  }, [existingProject]);

  // Determine if we're editing or creating new
  const isEditing = Boolean(existingProject);

  /**
   * Handle form submission
   * @param {Event} e - Form event
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSaveSuccess(false);
    
    // Basic validation
    if (!name.trim()) {
      setError('Please enter a project name');
      return;
    }
    
    // Must be authenticated to save
    if (!isAuthenticated) {
      setError('You must be logged in to save projects');
      return;
    }
    
    // Must have location data
    if (!location || !location.lat || !location.lon) {
      setError('Location data is required');
      return;
    }

    setLoading(true);
    
    try {
      const endpoint = isEditing
        ? `/api/projects/${existingProject.id}`
        : '/api/projects';
      
      const method = isEditing ? 'PUT' : 'POST';
      
      const projectPayload = {
        name,
        description,
        location_lat: location.lat,
        location_lon: location.lon,
        parameters: projectData,
        results: calculationResults
      };
      
      const response = await authFetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(projectPayload)
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to save project');
      }
      
      const data = await response.json();
      
      setSaveSuccess(true);
      
      // Call the success callback with the saved project data
      if (onSuccess) {
        onSuccess(data);
      }
    } catch (err) {
      console.error('Error saving project:', err);
      setError(err.message || 'Failed to save project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-6">
        {isEditing ? 'Update Project' : 'Save Project'}
      </h2>
      
      {/* Success message */}
      {saveSuccess && (
        <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
          Project saved successfully!
        </div>
      )}
      
      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        {/* Project name */}
        <div className="mb-4">
          <label 
            className="block text-gray-700 text-sm font-bold mb-2" 
            htmlFor="projectName"
          >
            Project Name <span className="text-red-500">*</span>
          </label>
          <input
            id="projectName"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="Enter project name"
            disabled={loading}
            required
          />
        </div>
        
        {/* Project description */}
        <div className="mb-6">
          <label 
            className="block text-gray-700 text-sm font-bold mb-2" 
            htmlFor="projectDescription"
          >
            Description
          </label>
          <textarea
            id="projectDescription"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-24"
            placeholder="Enter project description (optional)"
            disabled={loading}
          />
        </div>
        
        {/* Location summary */}
        <div className="mb-6 bg-gray-50 p-3 rounded">
          <h3 className="text-sm font-bold text-gray-700 mb-2">Project Location</h3>
          {location && location.lat && location.lon ? (
            <p className="text-gray-700">
              Latitude: {location.lat.toFixed(6)}, Longitude: {location.lon.toFixed(6)}
            </p>
          ) : (
            <p className="text-red-500">No location selected</p>
          )}
        </div>
        
        {/* Data summary */}
        <div className="mb-6 bg-gray-50 p-3 rounded">
          <h3 className="text-sm font-bold text-gray-700 mb-2">Project Data</h3>
          {projectData ? (
            <div className="text-gray-700 text-sm">
              <p>System Size: {projectData.systemCapacity || projectData.system_capacity || 'N/A'} kW</p>
              <p>Parameters: {Object.keys(projectData).length} configuration values</p>
            </div>
          ) : (
            <p className="text-red-500">No project data available</p>
          )}
          
          {calculationResults ? (
            <div className="mt-2 text-gray-700 text-sm">
              <p>Calculation results included</p>
            </div>
          ) : (
            <p className="text-yellow-500 text-sm mt-2">No calculation results available</p>
          )}
        </div>
        
        {/* Form actions */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-100 focus:outline-none focus:shadow-outline"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            disabled={loading}
          >
            {loading ? 'Saving...' : isEditing ? 'Update Project' : 'Save Project'}
          </button>
        </div>
      </form>
    </div>
  );
};

SaveProjectForm.propTypes = {
  projectData: PropTypes.object.isRequired,
  location: PropTypes.shape({
    lat: PropTypes.number,
    lon: PropTypes.number
  }),
  calculationResults: PropTypes.object,
  onSuccess: PropTypes.func,
  onCancel: PropTypes.func,
  existingProject: PropTypes.object
};

export default SaveProjectForm;