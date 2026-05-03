from fastapi import APIRouter, Request

from app.database import check_db_health

router = APIRouter(tags=["ops"])


@router.get("/status")
async def get_status(request: Request) -> dict:
    db_health = await check_db_health(request.app.state.engine)
    return {"api": "ok", "database": db_health}
