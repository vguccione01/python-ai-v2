from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from lipari_bank_ai.db.session import get_db
from lipari_bank_ai.services.auth_service import AuthService
from lipari_bank_ai.types.auth import TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Authorization"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    return await AuthService(db).login(form.username, form.password)
