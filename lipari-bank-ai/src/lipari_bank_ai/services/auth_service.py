from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lipari_bank_ai.auth.passwords import verify_password
from lipari_bank_ai.auth.tokens import ACCESS_TOKEN_TTL, create_access_token
from lipari_bank_ai.db.models import AppUser
from lipari_bank_ai.exceptions import InvalidCredentialsError
from lipari_bank_ai.types.auth import TokenResponse


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def login(self, username: str, password: str) -> TokenResponse:
        """Verifica le credenziali ed emette un access token a scadenza.

        Credenziali sbagliate: 401, e il messaggio NON dice quale delle due era sbagliata.
        """
        user = await self.session.scalar(select(AppUser).where(AppUser.username == username))
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        token = create_access_token(subject=user.username, role=user.role)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=int(ACCESS_TOKEN_TTL.total_seconds()),
        )
