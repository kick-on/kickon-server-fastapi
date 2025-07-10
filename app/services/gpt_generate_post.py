from openai import OpenAI
from app.core.config import settings
from typing import List
from app.services.query_search import search_comments

client = OpenAI(api_key=settings.openai_api_key)

def generate_post_from_comments(user: dict, topic: str, comments: List[str]) -> str:
    context = "\n\n".join([f"- {c}" for c in comments])

    prompt = f"""
    너는 '{user["team"]}' 팬인 축구 커뮤니티 유저야.

    지금부터 아래 주제에 대해 축구 커뮤니티 게시판에 쓸 짧은 댓글형 글을 하나 써줘.
    주제: {topic}

    아래는 이 주제에 대해 유튜브 댓글에서 검색된 실제 팬들의 반응들이야. 이걸 참고해서 써줘.
    {context}

    - **한국 커뮤니티 말투**처럼 써줘. 너무 깔끔하거나 과하게 공손한 문장은 안돼
    - 진짜 사람이 쓴 것처럼 **말하듯이, 감정 섞인 말투, 투덜거림, 거친 표현, 욕, 줄임말, 드립**, 자유롭게 써도 돼.
    - 한두 문장이면 돼. 무조건 2줄 이하로만 써. 길게 쓰지 마. 짧고 임팩트 있게 써.
    - 위 팬 반응을 참고하되, 경기의 특징적인 순간이나 전반적인 흐름을 드러낼 수 있게 써줘.
    - 경기의 특징적인 순간이나 반전에 대한 이야기를 드러낼 수 있게 써줘.
    - 예를 들어, 누가 골 넣었는지, 흐름이 어땠는지, 역전 상황 등 반전이 드러나는 포인트가 있으면 담아줘
    - 단순히 팀 이름에 대해 언급하는 건 하지마.
    """

    response = client.chat.completions.create(
        #model="gpt-3.5-turbo",
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    return response.choices[0].message.content.strip()

def run_rag_generation(user, topic):
    results = search_comments(topic, k=5)
    comment_texts = [doc.page_content for doc in results]
    return generate_post_from_comments(user, topic, comment_texts)