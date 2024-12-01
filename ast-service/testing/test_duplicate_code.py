import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.models.ast_models import DuplicateCodeResponse

@pytest.fixture
def sample_duplicate_code():
    return """
def fun():
    print("This is a function")
    x = 10
    y = 20
    if (x > 5) and (y < 10):
        print("This is borderline complex")
    return True
    
def fun2():
    print("This is not a function")
    x = 20
    y = 30
    if (x > 5) and (y < 10):
        print("This is borderline complex")
    return True
print("Hello world")
"""

@pytest.fixture
def no_duplicate_code():
    return """
def fun():
    print("This is a function")
    x = 10
    y = 20
    if (x > 5) and (y < 10):
        print("This is borderline complex")
    return True

print("Hello world")
fun()
"""

@pytest.fixture
def sample_duplicate_code2():
    return """
def fun():
    print("This is a function")
    x = 10
    y = 20
    if (x > 5) and (y < 10):
        print("This is borderline complex")
    return True
    
def fun2():
    print("This is a function")
    x = 10
    y = 20
    if (x > 5) and (y < 10):
        print("This is borderline complex")
    return True

fun()
fun2()
"""

@pytest.fixture
def duplicate_code_response():
    return {
               'duplicate_code': [
            {
                'original_code':'if (x > 5) and (y < 10):\nprint("This is borderline complex")\nreturn True',
                'start_line': 6,
                'end_line': 8,
                'duplicates': [
                    {
                        'code': 'if (x > 5) and (y < 10):\nprint("This is borderline complex")\nreturn True',
                        'start_line': 14,
                        'end_line': 16
                    }
                ],
                'duplicate_count': 1
            }
        ],
        'success': True,
        'error': None
    }

@pytest.fixture
def no_duplicate_code_response():
    return {
        'duplicate_code': [],
        'success': True,
        'error': None
    }

@pytest.fixture
def duplicate_code_response_2():
    return {
        'duplicate_code': [
            {
                'original_code':'print("This is a function")\nx = 10\ny = 20\nif (x > 5) and (y < 10):\nprint("This is borderline complex")\nreturn True\n',
                'start_line': 3,
                'end_line': 9,
                'duplicates': [
                    {
                        'code': 'print("This is a function")\nx = 10\ny = 20\nif (x > 5) and (y < 10):\nprint("This is borderline complex")\nreturn True\n',
                        'start_line': 11,
                        'end_line': 17
                    }
                ],
                'duplicate_count': 1
            }
        ],
        'success': True,
        'error': None
    }

@pytest.mark.asyncio
async def test_duplicate_code(sample_duplicate_code, duplicate_code_response):
    url = f"{BASE_URL}/duplicated-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_duplicate_code})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = DuplicateCodeResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dict() == duplicate_code_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_no_duplicate_code(no_duplicate_code, no_duplicate_code_response):
    url = f"{BASE_URL}/duplicated-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": no_duplicate_code})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = DuplicateCodeResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dict() == no_duplicate_code_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_2_duplicate_code(sample_duplicate_code2, duplicate_code_response_2):
    url = f"{BASE_URL}/duplicated-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_duplicate_code2})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = DuplicateCodeResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dict() == duplicate_code_response_2
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")