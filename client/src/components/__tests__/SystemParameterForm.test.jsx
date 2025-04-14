// client/src/components/__tests__/SystemParameterForm.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SystemParameterForm from '../SystemParameterForm';

describe('SystemParameterForm', () => {
  const mockSubmit = jest.fn();
  
  beforeEach(() => {
    mockSubmit.mockClear();
  });
  
  test('renders all form sections', () => {
    render(<SystemParameterForm onSubmit={mockSubmit} />);
    
    // Check that all sections are rendered
    expect(screen.getByText(/system specifications/i)).toBeInTheDocument();
    expect(screen.getByText(/array orientation/i)).toBeInTheDocument();
    expect(screen.getByText(/financial parameters/i)).toBeInTheDocument();
  });
  
  test('has correct default values', () => {
    render(<SystemParameterForm onSubmit={mockSubmit} />);
    
    // Check default values
    expect(screen.getByLabelText(/system capacity/i).value).toBe('10');
    expect(screen.getByLabelText(/tilt/i).value).toBe('20');
    expect(screen.getByLabelText(/azimuth/i).value).toBe('180');
  });
  
  test('updates form values on input change', () => {
    render(<SystemParameterForm onSubmit={mockSubmit} />);
    
    // Find capacity input
    const capacityInput = screen.getByLabelText(/system capacity/i);
    
    // Change input value
    fireEvent.change(capacityInput, { target: { value: '15' } });
    
    // Check that input value changed
    expect(capacityInput.value).toBe('15');
  });
  
  test('submits form with correct values', () => {
    render(<SystemParameterForm onSubmit={mockSubmit} />);
    
    // Find inputs and submit button
    const capacityInput = screen.getByLabelText(/system capacity/i);
    const tiltInput = screen.getByLabelText(/tilt/i);
    const submitButton = screen.getByText(/calculate/i);
    
    // Change input values
    fireEvent.change(capacityInput, { target: { value: '15' } });
    fireEvent.change(tiltInput, { target: { value: '30' } });
    
    // Submit form
    fireEvent.click(submitButton);
    
    // Check that onSubmit was called with updated values
    expect(mockSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        systemCapacity: 15,
        tilt: 30,
        azimuth: 180,  // Default value
      })
    );
  });
  
  test('validates numeric inputs', () => {
    render(<SystemParameterForm onSubmit={mockSubmit} />);
    
    // Find capacity input
    const capacityInput = screen.getByLabelText(/system capacity/i);
    
    // Change to invalid value
    fireEvent.change(capacityInput, { target: { value: '-5' } });
    
    // Submit form
    const submitButton = screen.getByText(/calculate/i);
    fireEvent.click(submitButton);
    
    // Check that error message is displayed
    expect(screen.getByText(/system capacity must be positive/i)).toBeInTheDocument();
    
    // Check that onSubmit was not called
    expect(mockSubmit).not.toHaveBeenCalled();
  });
});