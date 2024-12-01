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
    print("Some number")
    if 25 > 20:
        x = 25
    if 25 < 30:
        y = 25
    print(25)
    return True

print("Hello world")
fun() 
"""

@pytest.fixture
def sample_magic_number_varied():
    return """ 
def fun():
    x = 10
    z = [30, 10, 50]
    print(10)
    if 10 > 5:
        print("Multiple 10s")
    return x + 10 
"""

@pytest.fixture
def sample_magic_number_args():
    return """ 
def fun():
    print(10)
    if 10 > 5:
        print("Multiple 10s")
    z = 10
    return 10 
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
            {'magic_number': 25, 'line_number': 4}
        ],
        'success': True,
        'error': None
    }

@pytest.fixture
def magic_number_varied_response():
    return {
        'magic_numbers': [
            {'magic_number': 10, 'line_number': 5}
        ],
        'success': True,
        'error': None
    }

@pytest.fixture
def magic_number_args_response():
    return {
        'magic_numbers': [
            {'magic_number': 10, 'line_number': 3}
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