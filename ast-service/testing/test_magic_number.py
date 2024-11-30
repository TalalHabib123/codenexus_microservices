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
def sample_multiple_occurrences(): #Multiple Occurrences of the Same c Number
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
def sample_magic_number_varied(): #Magic Numbers in Different Contexts
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
def sample_magic_number_args(): #Magic Numbers in Function Arguments
    return """
def fun(x=10, y=20):
    if x > 5:
        print("Magic number in arguments")
    return x + y
"""
@pytest.fixture
def magic_number_reponse():
    return {
        'conditionals': [
            {
                'line_range': (2, 7),
                'condition_code': '(a > 10) and (b < 5)',
                'complexity_score': 4,
                'code_block': 'if (a > 10) and (b < 5):\n    if (c == 1):\n        if (d != 0):\n            if (e in range(5)):\n                if (f == True):\n                    print("Nested conditionals!")\n'
            },
            {
                'line_range': (3, 7),
                'condition_code': '(c == 1)',
                'complexity_score': 1,
                'code_block': 'if (c == 1):\n        if (d != 0):\n            if (e in range(5)):\n                if (f == True):\n                    print("Nested conditionals!")\n'
            },
            {
                'line_range': (4, 7),
                'condition_code': '(d != 0)',
                'complexity_score': 1,
                'code_block': 'if (d != 0):\n            if (e in range(5)):\n                if (f == True):\n                    print("Nested conditionals!")\n'
            },
            {
                'line_range': (6, 7),
                'condition_code': '(f == True)',
                'complexity_score': 1,
                'code_block': 'if (f == True):\n                    print("Nested conditionals!")\n'
            }
        ],
        'success': True,
        'error': None
    }

@pytest.fixture
def no_magic_number_reponse():
    return {
        'conditionals': [],
        'success': True,
        'error': None
    }


@pytest.fixture
def active_dead_classes_response():
    return {
        'conditionals': [
            {
                'line_range': (2, 3),
                'condition_code': '(x > 5) and (y < 10)',
                'complexity_score': 2,
                'code_block': 'if (x > 5) and (y < 10):\n    print("This is borderline complex")\n'
            }
        ],
        'success': True,
        'error': None
    }



@pytest.mark.asyncio
async def test_no_magic_number(sample_no_magic_number, magic_number_reponse):
    url = f"{BASE_URL}/magic_number"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_no_magic_number})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response =MagicNumbersResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        magic_number_reponse =MagicNumbersResponse(**magic_number_reponse)
        assert validated_response == magic_number_reponse
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")


@pytest.mark.asyncio
async def test_sample_multiple_occurrences(sample_multiple_occurrences, magic_number_reponse):
    url = f"{BASE_URL}/magic_number"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_multiple_occurrences})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response =MagicNumbersResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        magic_number_reponse =MagicNumbersResponse(**magic_number_reponse)
        assert validated_response == magic_number_reponse
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")





@pytest.mark.asyncio
async def test_sample_magic_number_varied(sample_magic_number_varied, magic_number_reponse):
    url = f"{BASE_URL}/magic_number"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_magic_number_varied})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response =MagicNumbersResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        magic_number_reponse =MagicNumbersResponse(**magic_number_reponse)
        assert validated_response == magic_number_reponse
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_sample_magic_number_args(sample_magic_number_args, magic_number_reponse):
    url = f"{BASE_URL}/magic_number"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_magic_number_args})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response =MagicNumbersResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        magic_number_reponse =MagicNumbersResponse(**magic_number_reponse)
        assert validated_response == magic_number_reponse
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")