from fastapi import APIRouter, HTTPException
from app.services.gpt_generate_post import generate_fan_post_from_user
from app.api.v1.schemas.generate import GeneratePostRequest
from app.data.fake_users import fake_users 

router = APIRouter()

fake_user_ids = [f"user_{i}" for i in range(1, 101)]  # 간단한 가상 유저 풀

@router.post("/generate-post", tags=["Generate"])
def generate_post(req: GeneratePostRequest):
    # user_id로 유저 정보 찾기
    user = next((u for u in fake_users if u["id"] == req.user_id), None)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    content = generate_fan_post_from_user(user, req.topic)

    return {
        "user_id": user["id"],
        "nickname": user["nickname"],
        "team": user["team"],
        "style": user["style"],
        "topic": req.topic,
        "content": content
    }