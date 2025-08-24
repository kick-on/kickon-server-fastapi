from openai import OpenAI
from app.core.config import settings
from typing import List
from app.rag.query_search import search_comments
from app.db.sql.session import SessionLocal
from app.models.user_favorite_team import UserFavoriteTeam
import json
import re

client = OpenAI(api_key=settings.openai_api_key)

def generate_post_from_comments(team_name_kr: str, topic: str, comments: List[str]) -> str:
    context = "\n\n".join([f"- {c}" for c in comments])

    prompt = f"""
    너는 '{team_name_kr}' 팬인 축구 커뮤니티 유저야.

    지금부터 아래 주제에 대해 축구 커뮤니티 게시판에 쓸 짧은 글을 하나 써줘.
    주제: {topic}

    아래는 이 주제와 관련된 유튜브 댓글이야. 
    형식은 ‘영상 제목’에 대한 팬 반응: ‘댓글 내용’이야. 이걸 참고해서 글을 써줘.
    {context}

    요청 조건은 다음과 같아:
    
    - 먼저 **짧은 커뮤니티 스타일의 제목**을 만들어.** 정말 짧게 1~3단어로.
    - 다음 줄에 **실제 게시글 내용**을 한두 문장, 무조건 3줄 이하로만 써줘. 너무 길게 쓰지 마. 짧고 임팩트 있게 써.
    - 제목과 본문 모두 **한국 커뮤니티 말투**처럼 써줘. 너무 깔끔하거나 과하게 공손한 문장은 안돼
    - 진짜 사람이 쓴 것처럼 **말하듯이, 감정 섞인 말투, 투덜거림, 거친 표현, 욕, 줄임말, 드립**, 자유롭게 써도 돼.
    - 위 팬 반응을 참고하되, 실제 사실 정보를 확인해서 써줘.
    - '영상 제목'은 어떤 유튜브 영상에 대한 댓글인지를 알 수 있도록 정보를 준 것이니 꼭 글 내용에 포함할 필요는 없어.

    - 반드시 다음의 JSON 형식으로 출력해줘:
    ```json
    {{
    "title": "...",
    "content": "..."
    }}

    """

    response = client.chat.completions.create(
        #model="gpt-3.5-turbo",
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    content = response.choices[0].message.content.strip()
    cleaned = strip_code_block(content)

    # JSON 파싱 시도
    try:
        parsed = json.loads(cleaned)
        title = parsed.get("title", "").strip()
        body = parsed.get("content", "").strip()
    except Exception as e:
        print(f"❌ JSON 파싱 실패: {e}")
        print("응답 내용:", cleaned)
        return {
            "title": topic,
            "contents": cleaned,
        }

    return {
        "title": title,
        "contents": body,
    }

def strip_code_block(text: str) -> str:
    # ```json ... ``` 같은 블록 제거
    return re.sub(r"^```json\s*|```$", "", text.strip(), flags=re.MULTILINE)

def run_rag_generation(user, topic):
    db = SessionLocal()

    favorite_team = (
        db.query(UserFavoriteTeam)
        .filter(UserFavoriteTeam.user_pk == user.pk)
        .order_by(UserFavoriteTeam.priority_num.asc())
        .first()
    )

    team_name_kr = favorite_team.team.name_kr if favorite_team else "중립"

    results = search_comments(topic, k=10)
    comment_texts = [doc.page_content for doc in results]

    user_with_team = {
        "nickname": user.nickname,
        "team_name_kr": team_name_kr,
    }

    generated_post = generate_post_from_comments(user_with_team, topic, comment_texts)
    return generated_post, comment_texts