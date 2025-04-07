from sqlalchemy.ext.asyncio import AsyncSession
from tronpy import AsyncTron
from tronpy.keys import to_base58check_address
from tronpy.exceptions import ValidationError, BadAddress, AddressNotFound
from tronpy.providers import AsyncHTTPProvider
from app.models import AddressQuery
from app.schemas import AddressRequest, AddressInfoResponse, QueryResponse
from app.dependencies import get_db
from sqlalchemy import select
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from app.database import init_db
import logging
import uvicorn
from datetime import datetime, timezone
from typing import Optional

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


async def get_tron_client():
    provider = AsyncHTTPProvider(api_key="dea3880f-ce31-47be-ae66-ceefbc7dc7be")
    return AsyncTron(provider=provider)


async def log_query_to_db(
    db: AsyncSession,
    address: str,
    status: str = "success",
    error_message: Optional[str] = None
):
    try:
        query = AddressQuery(
            address=address,
            status=status,
            error_message=error_message
        )
        db.add(query)
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to log query to DB: {str(e)}")
        await db.rollback()
        raise


@app.post("/address-info/", response_model=AddressInfoResponse)
async def get_address_info(
        request: AddressRequest,
        db: AsyncSession = Depends(get_db),
        client: AsyncTron = Depends(get_tron_client)
):
    normalized_address = None
    try:
        # Нормализация адреса
        normalized_address = to_base58check_address(request.address)

        # Проверка валидности адреса
        if not client.is_address(normalized_address):
            await log_query_to_db(db, normalized_address, "failed", "Invalid address")
            raise ValidationError("Invalid address")

        # Получение данных
        account = await client.get_account(normalized_address)
        resources = await client.get_account_resource(normalized_address)

        # Расчет значений
        bandwidth = resources.get('TotalNetLimit', 0) - resources.get('TotalNetWeight', 0)
        energy = resources.get('TotalEnergyLimit', 0) - resources.get('TotalEnergyWeight', 0)

        # Запись успешного запроса в БД
        await log_query_to_db(db, normalized_address)

        return {
            "address": normalized_address,
            "balance": account.get("balance", 0),
            "bandwidth": bandwidth,
            "energy": energy
        }

    except BadAddress as e:
        error_msg = str(e)
        if normalized_address:
            await log_query_to_db(db, normalized_address, "failed", error_msg)
        logger.error(f"Address validation error: {error_msg}")
        raise HTTPException(400, detail=error_msg)
    except AddressNotFound:
        error_msg = "Address not found"
        if normalized_address:
            await log_query_to_db(db, normalized_address, "failed", error_msg)
        raise HTTPException(404, error_msg)
    except Exception as e:
        error_msg = "Internal server error"
        if normalized_address:
            await log_query_to_db(db, normalized_address, "failed", str(e))
        logger.error(f"API error: {str(e)}", exc_info=True)
        raise HTTPException(500, error_msg)


@app.get("/queries/", response_model=list[QueryResponse])
async def get_queries(
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(AddressQuery)
            .order_by(AddressQuery.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Failed to fetch queries: {str(e)}")
        raise HTTPException(500, "Failed to fetch queries")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)