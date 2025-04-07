import pytest
from sqlalchemy import select
from app.models import AddressQuery
from app.database import async_session


@pytest.mark.asyncio
async def test_db_write(setup_db, client):
    async with async_session() as session:
        query = AddressQuery(address="TTestTestTestTestTestTestTest")
        session.add(query)
        await session.commit()

        result = await session.execute(select(AddressQuery))
        saved = result.scalars().first()
        assert saved.address == "TTestTestTestTestTestTestTest"