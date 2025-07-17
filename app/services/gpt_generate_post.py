from openai import OpenAI
from app.core.config import settings
from typing import List
from app.services.query_search import search_comments
from app.db.session import SessionLocal
from app.models.user_favorite_team import UserFavoriteTeam
import json

client = OpenAI(api_key=settings.openai_api_key)

def generate_post_from_comments(team_name_kr: str, topic: str, comments: List[str]) -> str:
    context = "\n\n".join([f"- {c}" for c in comments])

    prompt = f"""
    너는 '{team_name_kr}' 팬인 축구 커뮤니티 유저야.

    지금부터 아래 주제에 대해 축구 커뮤니티 게시판에 쓸 짧은 글을 하나 써줘.
    주제: {topic}

    아래는 이 주제에 대해 유튜브 댓글에서 검색된 실제 팬들의 반응들이야. 이걸 참고해서 써줘.
    {context}

    - 먼저 **짧고 눈에 띄는 게시글 제목**을 한 줄로 만들어줘. 20자 이내로.
    - 다음 줄에 **실제 게시글 내용**을 한두 문장이면 돼. 무조건 3줄 이하로만 써줘. 길게 쓰지 마. 짧고 임팩트 있게 써.
    
    - **한국 커뮤니티 말투**처럼 써줘. 너무 깔끔하거나 과하게 공손한 문장은 안돼
    - 진짜 사람이 쓴 것처럼 **말하듯이, 감정 섞인 말투, 투덜거림, 거친 표현, 욕, 줄임말, 드립**, 자유롭게 써도 돼.
    - 위 팬 반응을 참고하되, 경기의 특징적인 순간이나 전반적인 흐름을 드러낼 수 있게 써줘.
    - 단순히 팀 이름에 대해 언급하는 건 하지마.

    - 반드시 다음의 JSON 형식으로 출력해줘: 
    ```json
    {{
    "title": "...",
    "content": "..."
    }}
    ```

    """

    response = client.chat.completions.create(
        #model="gpt-3.5-turbo",
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    content = response.choices[0].message.content.strip()

    # JSON 파싱 시도
    try:
        parsed = json.loads(content)
        title = parsed.get("title", "").strip()
        body = parsed.get("content", "").strip()
    except Exception as e:
        print(f"❌ JSON 파싱 실패: {e}")
        print("응답 내용:", content)
        return {
            "title": topic,
            "contents": content,
        }

    return {
        "title": title,
        "contents": body,
    }

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