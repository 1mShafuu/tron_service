import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch
from tronpy.exceptions import BadAddress, AddressNotFound
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_tron_client():
    client = AsyncMock()
    client.is_address = Mock(return_value=True)
    client.get_account = AsyncMock(return_value={"balance": 1500})
    client.get_account_resource = AsyncMock(return_value={
        'TotalNetLimit': 400,
        'TotalNetWeight': 100,
        'TotalEnergyLimit': 900,
        'TotalEnergyWeight': 200
    })
    return client


@pytest.mark.asyncio
async def test_get_address_info_success(client, mock_tron_client):
    test_data = {
        "input_address": "TEST_ADDR",
        "normalized_address": "TTestTestTestTestTestTestTest",
        "expected_response": {
            "address": "TTestTestTestTestTestTestTest",
            "balance": 1500,
            "bandwidth": 300,
            "energy": 700
        }
    }

    with patch('app.main.to_base58check_address', return_value=test_data["normalized_address"]), \
            patch('app.main.AsyncTron', return_value=mock_tron_client), \
            patch('app.main.get_db', new_callable=AsyncMock):
        response = client.post(
            "/address-info/",
            json={"address": test_data["input_address"]}
        )

        assert response.status_code == 200
        assert response.json() == test_data["expected_response"]


@pytest.mark.asyncio
async def test_invalid_address(client):
    with patch('app.main.to_base58check_address', side_effect=BadAddress("Invalid address")):
        response = client.post(
            "/address-info/",
            json={"address": "INVALID"}
        )

        assert response.status_code == 400
        assert "Invalid address" in response.json()["detail"]


@pytest.mark.asyncio
async def test_address_not_found(client, mock_tron_client):
    mock_tron_client.is_address.side_effect = AddressNotFound("Address not found")

    with patch('app.main.AsyncTron', return_value=mock_tron_client), \
            patch('app.main.to_base58check_address', return_value="TValidButNotFoundAddress"):
        response = client.post(
            "/address-info/",
            json={"address": "VALID_BUT_NOT_FOUND"}
        )

        assert response.status_code == 404
        assert "Address not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_internal_server_error(client, mock_tron_client):
    mock_tron_client.get_account.side_effect = Exception("Some error")

    with patch('app.main.AsyncTron', return_value=mock_tron_client), \
            patch('app.main.to_base58check_address', return_value="TTestAddress"):
        response = client.post(
            "/address-info/",
            json={"address": "TEST_ADDR"}
        )

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]