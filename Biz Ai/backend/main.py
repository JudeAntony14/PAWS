from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Configure CORS - add both Electron and Vite dev server origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "file://"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FolderInfo(BaseModel):
    name: str
    path: str
    date_modified: str
    status: str = "Active"
    notes: str = ""

BASE_PATHS = {
    'rfq': "C:/Users/judea/OneDrive/Desktop/ProcessedRFQs",
    'quotations': "C:/Users/judea/OneDrive/Desktop/ProcessedQuotations",
    'purchase-orders': "C:/Users/judea/OneDrive/Desktop/Inquiries",
    'operations': "C:/Users/judea/OneDrive/Desktop/Inquiries",
    'finance': "C:/Users/judea/OneDrive/Desktop/Inquiries"
}

@app.get("/api/folders/{folder_type}", response_model=List[FolderInfo])
async def list_folders(folder_type: str):
    if folder_type not in BASE_PATHS:
        raise HTTPException(status_code=400, detail="Invalid folder type")
        
    base_path = BASE_PATHS[folder_type]
    
    try:
        folders = []
        with os.scandir(base_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    stat = entry.stat()
                    folders.append(FolderInfo(
                        name=entry.name,
                        path=entry.path,
                        date_modified=datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y'),
                        status="Active",
                        notes=f"Inquiry {entry.name}"
                    ))
        return folders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/open-folder")
async def open_folder(path: str):
    try:
        if os.path.exists(path):
            if os.name == 'nt':
                os.startfile(path)
            else:
                os.system(f'xdg-open "{path}"')
            return {"status": "success"}
        else:
            raise HTTPException(status_code=404, detail="Folder not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add a health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}