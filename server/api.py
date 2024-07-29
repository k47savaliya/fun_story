from fastapi import APIRouter
from server.api_v1.endpoints.user import user_router
from server.api_v1.endpoints.story import story_router

api_router = APIRouter()

api_router.include_router(user_router, include_in_schema=True)
api_router.include_router(story_router, prefix="/stories", tags=["stories"])