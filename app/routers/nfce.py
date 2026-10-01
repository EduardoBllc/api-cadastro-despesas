from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas.nfce import ImportarNfce, RascunhoNfce
from app.services import nfce as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/nfce", tags=["nfce"])


@router.post("/importar", response_model=RascunhoNfce)
async def importar_nfce(
    body: ImportarNfce, session: AsyncSession = Depends(get_db)
) -> RascunhoNfce:
    """Lê a NFC-e do link do QR Code e devolve um rascunho de despesa (nada é gravado)."""
    return await service.importar(session, body.url)
