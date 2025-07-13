from sqlalchemy.orm import Session
from app.models.user import User
import random

def get_random_ai_user(db: Session):
    users = db.query(User).filter(
        User.provider == 'AI',
        User.status == 'ACTIVATED'
    ).all()

    return random.choice(users) if users else None