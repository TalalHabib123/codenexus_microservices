import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
from app.models.ast_models import InconsistentNamingResponse

@pytest.fixture
def sample_snake_case():
 return """
def my_function():
    my_variable = 10
    another_variable = 20
    return my_variable + another_variable
"""

@pytest.fixture
def sample_camel_case():
  return """
def myFunction():
    myVariable = 10
    anotherVariable = 20
    return myVariable + anotherVariable
"""

@pytest.fixture
def sample_pascal_case():
    return """
def MyFunction():
    MyVariable = 10
    AnotherVariable = 20
    return MyVariable + AnotherVariable
"""

@pytest.fixture
def sample_mixed_case():
    return """
def my_function():
    myVariable = 10
    AnotherVariable = 20
    SomeVariable = 30
    anotherVariable = 40
    wishVariable = 50
    return myVariable + AnotherVariable+ SomeVariable + anotherVariable
"""

@pytest.fixture
def naming_convention_response():
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
def no_dead_code_response():
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
async def test_sample_snake_case(sample_snake_case, naming_convention_response):
    url = f"{BASE_URL}/naming-convention"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_snake_case})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = InconsistentNamingResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        naming_convention_response = InconsistentNamingResponse(**naming_convention_response)
        assert validated_response == naming_convention_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")



@pytest.mark.asyncio
async def test_sample_camel_case(sample_camel_case, naming_convention_response):
    url = f"{BASE_URL}/naming-convention"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_camel_case})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = InconsistentNamingResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        naming_convention_response = InconsistentNamingResponse(**naming_convention_response)
        assert validated_response == naming_convention_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")


@pytest.mark.asyncio
async def test_sample_pascal_case(sample_pascal_case, naming_convention_response):
    url = f"{BASE_URL}/naming-convention"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_pascal_case})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = InconsistentNamingResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        naming_convention_response = InconsistentNamingResponse(**naming_convention_response)
        assert validated_response == naming_convention_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}") 

@pytest.mark.asyncio
async def test_sample_mixed_case(sample_mixed_case, naming_convention_response):
    url = f"{BASE_URL}/naming-convention"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_mixed_case})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = InconsistentNamingResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        naming_convention_response = InconsistentNamingResponse(**naming_convention_response)
        assert validated_response == naming_convention_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}") 