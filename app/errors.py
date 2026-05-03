import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        """Trata erros de violação de integridade do banco (ex: Unique Constraint)."""
        logger.warning(f"Erro de integridade: {exc}")
        message = str(exc.orig).lower()
        detail = "Erro de validação de dados no banco."

        if "unique constraint" in message:
            detail = "Um registro com estes dados já existe."
        elif "foreign key" in message:
            detail = "Operação não permitida: registro relacionado não encontrado ou em uso."

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": detail, "type": "integrity_error"},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Trata erros genéricos do SQLAlchemy (ex: erros de conexão)."""
        logger.error(f"Erro de banco de dados: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Serviço de banco de dados temporariamente indisponível.",
                "type": "database_error",
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Trata exceções HTTP disparadas manualmente (400, 404, etc)."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "type": "http_error"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Trata qualquer erro inesperado (500)."""
        logger.error(f"Erro não tratado: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Ocorreu um erro interno inesperado no servidor.",
                "type": "internal_error",
            },
        )
