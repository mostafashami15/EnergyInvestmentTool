import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useAuth } from './AuthProvider';

/**
 * ProjectList component displays a list of the user's saved projects
 */
const ProjectList = ({ onProjectSelect, onCreateNew }) => {
  const { authFetch, isAuthenticated } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Fetch projects when component mounts and authentication changes
  useEffect(() => {
    if (isAuthenticated) {
      fetchProjects();
    } else {
      setProjects([]);
      setLoading(false);
    }
  }, [isAuthenticated]);

  /**
   * Fetch user's projects from the API
   */
  const fetchProjects = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await authFetch('/api/projects');
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to fetch projects');
      }
      
      const data = await response.json();
      setProjects(data.projects || []);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle project selection
   * @param {string} projectId - ID of selected project
   */
  const handleProjectSelect = async (projectId) => {
    setSelectedProjectId(projectId);
    
    try {
      const response = await authFetch(`/api/projects/${projectId}`);
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to load project');
      }
      
      const projectData = await response.json();
      
      // Call the onProjectSelect callback with the project data
      if (onProjectSelect) {
        onProjectSelect(projectData);
      }
    } catch (err) {
      console.error('Error loading project:', err);
      setError('Failed to load project details');
    }
  };

  /**
   * Handle project deletion
   * @param {string} projectId - ID of project to delete
   */
  const handleDeleteProject = async (projectId) => {
    try {
      const response = await authFetch(`/api/projects/${projectId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to delete project');
      }
      
      // Remove the project from the list
      setProjects(projects.filter(project => project.id !== projectId));
      
      // Clear selected project if it was deleted
      if (selectedProjectId === projectId) {
        setSelectedProjectId(null);
      }
      
      // Clear delete confirmation
      setDeleteConfirm(null);
    } catch (err) {
      console.error('Error deleting project:', err);
      setError('Failed to delete project');
    }
  };

  /**
   * Format date string for display
   * @param {string} dateString - ISO date string
   * @returns {string} Formatted date
   */
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">My Projects</h2>
        
        {/* Create new project button */}
        <button
          onClick={onCreateNew}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          New Project
        </button>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {/* Loading state */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : projects.length === 0 ? (
        // Empty state
        <div className="bg-gray-50 rounded p-8 text-center">
          <p className="text-gray-600 mb-4">You don't have any saved projects yet.</p>
          <button
            onClick={onCreateNew}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          >
            Create Your First Project
          </button>
        </div>
      ) : (
        // Project list
        <div className="overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="bg-gray-50 text-left">
                <th className="px-4 py-2 text-gray-600">Name</th>
                <th className="px-4 py-2 text-gray-600">Location</th>
                <th className="px-4 py-2 text-gray-600">Last Updated</th>
                <th className="px-4 py-2 text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {projects.map(project => (
                <tr 
                  key={project.id} 
                  className={`border-b hover:bg-gray-50 ${
                    selectedProjectId === project.id ? 'bg-blue-50' : ''
                  }`}
                >
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-800">{project.name}</div>
                    {project.description && (
                      <div className="text-sm text-gray-500 truncate max-w-xs">
                        {project.description}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {project.location_lat && project.location_lon ? (
                      <span className="text-sm">
                        {project.location_lat.toFixed(6)}, {project.location_lon.toFixed(6)}
                      </span>
                    ) : (
                      <span className="text-sm text-gray-500">No location</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {formatDate(project.updated_at)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex space-x-2">
                      {/* Load project button */}
                      <button
                        onClick={() => handleProjectSelect(project.id)}
                        className="bg-blue-100 hover:bg-blue-200 text-blue-700 py-1 px-3 rounded text-sm"
                      >
                        Load
                      </button>
                      
                      {/* Delete button/confirmation */}
                      {deleteConfirm === project.id ? (
                        <div className="flex space-x-1">
                          <button
                            onClick={() => handleDeleteProject(project.id)}
                            className="bg-red-500 hover:bg-red-600 text-white py-1 px-2 rounded text-sm"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(null)}
                            className="bg-gray-200 hover:bg-gray-300 text-gray-700 py-1 px-2 rounded text-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setDeleteConfirm(project.id)}
                          className="bg-gray-100 hover:bg-gray-200 text-gray-700 py-1 px-3 rounded text-sm"
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

ProjectList.propTypes = {
  onProjectSelect: PropTypes.func,
  onCreateNew: PropTypes.func
};

export default ProjectList;