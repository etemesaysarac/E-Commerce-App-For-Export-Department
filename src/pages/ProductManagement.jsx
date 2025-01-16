import React, { useState } from 'react';
import ProductList from '../components/products/ProductList';
import ProductForm from '../components/products/ProductForm';
import MarketplaceStatus from '../components/products/MarketplaceStatus';
import BulkUploadModal from '../components/products/BulkUploadModal';
import FilterPanel from '../components/products/FilterPanel';
import { SearchBar } from '../components/common/SearchBar';

const ProductManagement = () => {
  const [isAddProductModalOpen, setIsAddProductModalOpen] = useState(false);
  const [isBulkUploadOpen, setIsBulkUploadOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    categories: [],
    tags: [],
    priceRange: { min: '', max: '' },
    stock: 'all' // all, inStock, lowStock, outOfStock
  });

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Ürün Yönetimi</h1>
        <div className="flex space-x-3">
          <button
            onClick={() => setIsBulkUploadOpen(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
          >
            Toplu Ürün Yükle
          </button>
          <button
            onClick={() => setIsAddProductModalOpen(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Yeni Ürün Ekle
          </button>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex space-x-4">
          <div className="flex-1">
            <SearchBar 
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Ürün ara..."
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <FilterPanel filters={filters} setFilters={setFilters} />
        </div>
        <div className="lg:col-span-2">
          <ProductList searchQuery={searchQuery} filters={filters} />
        </div>
        <div className="lg:col-span-1">
          <MarketplaceStatus />
        </div>
      </div>

      {isAddProductModalOpen && (
        <ProductForm onClose={() => setIsAddProductModalOpen(false)} />
      )}
      
      {isBulkUploadOpen && (
        <BulkUploadModal onClose={() => setIsBulkUploadOpen(false)} />
      )}
    </div>
  );
};

export default ProductManagement; 