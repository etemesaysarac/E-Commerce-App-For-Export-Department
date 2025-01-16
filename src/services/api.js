import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export const api = {
  // Ürünleri getir
  getProducts: async (filters) => {
    const params = new URLSearchParams();
    if (filters.search) params.append('search', filters.search);
    filters.categories.forEach(c => params.append('categories', c));
    filters.tags.forEach(t => params.append('tags', t));
    if (filters.priceRange.min) params.append('min_price', filters.priceRange.min);
    if (filters.priceRange.max) params.append('max_price', filters.priceRange.max);
    if (filters.stock !== 'all') params.append('stock', filters.stock);

    const response = await axios.get(`${API_BASE_URL}/products`, { params });
    return response.data;
  },

  // Yeni ürün ekle
  addProduct: async (productData) => {
    const response = await axios.post(`${API_BASE_URL}/products`, productData);
    return response.data;
  },

  // Toplu ürün yükle
  bulkUpload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(`${API_BASE_URL}/products/bulk`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  // Ürün güncelle
  updateProduct: async (productId, productData) => {
    const response = await axios.put(`${API_BASE_URL}/products/${productId}`, productData);
    return response.data;
  },

  // Ürün sil
  deleteProduct: async (productId) => {
    const response = await axios.delete(`${API_BASE_URL}/products/${productId}`);
    return response.data;
  }
}; 