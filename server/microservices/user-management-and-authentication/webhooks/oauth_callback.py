from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

@router.get("/oauth/github/callback")
async def github_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code parameter")
    # return the code in the response.
    return {"code": code}

