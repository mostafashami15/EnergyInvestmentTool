import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import { useAuth } from './AuthProvider';

/**
 * CacheMonitoring component provides an admin interface for monitoring
 * the caching system's performance and managing cache settings.
 */
const CacheMonitoring = ({ isAdmin = false }) => {
  const { authFetch, isAuthenticated } = useAuth();
  const [cacheStats, setCacheStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAction, setSelectedAction] = useState(null);
  const [actionTier, setActionTier] = useState('all');
  const [actionNamespace, setActionNamespace] = useState('');
  const [actionSuccess, setActionSuccess] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(0);
  const [refreshTimer, setRefreshTimer] = useState(null);

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];
  
  // Format bytes to human-readable size
  const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };
  
  // Format percentage
  const formatPercent = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // Fetch cache statistics
  const fetchCacheStats = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authFetch('/api/admin/cache/stats');
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to fetch cache statistics');
      }
      
      const data = await response.json();
      setCacheStats(data);
    } catch (err) {
      console.error('Error fetching cache statistics:', err);
      setError(err.message || 'Failed to fetch cache statistics');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle cache actions (clear, invalidate, cleanup)
  const handleCacheAction = async () => {
    if (!selectedAction) return;
    
    setLoading(true);
    setActionSuccess(null);
    
    try {
      let endpoint = '/api/admin/cache/';
      let method = 'POST';
      let body = {};
      
      switch (selectedAction) {
        case 'clear':
          endpoint += 'clear';
          body = { tier: actionTier === 'all' ? null : actionTier };
          break;
        case 'invalidate':
          endpoint += 'invalidate';
          body = { 
            namespace: actionNamespace, 
            key_components: null // Invalidate entire namespace
          };
          break;
        case 'cleanup':
          endpoint += 'cleanup';
          break;
        default:
          throw new Error('Invalid action');
      }
      
      const response = await authFetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to perform cache action');
      }
      
      const data = await response.json();
      setActionSuccess({
        action: selectedAction,
        result: data
      });
      
      // Refresh stats after action
      fetchCacheStats();
    } catch (err) {
      console.error('Error performing cache action:', err);
      setError(err.message || 'Failed to perform cache action');
    } finally {
      setLoading(false);
    }
  };
  
  // Toggle automatic refresh
  const toggleRefresh = (interval) => {
    if (refreshTimer) {
      clearInterval(refreshTimer);
      setRefreshTimer(null);
      setRefreshInterval(0);
    } else if (interval > 0) {
      setRefreshInterval(interval);
      const timer = setInterval(() => {
        fetchCacheStats();
      }, interval * 1000);
      setRefreshTimer(timer);
    }
  };
  
  // Clean up interval on unmount
  useEffect(() => {
    return () => {
      if (refreshTimer) {
        clearInterval(refreshTimer);
      }
    };
  }, [refreshTimer]);
  
  // Fetch stats on component mount
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      fetchCacheStats();
    }
  }, [isAuthenticated, isAdmin]);

  // Prepare cache tier data for charts
  const prepareTierData = () => {
    if (!cacheStats || !cacheStats.disk_cache || !cacheStats.disk_cache.tiers) {
      return [];
    }
    
    return Object.entries(cacheStats.disk_cache.tiers).map(([tier, stats]) => ({
      tier,
      count: stats.count,
      size: stats.size_bytes,
      hits: stats.hits,
      misses: stats.misses,
      hitRatio: stats.hit_ratio,
      inserts: stats.inserts,
      evictions: stats.evictions,
      ttl: stats.ttl_seconds
    }));
  };
  
  // Prepare hit ratio data for pie chart
  const prepareHitRatioData = (cacheType = 'disk') => {
    if (!cacheStats) return [];
    
    if (cacheType === 'memory') {
      const memory = cacheStats.memory_cache;
      return [
        { name: 'Hits', value: memory.hits },
        { name: 'Misses', value: memory.misses }
      ];
    } else {
      const disk = cacheStats.disk_cache.total;
      return [
        { name: 'Hits', value: disk.hits },
        { name: 'Misses', value: disk.misses }
      ];
    }
  };

  // If not an admin or not authenticated, show restricted access message
  if (!isAdmin || !isAuthenticated) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Cache Monitoring</h2>
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          <p className="font-bold">Restricted Access</p>
          <p>You need administrator privileges to access this feature.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Cache Monitoring</h2>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => fetchCacheStats()}
            className="bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
          
          <div className="relative inline-block">
            <select
              value={refreshInterval}
              onChange={(e) => toggleRefresh(parseInt(e.target.value))}
              className="block appearance-none bg-white border border-gray-300 hover:border-gray-400 px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="0">Auto Refresh</option>
              <option value="5">5 seconds</option>
              <option value="15">15 seconds</option>
              <option value="30">30 seconds</option>
              <option value="60">1 minute</option>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
              <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {/* Success message */}
      {actionSuccess && (
        <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
          <p className="font-bold">
            {actionSuccess.action === 'clear' && 'Cache Cleared'}
            {actionSuccess.action === 'invalidate' && 'Cache Invalidated'}
            {actionSuccess.action === 'cleanup' && 'Expired Entries Removed'}
          </p>
          <p>
            {actionSuccess.result.count} entries affected.
          </p>
        </div>
      )}
      
      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}
      
      {!loading && cacheStats && (
        <div className="space-y-6">
          {/* Overview Section */}
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="text-lg font-semibold mb-3">Cache Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded shadow">
                <h4 className="text-sm font-medium text-gray-500">Memory Cache</h4>
                <p className="text-2xl font-bold">{cacheStats.memory_cache.size} / {cacheStats.memory_cache.max_size}</p>
                <p className="text-sm text-gray-500">Items in memory</p>
                <div className="mt-2">
                  <p className="text-sm">
                    Hit Ratio: <span className="font-semibold">{formatPercent(cacheStats.memory_cache.hit_ratio)}</span>
                  </p>
                </div>
              </div>
              
              <div className="bg-white p-4 rounded shadow">
                <h4 className="text-sm font-medium text-gray-500">Disk Cache</h4>
                <p className="text-2xl font-bold">{cacheStats.disk_cache.total.count}</p>
                <p className="text-sm text-gray-500">Total entries</p>
                <div className="mt-2">
                  <p className="text-sm">
                    Size: <span className="font-semibold">{formatBytes(cacheStats.disk_cache.total.size_bytes)}</span>
                  </p>
                </div>
              </div>
              
              <div className="bg-white p-4 rounded shadow">
                <h4 className="text-sm font-medium text-gray-500">Hit Ratio</h4>
                <p className="text-2xl font-bold">{formatPercent(cacheStats.disk_cache.total.hit_ratio)}</p>
                <p className="text-sm text-gray-500">Overall cache performance</p>
                <div className="mt-2">
                  <p className="text-sm">
                    Hits: <span className="font-semibold">{cacheStats.disk_cache.total.hits}</span>, 
                    Misses: <span className="font-semibold">{cacheStats.disk_cache.total.misses}</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Charts Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Hit Ratio Pie Chart */}
            <div className="bg-white p-4 rounded shadow">
              <h3 className="text-lg font-semibold mb-3">Hit Ratio</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={prepareHitRatioData('disk')}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({name, percent}) => `${name}: ${(percent * 100).toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {prepareHitRatioData('disk').map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => value.toLocaleString()} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            {/* Cache Tiers Bar Chart */}
            <div className="bg-white p-4 rounded shadow">
              <h3 className="text-lg font-semibold mb-3">Cache Tiers</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={prepareTierData()}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="tier" />
                    <YAxis />
                    <Tooltip formatter={(value) => value.toLocaleString()} />
                    <Legend />
                    <Bar dataKey="count" name="Entries" fill="#0088FE" />
                    <Bar dataKey="hits" name="Hits" fill="#00C49F" />
                    <Bar dataKey="misses" name="Misses" fill="#FF8042" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
          
          {/* Cache Tier Details */}
          <div className="bg-white p-4 rounded shadow">
            <h3 className="text-lg font-semibold mb-3">Cache Tier Details</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tier
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Entries
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Size
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Hit Ratio
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Hits/Misses
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      TTL
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {Object.entries(cacheStats.disk_cache.tiers).map(([tier, stats]) => (
                    <tr key={tier}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{tier}</div>
                        <div className="text-xs text-gray-500">{stats.description}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {stats.count.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatBytes(stats.size_bytes)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatPercent(stats.hit_ratio)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {stats.hits.toLocaleString()} / {stats.misses.toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {stats.ttl_seconds >= 86400
                          ? `${Math.floor(stats.ttl_seconds / 86400)} days`
                          : stats.ttl_seconds >= 3600
                          ? `${Math.floor(stats.ttl_seconds / 3600)} hours`
                          : `${Math.floor(stats.ttl_seconds / 60)} minutes`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Cache Management Section */}
          <div className="bg-white p-4 rounded shadow">
            <h3 className="text-lg font-semibold mb-3">Cache Management</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border rounded">
                <h4 className="font-medium mb-2">Clear Cache</h4>
                <p className="text-sm text-gray-600 mb-4">
                  Remove all entries from a specific cache tier or the entire cache.
                </p>
                
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tier
                  </label>
                  <select
                    value={actionTier}
                    onChange={(e) => setActionTier(e.target.value)}
                    className="block w-full border border-gray-300 rounded px-3 py-2"
                  >
                    <option value="all">All Tiers</option>
                    {Object.keys(cacheStats.disk_cache.tiers).map(tier => (
                      <option key={tier} value={tier}>{tier}</option>
                    ))}
                  </select>
                </div>
                
                <button
                  onClick={() => {
                    setSelectedAction('clear');
                    handleCacheAction();
                  }}
                  className="w-full bg-red-500 hover:bg-red-600 text-white py-2 px-3 rounded"
                  disabled={loading}
                >
                  Clear Cache
                </button>
              </div>
              
              <div className="p-4 border rounded">
                <h4 className="font-medium mb-2">Invalidate Namespace</h4>
                <p className="text-sm text-gray-600 mb-4">
                  Remove all entries for a specific namespace (e.g., "solar_resource").
                </p>
                
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Namespace
                  </label>
                  <input
                    type="text"
                    value={actionNamespace}
                    onChange={(e) => setActionNamespace(e.target.value)}
                    placeholder="e.g., solar_resource"
                    className="block w-full border border-gray-300 rounded px-3 py-2"
                  />
                </div>
                
                <button
                  onClick={() => {
                    setSelectedAction('invalidate');
                    handleCacheAction();
                  }}
                  className="w-full bg-yellow-500 hover:bg-yellow-600 text-white py-2 px-3 rounded"
                  disabled={loading || !actionNamespace.trim()}
                >
                  Invalidate Namespace
                </button>
              </div>
              
              <div className="p-4 border rounded">
                <h4 className="font-medium mb-2">Cleanup Expired Entries</h4>
                <p className="text-sm text-gray-600 mb-4">
                  Remove all expired entries from the cache to free up resources.
                </p>
                
                <button
                  onClick={() => {
                    setSelectedAction('cleanup');
                    handleCacheAction();
                  }}
                  className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-3 rounded"
                  disabled={loading}
                >
                  Cleanup Expired Entries
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

CacheMonitoring.propTypes = {
  isAdmin: PropTypes.bool
};

export default CacheMonitoring;