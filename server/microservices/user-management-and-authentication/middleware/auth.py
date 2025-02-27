from fastapi import Request, HTTPException
import jwt
import os

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise Exception("JWT_SECRET_KEY environment variable is not set!")

ALGORITHM = "HS256"

async def authMiddleware(request: Request, call_next):
    authorization: str = request.headers.get("Authorization")
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = payload.get("user_id")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    else:
        request.state.user_id = None
    response = await call_next(request)
    return response

