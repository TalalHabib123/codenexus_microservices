import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
from app.models.ast_models import DeadCodeResponse

@pytest.fixture
def sample_code_dead():
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
def sample_code_active():
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
def sample_code_dead_imports():
    return """
import os
import sys

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
def dead_imports_response():
    return {
        'function_names': ['fun'],
        'class_details': [],
        'global_variables': [],
        'imports': {
            'dead_imports': [{'alias': 'os', 'original': 'os', 'items': []}, {'alias': 'sys', 'original': 'sys', 'items': []}], 
            'unused_imports': []
        },
        'success': True,
        'error': None
    }


@pytest.fixture
def dead_code_response():
    return {
        'function_names': ['fun'],
        'class_details': [],
        'global_variables': [],
        'imports': {
            'dead_imports': [],
            'unused_imports': []
        },
        'success': True,
        'error': None
    }

@pytest.fixture
def no_dead_code_response():
    return {
        'function_names': [],
        'class_details': [],
        'global_variables': [],
        'imports': {
            'dead_imports': [],
            'unused_imports': []
        },
        'success': True,
        'error': None
    }


@pytest.mark.asyncio
async def test_dead_code(sample_code_dead, dead_code_response):
    url = f"{BASE_URL}/dead-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_code_dead, "function_names": ["fun"] , "global_variables": []})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = DeadCodeResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        dead_code_response = DeadCodeResponse(**dead_code_response)
        assert validated_response == dead_code_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")



@pytest.mark.asyncio
async def test_not_complex_conditionals(sample_code_active, no_dead_code_response):
   
    url = f"{BASE_URL}/dead-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_code_active, "function_names": ["fun"] , "global_variables": []})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = DeadCodeResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        no_dead_code_response = DeadCodeResponse(**no_dead_code_response)
        assert validated_response ==  no_dead_code_response
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_dead_imports(sample_code_dead_imports, dead_imports_response):
    url = f"{BASE_URL}/dead-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_code_dead_imports, "function_names": ["fun"] , "global_variables": []})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = DeadCodeResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        dead_imports_response = DeadCodeResponse(**dead_imports_response)
        assert validated_response == dead_imports_response
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

