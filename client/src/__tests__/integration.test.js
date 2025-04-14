// client/src/__tests__/integration.test.js
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { renderHook, act } from '@testing-library/react-hooks';
import { useCalculationApi } from '../hooks/useCalculationApi';

describe('API Integration', () => {
  let mock;
  
  beforeEach(() => {
    mock = new MockAdapter(axios);
  });
  
  afterEach(() => {
    mock.restore();
  });
  
  test('fetchSolarProduction makes correct API call and processes response', async () => {
    // Mock API response
    const mockResponse = {
      nrel: {
        annual_production_kwh: 15000,
        monthly_production_kwh: [1000, 1100, 1300, 1400, 1500, 1600, 1600, 1500, 1400, 1300, 1100, 1000]
      },
      nasa: {
        annual_production_kwh: 12000,
        monthly_production_kwh: [800, 900, 1000, 1100, 1200, 1300, 1300, 1200, 1100, 1000, 900, 800]
      },
      comparison: {
        percent_difference: 25
      }
    };
    
    mock.onPost('/api/calculate-production').reply(200, mockResponse);
    
    // Render hook
    const { result, waitForNextUpdate } = renderHook(() => useCalculationApi());
    
    // Call the API method
    act(() => {
      result.current.fetchSolarProduction({
        latitude: 39.7392,
        longitude: -104.9903,
        systemCapacity: 10.0,
        moduleType: 1,
        tilt: 20,
        azimuth: 180
      });
    });
    
    // Wait for the API call to complete
    await waitForNextUpdate();
    
    // Verify loading state changed
    expect(result.current.loading).toBe(false);
    
    // Verify data was set correctly
    expect(result.current.data).toEqual(mockResponse);
    
    // Verify error is null
    expect(result.current.error).toBe(null);
  });
  
  test('handles API errors correctly', async () => {
    // Mock API error
    mock.onPost('/api/calculate-production').reply(500, { error: 'Internal server error' });
    
    // Render hook
    const { result, waitForNextUpdate } = renderHook(() => useCalculationApi());
    
    // Call the API method
    act(() => {
      result.current.fetchSolarProduction({
        latitude: 39.7392,
        longitude: -104.9903,
        systemCapacity: 10.0
      });
    });
    
    // Wait for the API call to complete
    await waitForNextUpdate();
    
    // Verify loading state changed
    expect(result.current.loading).toBe(false);
    
    // Verify error was set
    expect(result.current.error).toBe('Internal server error');
    
    // Verify data is null
    expect(result.current.data).toBe(null);
  });
});