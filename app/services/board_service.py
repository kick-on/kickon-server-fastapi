from app.models.board import Board
from sqlalchemy.orm import Session

def save_generated_post(db: Session, user_pk: int, title: str, contents: str, has_image: bool = False):
    post = Board(
        user_pk=user_pk,
        title=title,
        contents=contents,
        has_image=has_image,
        is_pinned=False 
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post