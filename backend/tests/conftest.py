import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock


def make_mock_collection():
    mock_collection = MagicMock()
    mock_collection.insert_one = AsyncMock(return_value=None)
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_collection.count_documents = AsyncMock(return_value=0)

    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_collection.find.return_value = mock_cursor

    return mock_collection


_mock_collection = make_mock_collection()


def _get_mock_collection(name):
    return _mock_collection


import backend.database as _db
_db.get_collection = _get_mock_collection


@pytest.fixture
def mock_db():
    _mock_collection.find_one = AsyncMock(return_value=None)
    _mock_collection.insert_one = AsyncMock(return_value=None)
    _mock_collection.count_documents = AsyncMock(return_value=0)
    return _mock_collection


@pytest_asyncio.fixture
async def client():
    from backend.main import app
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac