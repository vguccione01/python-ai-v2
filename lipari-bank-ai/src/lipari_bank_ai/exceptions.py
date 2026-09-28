class AppError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.headers = headers


class InvalidCredentialsError(AppError):
    def __init__(self) -> None:
        super().__init__(
            401,
            "INVALID_CREDENTIALS",
            "Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ChatSessionNotFoundError(AppError):
    def __init__(self, session_id: str) -> None:
        super().__init__(404, "CHAT_SESSION_NOT_FOUND", f"Sessione {session_id} non trovata")


class RateLimitError(AppError):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__(429, "RATE_LIMIT", f"Limite raggiunto. Riprova in {retry_after_seconds}s")
        self.retry_after = retry_after_seconds


class LLMProviderError(AppError):
    def __init__(self, provider: str, original: str) -> None:
        super().__init__(502, "LLM_PROVIDER_ERROR", f"Errore provider {provider}")
        self.original = original
