const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  listFolders: (path) => ipcRenderer.invoke('list-folders', path),
  platform: process.platform,
  openFolder: (path) => ipcRenderer.invoke('open-folder', path)
}); 