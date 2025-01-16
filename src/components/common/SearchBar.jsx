import React from 'react';

export const SearchBar = ({ value, onChange, placeholder }) => {
  return (
    <div className="relative">
      <span className="absolute inset-y-0 left-0 pl-3 flex items-center">
        <span className="material-icons text-gray-400">search</span>
      </span>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );
}; 