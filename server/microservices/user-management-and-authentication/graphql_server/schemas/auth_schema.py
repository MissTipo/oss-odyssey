import strawberry

@strawberry.type
class Token:
    access_token: str
    token_type: str

@strawberry.input
class RegisterInput:
    username: str
    email: str
    password: str

@strawberry.input
class LoginInput:
    email: str
    password: str

