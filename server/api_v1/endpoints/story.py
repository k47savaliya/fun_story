import base64
import os
import shutil
from typing import Optional, Union
import uuid
from fastapi import FastAPI, Depends, File, Form, HTTPException, APIRouter, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from server import crud, schemas
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from server.utils.auth import get_current_user
from server.config import settings
from server.utils.common import save_image

from ..deps import get_db

story_router = APIRouter()
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".png", ".jpeg", ".jpg"}

imagekit = ImageKit(
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    url_endpoint=settings.IMAGEKIT_UPLOAD_URL,
)

options = UploadFileRequestOptions(
    use_unique_file_name=True,
    overwrite_file=True,
)

# JSONify the story response
def jsonify_story_response(stories):
    if not isinstance(stories, list):
        stories = [stories]
    return [{
        "id":story.id,
        "title":story.title,
        "contributions":story.contributions,
        "image_path": story.story_image,
        "created_by":story.created_by
        }for story in stories
    ]


@story_router.post("/create")
def create_story(
    story: schemas.StoryCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Create a new story
    """

    try:
        # Update the story object with the current user
        story_obj = crud.story.create(
            db,
            obj_in=schemas.StoryBase(
                title=story.title,
                contributions=story.contributions,
                created_by=story.created_by,
            ),
        )

        # Return the response
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": jsonify_story_response(story_obj),
                "message": "Story created successfully!",
            },
        )
    
    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()

@story_router.post("/upload-image")
def upload_image(
    image: UploadFile = File(...),
    title: str = Form(),
    created_by: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Upload an image
    """

    try:
        # Validate file type
        file_extension = os.path.splitext(image.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Invalid file type. Only .png, .jpeg, and .jpg are allowed.",
                },
            )

        # Validate image size
        image_size = len(image.file.read())
        if image_size > MAX_IMAGE_SIZE:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Image size exceeds the allowed limit of 5MB.",
                },
            )
        
        file_id = str(uuid.uuid4())
        
        image_data = image.file.read()
        image_result = imagekit.upload_file(
            file=base64.b64encode(image_data).decode(),
            file_name=f"{file_id}_image",
            options=options,
        )

        image_path = image_result.__dict__
        image_path = image_path.get("url")
        story_obj = crud.story.create(
            db,
            obj_in=schemas.StoryBase(
                title=title,
                contributions=[],
                created_by=created_by,
                story_image=image_path,
            ),
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": jsonify_story_response(story_obj),
                "message": "Image uploaded successfully!",
            },
        )
    
    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@story_router.put("/update")
def update_story(
    story_id: str, 
    story: schemas.StoryUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update a story
    """

    try:
        # Fetch story by ID
        story_obj = crud.story.get_by_id(db, id=story_id)
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")

        # Update the story object
        story_obj = crud.story.update(db, db_obj=story_obj, obj_in=story)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": jsonify_story_response(story_obj),
                "message": "Story updated successfully!",
            },
        )
    
    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@story_router.delete("/delete")
def delete_story(
    story_id: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a story
    """

    try:
        # Fetch story by ID
        story_obj = crud.story.get_by_id(db, id=story_id)
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")

        # Delete the story object
        story_obj = crud.story.remove(db, id=story_id)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Story deleted successfully!",
            },
        )
    
    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@story_router.get("/get-all-stories")
def read_stories(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all stories
    """

    try:
        # Fetch all stories
        stories = crud.story.get_multi(db)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": jsonify_story_response(stories),
                "message": "Stories fetched successfully!",
            },
        )
    
    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@story_router.get("/get-by-id")
def read_story(
    story_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a story by ID
    """

    try:
        # Fetch story by ID
        story = crud.story.get_by_id(db, id=story_id)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": jsonify_story_response(story),
                "message": "Story fetched successfully!",
            },
        )
    
    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@story_router.post("/add-contribution", response_model=schemas.StoryBase)
def add_contribution(
    story_id: str, 
    contribution: schemas.Contribution, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """
    Add a contribution to a story
    """

    try:
        # Fetch story by ID
        story = crud.story.get_by_id(db, id=story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")

        if story.contributions is None:
            story.contributions = []

        # Add contribution to the story
        stories = story.contributions.copy()
        stories.append(contribution.dict())

        # Update the story with the new contribution
        story.contributions = stories
        db.commit()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": jsonify_story_response(story),
                "message": "Contribution added successfully!",
            },
        )
    
    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()