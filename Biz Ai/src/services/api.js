const API_BASE_URL = 'http://localhost:8000/api';

export const folderService = {
  async listFolders(folderType) {
    try {
      // First check if the API is available
      const healthCheck = await fetch(`${API_BASE_URL}/health`);
      if (!healthCheck.ok) {
        throw new Error('API server is not running');
      }

      const response = await fetch(`${API_BASE_URL}/folders/${folderType}`);
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch folders');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching folders:', error);
      throw error;
    }
  },

  async openFolder(path) {
    try {
      const response = await fetch(`${API_BASE_URL}/open-folder?path=${encodeURIComponent(path)}`);
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to open folder');
      }
      return await response.json();
    } catch (error) {
      console.error('Error opening folder:', error);
      throw error;
    }
  }
}; 