
import shutil
from fastapi import HTTPException, UploadFile


def save_image(image: UploadFile):
    # Check if the image is valid
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file type")

    # Save the image
    image_path = f"images/{image.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return image_path