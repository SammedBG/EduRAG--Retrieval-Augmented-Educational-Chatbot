import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { FileUpload } from './components/FileUpload';
import { ChatInterface } from './components/ChatInterface';
import { Header } from './components/Header';
import { StatusBar } from './components/StatusBar';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://edurag-retrieval-augmented-educational.onrender.com';

function App() {
  const [files, setFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [systemStatus, setSystemStatus] = useState({ healthy: false, embeddingsReady: false });
  const [activeTab, setActiveTab] = useState('chat');

  useEffect(() => {
    checkSystemStatus();
    loadFiles();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setSystemStatus(response.data);
    } catch (error) {
      console.error('Error checking system status:', error);
      setSystemStatus({ healthy: false, embeddingsReady: false });
    }
  };

  const loadFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files`);
      setFiles(response.data.files);
    } catch (error) {
      console.error('Error loading files:', error);
    }
  };

  const handleFileUpload = async (uploadedFiles) => {
    setIsProcessing(true);
    try {
      // Step 1: Upload files
      const formData = new FormData();
      uploadedFiles.forEach(file => {
        formData.append('files', file);
      });

      const uploadResponse = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Reload files after upload
      await loadFiles();
      
      alert(`Successfully uploaded ${uploadResponse.data.uploaded_files.length} files!`);
      
      // Step 2: Process documents
      alert('Now processing documents... This may take a moment.');
      const processResponse = await axios.post(`${API_BASE_URL}/process`);
      
      // Check status after processing
      await checkSystemStatus();
      
      alert(`Successfully processed documents! ${processResponse.data.message}`);
    } catch (error) {
      console.error('Error uploading/processing files:', error);
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileDelete = async (filename) => {
    try {
      await axios.delete(`${API_BASE_URL}/files/${filename}`);
      await loadFiles();
      await checkSystemStatus();
      alert(`File ${filename} deleted successfully!`);
    } catch (error) {
      console.error('Error deleting file:', error);
      alert(`Error deleting file: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        systemStatus={systemStatus}
      />
      
      <StatusBar 
        systemStatus={systemStatus}
        fileCount={files.length}
        isProcessing={isProcessing}
      />

      <main className="container mx-auto px-4 py-8">
        {activeTab === 'upload' && (
          <FileUpload 
            onFileUpload={handleFileUpload}
            files={files}
            onFileDelete={handleFileDelete}
            isProcessing={isProcessing}
          />
        )}
        
        {activeTab === 'chat' && (
          <ChatInterface 
            systemStatus={systemStatus}
            files={files}
          />
        )}
      </main>
    </div>
  );
}

export default App;
