import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
from app.models.ast_models import LongParameterListResponse


@pytest.fixture
def sample_long_parameter_code():
    return """
def long_param_fun(a, b, c, d):
    return a + b + c + d

result = long_param_fun(1, 2, 3, 4)
print(result)
"""

@pytest.fixture
def no_long_parameter_code():
    return """
def simple_fun():
    print("This is a simple function with no long parameter list.")
    return True

simple_fun()
"""

@pytest.fixture
def border_long_param_code():
    return """
def complex_fun(a, b, c):
    print("This is a function with exactly three parameters.")
    return a * b + c

def another_fun():
    print("This is another simple function.")
    return True

result = complex_fun(2, 3, 4)
another_fun()
print(result)
"""



@pytest.fixture
def sample_long_parameter_response():
    return {
  "long_parameter_list": [
    {
      "function_name": "long_param_fun",
      "parameters": ["a", "b", "c", "d"],
      "long_parameter_count": 4,
      "long_parameter": True,
      "line_number": 2
    }
  ],
  "success": True,
  "error": None
}


@pytest.fixture
def no_long_parameter_response():
    return {
    "long_parameter_list": [
    {
      "function_name": "simple_fun",
      "parameters": [],
      "long_parameter_count": 0,
      "long_parameter": False,
      "line_number": 2
    }],
    "success": True,
    "error": None
}
    
    



@pytest.fixture
def border_long_param_response_2():
    return {
  "long_parameter_list": [
    {
      "function_name": "complex_fun",
      "parameters": ["a", "b", "c"],
      "long_parameter_count": 3,
      "long_parameter": False,
      "line_number": 2
    },
    {
        "function_name": "another_fun",
        "parameters": [],
        "long_parameter_count": 0,
        "long_parameter": False,
        "line_number": 6
    }
  ],
  "success": True,
  "error": None
}




@pytest.mark.asyncio
async def test_long_param_code(sample_long_parameter_code, sample_long_parameter_response):
    url = f"{BASE_URL}/parameter-list"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_long_parameter_code})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = LongParameterListResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        sample_long_parameter_response = LongParameterListResponse(**sample_long_parameter_response)
        assert validated_response == sample_long_parameter_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")



@pytest.mark.asyncio
async def test_no_long_param_code(no_long_parameter_code, no_long_parameter_response):
   
    url = f"{BASE_URL}/parameter-list"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": no_long_parameter_code})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = LongParameterListResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        no_long_parameter_response = LongParameterListResponse(**no_long_parameter_response)
        assert validated_response ==  no_long_parameter_response
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")


@pytest.mark.asyncio
async def test_border_long_param_code(border_long_param_code, border_long_param_response_2):
   
    url = f"{BASE_URL}/parameter-list"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": border_long_param_code})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = LongParameterListResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        border_long_param_response_2 = LongParameterListResponse(**border_long_param_response_2)
        assert validated_response ==  border_long_param_response_2
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")