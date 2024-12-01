import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
from app.models.ast_models import MagicNumbersResponse

@pytest.fixture
def sample_no_magic_number():
    return """
def fun():
    print("This is a function")
    x = 10
    y = 20
    if (x > 5) and (y < 10):
        print("This is borderline complex")
    return True

print("Hello world")
"""

@pytest.fixture
def sample_multiple_occurrences():
    return """
def fun():
    print("This is a function")
    x = 25
    y = 25
    if (x > 25) and (y < 10):
        print("This is borderline complex")
    return True

print("Hello world")
fun()
"""

@pytest.fixture
def sample_magic_number_varied():
    return """
def fun():
    x = 10
    y = 20
    z = [30, 10, 50]
    if x > 5:
        print("Magic number detected")
        y=10
    return x + y + z[0]
"""

@pytest.fixture
def sample_magic_number_args():
    return """
def fun(x=10, y=20):
    if x > 5:
        print("Magic number in arguments")
    return x + y
"""

@pytest.fixture
def no_magic_number_response():
    return {
        'magic_numbers': [],
        'success': True,
        'error': None
    }


@pytest.fixture
def multiple_occurrences_response():
    return {
        'magic_numbers': [
            {'magic_number': 25, 'line_number': 4},
            {'magic_number': 25, 'line_number': 5},
            {'magic_number': 25, 'line_number': 6}
        ],
        'success': True,
        'error': None
    }

@pytest.fixture
def magic_number_varied_response():
    return {
        'magic_numbers': [
            {'magic_number': 10, 'line_number': 3},
            {'magic_number': 20, 'line_number': 4},
            {'magic_number': 30, 'line_number': 5},
            {'magic_number': 10, 'line_number': 6},
            {'magic_number': 10, 'line_number': 8}
        ],
        'success': True,
        'error': None
    }

@pytest.fixture
def magic_number_args_response():
    return {
        'magic_numbers': [
            {'magic_number': 10, 'line_number': 2},
            {'magic_number': 20, 'line_number': 2},
            {'magic_number': 5, 'line_number': 3}
        ],
        'success': True,
        'error': None
    }

@pytest.mark.asyncio
async def test_no_magic_number(sample_no_magic_number, no_magic_number_response):
    url = f"{BASE_URL}/magic-numbers"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_no_magic_number})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = MagicNumbersResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dict() == no_magic_number_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_sample_multiple_occurrences(sample_multiple_occurrences, multiple_occurrences_response):
    url = f"{BASE_URL}/magic-numbers"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_multiple_occurrences})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = MagicNumbersResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dict() == multiple_occurrences_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_sample_magic_number_varied(sample_magic_number_varied, magic_number_varied_response):
    url = f"{BASE_URL}/magic-numbers"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_magic_number_varied})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = MagicNumbersResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dict() == magic_number_varied_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_sample_magic_number_args(sample_magic_number_args, magic_number_args_response):
    url = f"{BASE_URL}/magic-numbers"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_magic_number_args})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = MagicNumbersResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dict() == magic_number_args_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")