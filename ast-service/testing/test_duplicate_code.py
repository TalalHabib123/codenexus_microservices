import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
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
def no_duplicate_code_response():
    return {
        'conditionals': [],
        'success': True,
        'error': None
    }


@pytest.fixture
def duplicate_code_response_2():
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
        
        duplicate_code_response = DuplicateCodeResponse(**duplicate_code_response)
        assert validated_response == duplicate_code_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")



@pytest.mark.asyncio
async def test_no_duplicate_code(no_duplicate_code, no_duplicate_code_response):
   
    url = f"{BASE_URL}/duplicated-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_duplicate_code})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = DuplicateCodeResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        no_duplicate_code_response = DuplicateCodeResponse(**no_duplicate_code_response)
        assert validated_response ==  no_duplicate_code_response
        
    
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
        
            
        duplicate_code_response_2 = DuplicateCodeResponse(**duplicate_code_response_2)
        assert validated_response ==  duplicate_code_response_2
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")