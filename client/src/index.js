// client/src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import EnergyInvestmentApp from './components/EnergyInvestmentApp';
import AuthProvider from './components/AuthProvider';
import './index.css';

ReactDOM.render(
  <React.StrictMode>
    <AuthProvider>
      <EnergyInvestmentApp />
    </AuthProvider>
  </React.StrictMode>,
  document.getElementById('root')
);