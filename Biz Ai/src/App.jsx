import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import {
  RFQView,
  QuotationsView,
  PurchaseOrdersView,
  OperationsView,
  FinanceView,
  SettingsView
} from './views';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-100">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/rfqs" replace />} />
              <Route path="/rfqs" element={<RFQView />} />
              <Route path="/quotations" element={<QuotationsView />} />
              <Route path="/purchase-orders" element={<PurchaseOrdersView />} />
              <Route path="/operations" element={<OperationsView />} />
              <Route path="/finance" element={<FinanceView />} />
              <Route path="/settings" element={<SettingsView />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App; 

