// client/src/components/__tests__/SolarMapComponent.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SolarMapComponent from '../SolarMapComponent';

// Mock the Leaflet library
jest.mock('leaflet', () => ({
  map: jest.fn().mockReturnValue({
    setView: jest.fn(),
    on: jest.fn(),
    removeLayer: jest.fn(),
  }),
  tileLayer: jest.fn().mockReturnValue({
    addTo: jest.fn().mockReturnThis(),
  }),
  marker: jest.fn().mockReturnValue({
    addTo: jest.fn().mockReturnThis(),
    bindPopup: jest.fn().mockReturnThis(),
  }),
  circleMarker: jest.fn().mockReturnValue({
    addTo: jest.fn().mockReturnThis(),
    bindPopup: jest.fn().mockReturnThis(),
    on: jest.fn(),
  }),
  layerGroup: jest.fn().mockReturnValue({
    addTo: jest.fn().mockReturnThis(),
    clearLayers: jest.fn(),
    eachLayer: jest.fn((callback) => callback({
      _latlng: { lat: 39.7392, lng: -104.9903 },
      removeLayer: jest.fn(),
    })),
  }),
  control: {
    layers: jest.fn().mockReturnValue({
      addTo: jest.fn(),
    }),
  },
}));

describe('SolarMapComponent', () => {
  const mockOnLocationSelect = jest.fn();
  
  beforeEach(() => {
    // Reset mocks
    mockOnLocationSelect.mockClear();
  });
  
  test('renders map container', () => {
    render(<SolarMapComponent onLocationSelect={mockOnLocationSelect} />);
    
    // Check that the map container is rendered
    const mapContainer = screen.getByTestId('map-container');
    expect(mapContainer).toBeInTheDocument();
  });
  
  test('handles latitude input change', () => {
    render(<SolarMapComponent onLocationSelect={mockOnLocationSelect} />);
    
    // Find latitude input
    const latInput = screen.getByLabelText(/latitude/i);
    
    // Change input value
    fireEvent.change(latInput, { target: { value: '40.0' } });
    
    // Check that input value changed
    expect(latInput.value).toBe('40.0');
  });
  
  test('calls onLocationSelect when Go button is clicked', () => {
    render(<SolarMapComponent onLocationSelect={mockOnLocationSelect} />);
    
    // Find latitude and longitude inputs
    const latInput = screen.getByLabelText(/latitude/i);
    const lonInput = screen.getByLabelText(/longitude/i);
    const goButton = screen.getByText(/go to location/i);
    
    // Change input values
    fireEvent.change(latInput, { target: { value: '40.0' } });
    fireEvent.change(lonInput, { target: { value: '-105.0' } });
    
    // Click button
    fireEvent.click(goButton);
    
    // Check that onLocationSelect was called with correct coordinates
    expect(mockOnLocationSelect).toHaveBeenCalledWith({
      lat: 40.0,
      lon: -105.0
    });
  });
});