from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)

def generate_fan_post_from_user(user: dict, topic: str) -> str:
    prompt = f"""
    너는 '{user["team"]}' 팬인 '{user["nickname"]}'이라는 이름의 축구 커뮤니티 유저야. {user["style"]} 스타일로 글을 써.

    지금부터 아래 주제에 대해 **축구 커뮤니티 게시판에 쓸 짧은 댓글형 글**을 하나 써줘.

    - 너무 길게 말하지 말고, **0.5~2줄** 정도가 자연스러워.
    - **유튜브 축구 댓글**, **한국 커뮤니티 말투**처럼 써줘. 너무 깔끔하거나 과하게 공손한 문장은 안돼
    - **말하듯이, 줄임말, 감탄사, 드립, 투덜거림, 밈, 욕**, 자유롭게 써도 돼.
    - 진짜 사람이 쓴 것처럼 **감정 섞인 말투**, **거친 표현**도 괜찮아.
    - 특히 '{user["team"]}' 팬 분위기를 잘 담아줘.

    예시:
    살라 오늘 왤케 헤매냐 ㅋㅋㅋ 답답해서 미치는줄
    와 진짜 개지렸다 ㄹㅇ;; 이런 경기 또 언제 보냐
    감독 전술 진심 뭐냐;; 그냥 선수들 개고생

    주제:
    {topic}
    """

    response = client.chat.completions.create(
        #model="gpt-3.5-turbo",
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    return response.choices[0].message.content.strip()