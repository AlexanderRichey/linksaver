from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    UnauthenticatedUser,
    AuthCredentials,
)
from .models import User


class CookieAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        session_id = request.session.get("id")
        if not session_id:
            return AuthCredentials(["unauthenticated"]), UnauthenticatedUser()

        user = User.get_by_session_id(session_id)
        if not user:
            return AuthCredentials(["unauthenticated"]), UnauthenticatedUser()

        return AuthCredentials(["authenticated"]), user
