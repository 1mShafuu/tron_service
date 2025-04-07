import pytest
from app.schemas import AddressRequest, AddressInfoResponse, QueryResponse


def test_address_request_schema():
    data = {"address": "TTestAddress"}
    request = AddressRequest(**data)
    assert request.address == "TTestAddress"


def test_address_info_response_schema():
    data = {
        "address": "TTestAddress",
        "balance": 1000,
        "bandwidth": 500,
        "energy": 300
    }
    response = AddressInfoResponse(**data)
    assert response.address == "TTestAddress"
    assert response.balance == 1000


def test_query_response_schema():
    from datetime import datetime
    data = {
        "id": 1,
        "address": "TTestAddress",
        "status": "success",
        "error_message": None,
        "created_at": datetime.now()
    }
    response = QueryResponse(**data)
    assert response.id == 1
    assert response.address == "TTestAddress"