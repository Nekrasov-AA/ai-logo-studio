import React from 'react';

const ApiTest: React.FC = () => {
  const testApi = async () => {
    try {
      console.log('Testing API connection...');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/health`);
      const data = await response.json();
      console.log('API Response:', data);
      alert(`API Status: ${data.status}`);
    } catch (error) {
      console.error('API Error:', error);
      alert('API connection failed');
    }
  };

  return (
    <div className="p-4">
      <button 
        onClick={testApi}
        className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800"
      >
        Test API Connection
      </button>
    </div>
  );
};

export default ApiTest;