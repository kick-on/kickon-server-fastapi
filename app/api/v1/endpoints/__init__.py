from fastapi import APIRouter
from app.api.v1.endpoints import generate, crawl, schedule

api_router = APIRouter()
api_router.include_router(generate.router)
api_router.include_router(crawl.router)
api_router.include_router(schedule.router)