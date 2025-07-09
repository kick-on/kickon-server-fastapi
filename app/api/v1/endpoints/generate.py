from fastapi import APIRouter, HTTPException
from app.api.v1.schemas.generate import GeneratePostRequest
from app.data.fake_users import fake_users
from app.services.gpt_generate_post import run_rag_generation

router = APIRouter()
fake_user_ids = [f"user_{i}" for i in range(1, 101)]

@router.post("/generate-post", tags=["Generate"])
def generate_post(req: GeneratePostRequest):
    user = next((u for u in fake_users if u["id"] == req.user_id), None)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        content = run_rag_generation(user, req.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "user_id": user["id"],
        "nickname": user["nickname"],
        "team": user["team"],
        "style": user["style"],
        "topic": req.topic,
        "content": content
    }