import React, { useState } from 'react';

const ProductForm = ({ onClose, editProduct = null }) => {
  const [formData, setFormData] = useState({
    name: editProduct?.name || '',
    sku: editProduct?.sku || '',
    price: editProduct?.price || '',
    stock: editProduct?.stock || '',
    description: editProduct?.description || '',
    marketplaces: editProduct?.marketplaces || {
      trendyol: false,
      amazon: false,
      n11: false,
      hepsiburada: false
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // API'ye ürün kaydetme işlemi burada yapılacak
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {editProduct ? 'Ürün Düzenle' : 'Yeni Ürün Ekle'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <span className="material-icons">close</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Ürün Adı</label>
              <input
                type="text"
                className="w-full border rounded-lg p-2"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">SKU</label>
              <input
                type="text"
                className="w-full border rounded-lg p-2"
                value={formData.sku}
                onChange={(e) => setFormData({...formData, sku: e.target.value})}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Fiyat</label>
              <input
                type="number"
                className="w-full border rounded-lg p-2"
                value={formData.price}
                onChange={(e) => setFormData({...formData, price: e.target.value})}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Stok</label>
              <input
                type="number"
                className="w-full border rounded-lg p-2"
                value={formData.stock}
                onChange={(e) => setFormData({...formData, stock: e.target.value})}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Pazaryerleri</label>
            <div className="grid grid-cols-2 gap-2">
              {Object.keys(formData.marketplaces).map(marketplace => (
                <label key={marketplace} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.marketplaces[marketplace]}
                    onChange={(e) => setFormData({
                      ...formData,
                      marketplaces: {
                        ...formData.marketplaces,
                        [marketplace]: e.target.checked
                      }
                    })}
                  />
                  <span className="capitalize">{marketplace}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border rounded-lg"
            >
              İptal
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Kaydet
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProductForm; 