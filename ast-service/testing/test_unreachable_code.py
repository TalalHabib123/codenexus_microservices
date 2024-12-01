import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
from app.models.ast_models import UnreachableResponse

@pytest.fixture
def sample_unreachable_code():
    return """
def divide(a, b):
    if b == 0:
        return "Cannot divide by zero."
    return a / b
    print("This line is never reached.")

divide(10, 2)

"""

@pytest.fixture
def no_unreachable_code():
    return """
def categorize_number(num):
    if num > 0:
        return "Positive"
    elif num < 0:
        return "Negative"
    else:
        return "Zero"

# All cases are logically reachable
print(categorize_number(5))
"""


@pytest.fixture
def sample_unreachable_code2():
    return """
def nested_conditions(flag):
    if flag:
        return "Flag is True"
        print("This is unreachable 1")  # Unreachable due to `return`
    else:
        return "Flag is False"
        print("This is unreachable 2")  # Unreachable due to `return`

    print("End of function.")  # Completely unreachable code outside logic flow

nested_conditions(True)
"""



@pytest.fixture
def unreachable_code_response():
    return {
        'unreachable_code': [
                "Unreachable code at line 6"
        ],
        'success': True,
        'error': None
    }

@pytest.fixture
def no_unreachable_code_response():
    return {
        'unreachable_code': [],
        'success': True,
        'error': None
    }


@pytest.fixture
def unreachable_code_response_2():
    return {
        'unreachable_code': [
                "Unreachable code at line 5",
                "Unreachable code at line 8",
                "Unreachable code at line 10"
        ],
        'success': True,
        'error': None
    }



@pytest.mark.asyncio
async def test_unreachable_code(sample_unreachable_code, unreachable_code_response):
    url = f"{BASE_URL}/unreachable-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_unreachable_code})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = UnreachableResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        unreachable_code_response = UnreachableResponse(**unreachable_code_response)
        assert validated_response == unreachable_code_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")



@pytest.mark.asyncio
async def test_no_unreachable_code(no_unreachable_code, no_unreachable_code_response):
   
    url = f"{BASE_URL}/unreachable-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": no_unreachable_code})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = UnreachableResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        no_unreachable_code_response = UnreachableResponse(**no_unreachable_code_response)
        assert validated_response ==  no_unreachable_code_response
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")


@pytest.mark.asyncio
async def test_2_unreachable_code(sample_unreachable_code2, unreachable_code_response_2):
   
    url = f"{BASE_URL}/unreachable-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_unreachable_code2})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = UnreachableResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        unreachable_code_response_2 = UnreachableResponse(**unreachable_code_response_2)
        assert validated_response ==  unreachable_code_response_2
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")