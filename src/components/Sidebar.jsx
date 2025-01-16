import React from 'react';
import { Link } from 'react-router-dom';

const Sidebar = () => {
  const menuItems = [
    { title: 'Dashboard', path: '/', icon: 'dashboard' },
    { title: 'Ürün Yönetimi', path: '/products', icon: 'inventory' },
    { title: 'Stok Takibi', path: '/stock', icon: 'storage' },
    { title: 'Kâr Hesaplama', path: '/profit-calculator', icon: 'calculate' },
    { title: 'ERP Entegrasyonu', path: '/erp-integration', icon: 'settings' },
  ];

  return (
    <div className="w-64 min-h-screen bg-gray-800 text-white">
      <div className="p-4">
        <h1 className="text-xl font-bold">E-Ticaret Yönetimi</h1>
      </div>
      <nav className="mt-8">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className="flex items-center px-6 py-3 hover:bg-gray-700"
          >
            <span className="material-icons mr-3">{item.icon}</span>
            {item.title}
          </Link>
        ))}
      </nav>
    </div>
  );
}

export default Sidebar; 