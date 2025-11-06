from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.schemas.auth import UserOut
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(id=user.id, email=user.email, username=user.username)
