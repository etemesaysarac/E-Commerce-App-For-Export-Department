import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';

const BulkUploadModal = ({ onClose }) => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
  
  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setUploadedFile(acceptedFiles[0]);
    }
  });

  const handleUpload = async () => {
    if (!uploadedFile) return;
    
    setUploadStatus('uploading');
    
    // Örnek upload işlemi
    const formData = new FormData();
    formData.append('file', uploadedFile);
    
    try {
      // API çağrısı burada yapılacak
      await new Promise(resolve => setTimeout(resolve, 2000)); // Demo için gecikme
      setUploadStatus('success');
    } catch (error) {
      setUploadStatus('error');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Toplu Ürün Yükleme</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <span className="material-icons">close</span>
          </button>
        </div>

        <div className="space-y-4">
          <div
            {...getRootProps()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500"
          >
            <input {...getInputProps()} />
            {uploadedFile ? (
              <div>
                <p className="text-green-600">Dosya seçildi: {uploadedFile.name}</p>
                <p className="text-sm text-gray-500">Değiştirmek için tıklayın veya yeni bir dosya sürükleyin</p>
              </div>
            ) : (
              <div>
                <p>Excel veya CSV dosyanızı buraya sürükleyin</p>
                <p className="text-sm text-gray-500">veya dosya seçmek için tıklayın</p>
              </div>
            )}
          </div>

          <div className="flex justify-between items-center">
            <a
              href="/sample-template.xlsx"
              download
              className="text-blue-600 hover:text-blue-800"
            >
              Örnek şablonu indir
            </a>
            
            <div className="flex space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 border rounded-lg"
              >
                İptal
              </button>
              <button
                onClick={handleUpload}
                disabled={!uploadedFile || uploadStatus === 'uploading'}
                className={`px-4 py-2 rounded-lg ${
                  uploadStatus === 'uploading'
                    ? 'bg-gray-400'
                    : 'bg-blue-600 hover:bg-blue-700'
                } text-white`}
              >
                {uploadStatus === 'uploading' ? 'Yükleniyor...' : 'Yükle'}
              </button>
            </div>
          </div>

          {uploadStatus === 'success' && (
            <div className="text-green-600 text-center">
              Dosya başarıyla yüklendi!
            </div>
          )}
          
          {uploadStatus === 'error' && (
            <div className="text-red-600 text-center">
              Yükleme sırasında bir hata oluştu. Lütfen tekrar deneyin.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BulkUploadModal; 