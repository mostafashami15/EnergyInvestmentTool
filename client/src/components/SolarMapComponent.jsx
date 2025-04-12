import React, { useState, useEffect, useRef } from 'react';

const SolarMapComponent = ({ onLocationSelect, initialLocation, solarData }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersLayerRef = useRef(null);
  const heatmapLayerRef = useRef(null);
  const selectedMarkerRef = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapError, setMapError] = useState(null);
  
  // Default location (Denver, CO) if none provided
  const defaultLocation = { lat: 39.7392, lon: -104.9903 };
  const location = initialLocation || defaultLocation;
  
  // Sample data for solar radiation (for demonstration purposes)
  // In a real implementation, this would come from the API
  const sampleSolarData = solarData || [
    { "city": "Denver", "lat": 39.7392, "lon": -104.9903, "ghi": 5.5, "dni": 6.1 },
    { "city": "Phoenix", "lat": 33.4484, "lon": -112.0740, "ghi": 6.2, "dni": 7.4 },
    { "city": "Seattle", "lat": 47.6062, "lon": -122.3321, "ghi": 3.5, "dni": 3.9 },
    { "city": "New York", "lat": 40.7128, "lon": -74.0060, "ghi": 4.1, "dni": 4.5 },
    { "city": "Miami", "lat": 25.7617, "lon": -80.1918, "ghi": 5.7, "dni": 5.9 },
    { "city": "Chicago", "lat": 41.8781, "lon": -87.6298, "ghi": 4.0, "dni": 4.3 },
    { "city": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "ghi": 5.6, "dni": 6.4 },
    { "city": "Houston", "lat": 29.7604, "lon": -95.3698, "ghi": 5.2, "dni": 5.5 },
    { "city": "Boston", "lat": 42.3601, "lon": -71.0589, "ghi": 4.0, "dni": 4.4 },
    { "city": "San Francisco", "lat": 37.7749, "lon": -122.4194, "ghi": 5.0, "dni": 5.9 }
  ];

  // Initialize map when component mounts
  useEffect(() => {
    // Check if Leaflet is available
    if (!window.L) {
      // Load Leaflet CSS
      const linkElement = document.createElement('link');
      linkElement.rel = 'stylesheet';
      linkElement.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      linkElement.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
      linkElement.crossOrigin = '';
      document.head.appendChild(linkElement);
      
      // Load Leaflet JS
      const scriptElement = document.createElement('script');
      scriptElement.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      scriptElement.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
      scriptElement.crossOrigin = '';
      scriptElement.onload = initializeMap;
      scriptElement.onerror = () => setMapError('Failed to load map library');
      document.body.appendChild(scriptElement);
    } else {
      initializeMap();
    }
    
    return () => {
      // Clean up map when component unmounts
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);
  
  // Update map when location or solar data changes
  useEffect(() => {
    if (mapLoaded && mapInstanceRef.current) {
      updateMapView();
      updateSolarDataLayer();
    }
  }, [mapLoaded, location, solarData]);
  
  const initializeMap = () => {
    try {
      if (!mapRef.current || mapInstanceRef.current) return;
      
      const L = window.L;
      
      // Create map instance
      const map = L.map(mapRef.current).setView([location.lat, location.lon], 5);
      
      // Add tile layer (OpenStreetMap)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
      }).addTo(map);
      
      // Create layer for markers
      const markersLayer = L.layerGroup().addTo(map);
      
      // Store references
      mapInstanceRef.current = map;
      markersLayerRef.current = markersLayer;
      
      // Add click handler to map
      map.on('click', handleMapClick);
      
      // Add selected location marker
      addSelectedLocationMarker(location.lat, location.lon);
      
      // Add solar data to map
      updateSolarDataLayer();
      
      // Add legend
      addLegend(map);
      
      setMapLoaded(true);
    } catch (error) {
      console.error('Error initializing map:', error);
      setMapError('Failed to initialize map');
    }
  };
  
  const updateMapView = () => {
    const map = mapInstanceRef.current;
    if (!map) return;
    
    // Update the map view to center on the selected location
    map.setView([location.lat, location.lon], map.getZoom());
    
    // Update the selected location marker
    addSelectedLocationMarker(location.lat, location.lon);
  };
  
  const updateSolarDataLayer = () => {
    const map = mapInstanceRef.current;
    const markersLayer = markersLayerRef.current;
    if (!map || !markersLayer) return;
    
    // Clear existing markers (except the selected one)
    markersLayer.eachLayer(layer => {
      if (layer !== selectedMarkerRef.current) {
        markersLayer.removeLayer(layer);
      }
    });
    
    // Add solar data markers
    sampleSolarData.forEach(data => {
      // Calculate marker color based on GHI value
      const normalizedGHI = (data.ghi - 3.5) / (6.5 - 3.5); // Scale 3.5-6.5 to 0-1
      const color = getColorForValue(normalizedGHI);
      
      // Create a circle marker with color based on solar radiation
      const circle = L.circleMarker([data.lat, data.lon], {
        radius: 15,
        fillColor: color,
        color: '#000',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
      }).addTo(markersLayer);
      
      // Add a popup with location details
      circle.bindPopup(`
        <strong>${data.city || 'Location'}</strong><br>
        GHI: ${data.ghi} kWh/m²/day<br>
        DNI: ${data.dni} kWh/m²/day<br>
        <em>Click to select this location</em>
      `);
      
      // Add click handler to set the location
      circle.on('click', () => {
        selectLocation(data.lat, data.lon);
      });
    });
  };
  
  const addSelectedLocationMarker = (lat, lon) => {
    const L = window.L;
    const map = mapInstanceRef.current;
    const markersLayer = markersLayerRef.current;
    if (!L || !map || !markersLayer) return;
    
    // Remove existing selected marker
    if (selectedMarkerRef.current) {
      markersLayer.removeLayer(selectedMarkerRef.current);
    }
    
    // Add a marker at the selected location
    const marker = L.marker([lat, lon]).addTo(markersLayer);
    marker.bindPopup(`Selected Location<br>Lat: ${lat.toFixed(4)}<br>Lon: ${lon.toFixed(4)}`);
    
    // Store reference to the selected marker
    selectedMarkerRef.current = marker;
  };
  
  const addLegend = (map) => {
    const L = window.L;
    if (!L || !map) return;
    
    // Create a legend control
    const legend = L.control({ position: 'bottomright' });
    
    // Define the legend content
    legend.onAdd = function () {
      const div = L.DomUtil.create('div', 'legend');
      div.style.backgroundColor = 'white';
      div.style.padding = '10px';
      div.style.borderRadius = '5px';
      div.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';
      
      // Legend title
      div.innerHTML = '<div style="font-weight: bold; margin-bottom: 5px;">Solar Radiation (GHI)</div>';
      
      const grades = [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5];
      
      // Loop through our intervals and generate a label with a colored square for each interval
      for (let i = 0; i < grades.length; i++) {
        const normalizedGHI = (grades[i] - 3.5) / (6.5 - 3.5);
        const color = getColorForValue(normalizedGHI);
        
        div.innerHTML +=
          '<div style="display: flex; align-items: center; margin-bottom: 3px;">' +
          `<span style="display: inline-block; width: 15px; height: 15px; margin-right: 5px; background: ${color};"></span> ` +
          `<span>${grades[i]}${grades[i + 1] ? '–' + grades[i + 1] : '+'} kWh/m²/day</span>` +
          '</div>';
      }
      
      return div;
    };
    
    // Add the legend to the map
    legend.addTo(map);
  };
  
  const handleMapClick = (e) => {
    selectLocation(e.latlng.lat, e.latlng.lng);
  };
  
  const selectLocation = (lat, lon) => {
    if (onLocationSelect) {
      onLocationSelect({ lat, lon });
    }
    
    // Update the selected location marker
    addSelectedLocationMarker(lat, lon);
  };
  
  // Function to convert a normalized value (0-1) to a color
  const getColorForValue = (normalizedValue) => {
    // Color ramp from blue (low) to red (high)
    const h = (1 - normalizedValue) * 240; // Hue: 240 (blue) to 0 (red)
    return `hsl(${h}, 100%, 50%)`;
  };
  
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold text-gray-800">Solar Resource Map</h2>
        <p className="text-sm text-gray-600">
          Click on the map to select a location or use the search box below
        </p>
      </div>
      
      <div className="p-4">
        <div className="flex flex-col md:flex-row mb-4 gap-2">
          <div className="flex-grow">
            <label htmlFor="latitude" className="block text-sm font-medium text-gray-700 mb-1">
              Latitude
            </label>
            <input
              type="number"
              id="latitude"
              value={location.lat}
              onChange={(e) => selectLocation(parseFloat(e.target.value), location.lon)}
              step="0.0001"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>
          <div className="flex-grow">
            <label htmlFor="longitude" className="block text-sm font-medium text-gray-700 mb-1">
              Longitude
            </label>
            <input
              type="number"
              id="longitude"
              value={location.lon}
              onChange={(e) => selectLocation(location.lat, parseFloat(e.target.value))}
              step="0.0001"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                if (navigator.geolocation) {
                  navigator.geolocation.getCurrentPosition(
                    (position) => {
                      selectLocation(position.coords.latitude, position.coords.longitude);
                    },
                    (error) => {
                      console.error('Error getting location:', error);
                      alert('Could not get your current location.');
                    }
                  );
                } else {
                  alert('Geolocation is not supported by your browser.');
                }
              }}
              className="h-10 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Use My Location
            </button>
          </div>
        </div>
      </div>
      
      {mapError ? (
        <div className="p-4 text-red-600 bg-red-50 rounded-md">
          {mapError}
        </div>
      ) : (
        <div 
          ref={mapRef} 
          style={{ height: '500px' }}
          className="rounded-b-lg"
        ></div>
      )}
    </div>
  );
};

export default SolarMapComponent;