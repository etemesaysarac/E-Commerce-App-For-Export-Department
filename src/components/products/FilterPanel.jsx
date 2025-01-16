import React from 'react';

const FilterPanel = ({ filters, setFilters }) => {
  const categories = [
    'Elektronik',
    'Giyim',
    'Ev & Yaşam',
    'Kozmetik',
    'Kitap',
    'Spor'
  ];

  const tags = [
    'Yeni',
    'İndirimli',
    'Çok Satan',
    'Kampanyalı',
    'Öne Çıkan'
  ];

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-semibold mb-4">Filtreler</h3>
      
      <div className="space-y-6">
        {/* Kategoriler */}
        <div>
          <h4 className="font-medium mb-2">Kategoriler</h4>
          <div className="space-y-2">
            {categories.map(category => (
              <label key={category} className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.categories.includes(category)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFilters({
                        ...filters,
                        categories: [...filters.categories, category]
                      });
                    } else {
                      setFilters({
                        ...filters,
                        categories: filters.categories.filter(c => c !== category)
                      });
                    }
                  }}
                  className="mr-2"
                />
                {category}
              </label>
            ))}
          </div>
        </div>

        {/* Etiketler */}
        <div>
          <h4 className="font-medium mb-2">Etiketler</h4>
          <div className="space-y-2">
            {tags.map(tag => (
              <label key={tag} className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.tags.includes(tag)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFilters({
                        ...filters,
                        tags: [...filters.tags, tag]
                      });
                    } else {
                      setFilters({
                        ...filters,
                        tags: filters.tags.filter(t => t !== tag)
                      });
                    }
                  }}
                  className="mr-2"
                />
                {tag}
              </label>
            ))}
          </div>
        </div>

        {/* Fiyat Aralığı */}
        <div>
          <h4 className="font-medium mb-2">Fiyat Aralığı</h4>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              placeholder="Min"
              value={filters.priceRange.min}
              onChange={(e) => setFilters({
                ...filters,
                priceRange: { ...filters.priceRange, min: e.target.value }
              })}
              className="border rounded p-1 text-sm"
            />
            <input
              type="number"
              placeholder="Max"
              value={filters.priceRange.max}
              onChange={(e) => setFilters({
                ...filters,
                priceRange: { ...filters.priceRange, max: e.target.value }
              })}
              className="border rounded p-1 text-sm"
            />
          </div>
        </div>

        {/* Stok Durumu */}
        <div>
          <h4 className="font-medium mb-2">Stok Durumu</h4>
          <select
            value={filters.stock}
            onChange={(e) => setFilters({ ...filters, stock: e.target.value })}
            className="w-full border rounded p-1"
          >
            <option value="all">Tümü</option>
            <option value="inStock">Stokta Var</option>
            <option value="lowStock">Düşük Stok</option>
            <option value="outOfStock">Stokta Yok</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default FilterPanel; 