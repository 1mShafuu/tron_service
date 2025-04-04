from sqlalchemy.ext.asyncio import AsyncSession
from tronpy import AsyncTron
from tronpy.keys import to_base58check_address
from tronpy.exceptions import AddressNotFound, ValidationError
from tronpy.providers import AsyncHTTPProvider
from .models import AddressQuery
from .schemas import AddressRequest, AddressInfoResponse, QueryResponse
from .dependencies import get_db
from sqlalchemy import select
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from .database import init_db
import logging

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


# Конфигурация Tron клиента

async def get_tron_client():
    provider = AsyncHTTPProvider(api_key="dea3880f-ce31-47be-ae66-ceefbc7dc7be")

    return AsyncTron(provider=provider)


@app.post("/address-info/", response_model=AddressInfoResponse)
async def get_address_info(
        request: AddressRequest,
        db: AsyncSession = Depends(get_db),
        client: AsyncTron = Depends(get_tron_client)
):
    try:
        # Нормализация и валидация адреса
        normalized_address = to_base58check_address(request.address)
        if not client.is_address(normalized_address):
            raise ValidationError("Invalid address format")

        # Получение данных из сети Tron
        account = await client.get_account(normalized_address)
        resources = await client.get_account_resource(normalized_address)

        # Запись в БД
        query = AddressQuery(address=normalized_address)
        db.add(query)
        await db.commit()

        return {
            "address": normalized_address,
            "balance": account.get("balance", 0),
            "bandwidth": resources.get("free_net_limit", 0),
            "energy": resources.get("energy_limit", 0),
        }

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(400, detail=str(e))
    except AddressNotFound:
        raise HTTPException(404, "Address not found in Tron network")
    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        raise HTTPException(500, "Internal server error")


@app.get("/queries/", response_model=list[QueryResponse])
async def get_queries(
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AddressQuery)
        .order_by(AddressQuery.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
