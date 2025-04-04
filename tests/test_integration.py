import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.mark.asyncio
async def test_address_info(client: TestClient, mocker):
    mock_tron = mocker.patch("app.main.AsyncTron")
    mock_client = mock_tron.return_value.__aenter__.return_value
    mock_client.get_account.return_value = {"balance": 1000}
    mock_client.get_account_resource.return_value = {
        "free_net_limit": 500,
        "energy_limit": 200
    }

    response = client.post(
        "/address-info/",
        json={"address": "TEST_ADDRESS"}
    )
    assert response.status_code == 200

    response = client.get("/queries/?skip=0&limit=10")
    assert response.status_code == 200
    assert len(response.json()) == 1