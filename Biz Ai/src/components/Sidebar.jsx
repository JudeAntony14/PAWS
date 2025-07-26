import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  FileText,
  ClipboardList,
  ShoppingCart,
  Activity,
  DollarSign,
  Settings
} from 'lucide-react';

const Sidebar = () => {
  const navigation = [
    { name: 'RFQs', path: '/rfqs', icon: FileText },
    { name: 'Quotations', path: '/quotations', icon: ClipboardList },
    { name: 'Purchase Orders', path: '/purchase-orders', icon: ShoppingCart },
    { name: 'Operations', path: '/operations', icon: Activity },
    { name: 'Finance', path: '/finance', icon: DollarSign },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <div className="w-64 bg-white border-r">
      <div className="h-16 flex items-center px-6 border-b">
        <h1 className="text-xl font-semibold text-gray-800">Trading Workflow</h1>
      </div>
      <nav className="mt-6">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center px-6 py-3 text-gray-700 hover:bg-gray-50 ${
                  isActive ? 'bg-gray-50 text-blue-600' : ''
                }`
              }
            >
              <Icon className="w-5 h-5 mr-3" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
};

export default Sidebar; 