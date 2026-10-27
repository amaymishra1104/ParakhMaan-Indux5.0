import os
import uuid
import shutil
from fastapi import UploadFile
from app.core.config import settings

class StorageService:
    """
    Local storage service with abstraction for MinIO/S3.
    """

    def __init__(self):
        self.upload_dir = os.path.join(settings.STORAGE_DIR, "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_upload(self, file: UploadFile, inspection_id: str) -> str:
        insp_dir = os.path.join(self.upload_dir, inspection_id)
        os.makedirs(insp_dir, exist_ok=True)

        ext = os.path.splitext(file.filename or "")[1]
        if not ext:
            ext = ".jpg"
        
        unique_filename = f"{uuid.uuid4()}{ext}"
        target_path = os.path.join(insp_dir, unique_filename)

        content = await file.read()
        with open(target_path, "wb") as out_file:
            out_file.write(content)

        return target_path

    def save_bytes(self, image_bytes: bytes, inspection_id: str, filename: str = "capture.jpg") -> str:
        insp_dir = os.path.join(self.upload_dir, inspection_id)
        os.makedirs(insp_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4()}_{filename}"
        target_path = os.path.join(insp_dir, unique_filename)

        with open(target_path, "wb") as out_file:
            out_file.write(image_bytes)

        return target_path

    def get_relative_url(self, file_path: str) -> str:
        # Converts local absolute path to static served URL
        normalized = file_path.replace("\\", "/")
        if "storage" in normalized:
            idx = normalized.find("storage")
            return "/" + normalized[idx:]
        return file_path

storage_service = StorageService()
