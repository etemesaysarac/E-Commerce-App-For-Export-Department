import React, { useState } from 'react';
import 'material-icons/iconfont/material-icons.css';

const ProductCard = ({ product }) => {
  const [showVariants, setShowVariants] = useState(false);

  if (!product) {
    return <div>Ürün bilgisi bulunamadı</div>;
  }

  return (
    <div className="border rounded-lg p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-start space-x-4">
        <img
          src={product.image || '/placeholder-image.jpg'}
          alt={product.name}
          className="w-24 h-24 object-cover rounded"
          onError={(e) => {
            e.target.src = '/placeholder-image.jpg';
          }}
        />
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold">{product.name}</h3>
              <p className="text-sm text-gray-600">SKU: {product.sku}</p>
            </div>
            <div className="flex flex-col space-y-2">
              <button className="text-blue-600 hover:text-blue-800">
                <span className="material-icons">edit</span>
              </button>
              <button className="text-red-600 hover:text-red-800">
                <span className="material-icons">delete</span>
              </button>
            </div>
          </div>

          <div className="mt-2 flex items-center space-x-2">
            <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
              Stok: {product.stock}
            </span>
            <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
              {product.price} TL
            </span>
          </div>

          <div className="mt-2 flex flex-wrap gap-2">
            {product.categories?.map(category => (
              <span
                key={category}
                className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded"
              >
                {category}
              </span>
            ))}
            {product.tags?.map(tag => (
              <span
                key={tag}
                className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded"
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="mt-2">
            {product.variants && product.variants.length > 0 && (
              <>
                <button
                  onClick={() => setShowVariants(!showVariants)}
                  className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                >
                  <span className="material-icons text-sm mr-1">
                    {showVariants ? 'expand_less' : 'expand_more'}
                  </span>
                  Varyasyonlar ({product.variants.length})
                </button>
                
                {showVariants && (
                  <div className="mt-2 space-y-2">
                    {product.variants.map((variant, index) => (
                      <div
                        key={index}
                        className="text-sm p-2 bg-gray-50 rounded flex justify-between items-center"
                      >
                        <span>{variant.name}</span>
                        <span className="text-gray-600">{variant.stock} adet</span>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard; 