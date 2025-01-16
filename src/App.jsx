import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import ProductManagement from './pages/ProductManagement';
import StockManagement from './pages/StockManagement';
import ProfitCalculator from './pages/ProfitCalculator';
import ERPIntegration from './pages/ERPIntegration';

function App() {
  return (
    <BrowserRouter>
      <div className="flex">
        <Sidebar />
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/products" element={<ProductManagement />} />
            <Route path="/stock" element={<StockManagement />} />
            <Route path="/profit-calculator" element={<ProfitCalculator />} />
            <Route path="/erp-integration" element={<ERPIntegration />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App; 