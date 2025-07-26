import React, { useState, useEffect } from 'react';
import { folderService } from '../services/api';

const FolderView = ({ title, folderType }) => {
  const [folders, setFolders] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFolders(true);
  }, [folderType]);

  useEffect(() => {
    const refreshInterval = setInterval(() => {
      silentRefresh();
    }, 20000);  // 20 seconds

    return () => clearInterval(refreshInterval);
  }, [folderType]);

  const loadFolders = async (showLoading) => {
    try {
      if (showLoading) setLoading(true);
      setError(null);
      const folderList = await folderService.listFolders(folderType);
      setFolders(folderList);
    } catch (err) {
      setError(err.message || 'Failed to load folders');
      console.error('Error loading folders:', err);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  const silentRefresh = async () => {
    try {
      const folderList = await folderService.listFolders(folderType);
      if (JSON.stringify(folderList) !== JSON.stringify(folders)) {
        setFolders(folderList);
      }
    } catch (err) {
      console.error('Silent refresh error:', err);
    }
  };

  const handleFolderClick = async (path) => {
    try {
      await folderService.openFolder(path);
    } catch (err) {
      console.error('Error opening folder:', err);
      setError('Failed to open folder');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-red-500 bg-red-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">Error</h3>
        <p>{error}</p>
        <button 
          onClick={() => loadFolders(true)}
          className="mt-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-800 mb-8">{title}</h2>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="grid grid-cols-4 gap-x-16 px-8 py-4 bg-gray-50 border-b">
          <div className="font-semibold text-gray-700">Folders</div>
          <div className="font-semibold text-gray-700">Date</div>
          <div className="font-semibold text-gray-700">Status</div>
          <div className="font-semibold text-gray-700">Notes</div>
        </div>
        {folders.length === 0 ? (
          <div className="px-8 py-4 text-gray-500">No folders found</div>
        ) : (
          folders.map((folder) => (
            <div 
              key={folder.path}
              className="grid grid-cols-4 gap-x-16 px-8 py-4 border-b last:border-b-0 hover:bg-gray-50 items-center cursor-pointer"
              onClick={() => handleFolderClick(folder.path)}
            >
              <div className="text-gray-900">{folder.name}</div>
              <div className="text-gray-600">{folder.date_modified}</div>
              <div className="text-green-600">{folder.status}</div>
              <div className="text-gray-600">{folder.notes}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FolderView; 
