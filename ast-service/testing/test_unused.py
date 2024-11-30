import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
from app.models.ast_models import UnusedVariablesResponse

@pytest.fixture
def sample_one_unused_variable():
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
def sample_no_variables():
    return """
def fun():
    print("This is a function")
    return True

print("Hello world")
"""

@pytest.fixture
def sample_dead(): #consider the unsued variables in dead code 
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
def unused_variable_reponse():
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
def no_unused_variable_reponse():
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
async def test_one_unused_variable(sample_one_unused_variable, unused_variable_reponse):
   
    url = f"{BASE_URL}/unused-variables"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_one_unused_variable})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = UnusedVariablesResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        unused_variable_reponse = UnusedVariablesResponse(**unused_variable_reponse)
        assert validated_response ==  unused_variable_reponse
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")



@pytest.mark.asyncio
async def test_no_unused_variable(sample_no_variables, no_unused_variable_reponse):
   
    url = f"{BASE_URL}/unused-variables"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_no_variables})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = UnusedVariablesResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        no_unused_variable_reponse = UnusedVariablesResponse(**no_unused_variable_reponse)
        assert validated_response ==  no_unused_variable_reponse
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

        
@pytest.mark.asyncio
async def test_no_dead_code(sample_dead, unused_variable_reponse):
   
    url = f"{BASE_URL}/unused-variables"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_dead})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = UnusedVariablesResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        unused_variable_reponse = UnusedVariablesResponse(**unused_variable_reponse)
        assert validated_response ==  unused_variable_reponse
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")