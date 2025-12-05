from fastapi import FastAPI, UploadFile, File, Form
import zipfile
import io
import base64
import mimetypes
import os

app = FastAPI()

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff", ".tif"}

@app.post("/unzip")
async def unzip_file(
    file: UploadFile = File(...),
    images_only: bool = Form(False)
):
    contents = await file.read()
    zip_bytes = io.BytesIO(contents)

    result = []

    try:
        with zipfile.ZipFile(zip_bytes, "r") as z:
            for name in z.namelist():
                if name.endswith("/"):
                    continue

                ext = os.path.splitext(name)[1].lower()
                if images_only and ext not in IMAGE_EXTS:
                    continue

                data = z.read(name)
                mime, _ = mimetypes.guess_type(name)

                result.append({
                    "filename": name,
                    "mime_type": mime or "application/octet-stream",
                    "base64": base64.b64encode(data).decode("utf-8")
                })

        return {"files": result}

    except zipfile.BadZipFile:
        return {"error": "Invalid ZIP file"}
