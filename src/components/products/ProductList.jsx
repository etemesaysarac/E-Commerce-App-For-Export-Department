import React from 'react';
import ProductCard from './ProductCard';

const ProductList = () => {
  // Örnek ürün verisi
  const products = [
    {
      id: 1,
      name: 'Örnek Ürün 1',
      sku: 'SKU001',
      stock: 150,
      price: 199.99,
      marketplaces: ['Trendyol', 'Amazon', 'N11'],
      image: 'product1.jpg'
    }
    // Diğer ürünler...
  ];

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Ürün Listesi</h2>
      </div>
      <div className="grid gap-4 p-4">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
};

export default ProductList; 