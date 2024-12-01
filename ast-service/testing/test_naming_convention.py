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
def snake_case_response():
    return {
        "inconsistent_naming": [
            {
                "type": "snake_case",
                "total_count": 5,
                "type_count": 5,
                "vars": [
                    {"variable": "my_variable", "line_number": 3},
                    {"variable": "another_variable", "line_number": 4},
                    {"variable": "my_variable", "line_number": 5},
                    {"variable": "another_variable", "line_number": 5},
                    {"variable": "my_function", "line_number": 2},
                ],
            },
            {
                "type": "camel_case",
                "total_count": 5,
                "type_count": 0,
                "vars": [],
            },
            {
                "type": "pascal_case",
                "total_count": 5,
                "type_count": 0,
                "vars": [],
            },
        ],
        "success": True,
        "error": None,
    }
    
@pytest.fixture
def camel_case_response():
    return {
        "inconsistent_naming": [
            {
                "type": "snake_case",
                "total_count": 5,
                "type_count": 0,
                "vars": [],
            },
            {
                "type": "camel_case",
                "total_count": 5,
                "type_count": 5,
                "vars": [
                    {"variable": "myVariable", "line_number": 3},
                    {"variable": "anotherVariable", "line_number": 4},
                    {"variable": "myVariable", "line_number": 5},
                    {"variable": "anotherVariable", "line_number": 5},
                    {"variable": "myFunction", "line_number": 2},
                ],
            },
            {
                "type": "pascal_case",
                "total_count": 5,
                "type_count": 0,
                "vars": [],
            },
        ],
        "success": True,
        "error": None,
    }


@pytest.fixture
def pascal_case_response():
    return {
  "inconsistent_naming": [
    {
      "type": "snake_case",
      "total_count": 5,
      "type_count": 0,
      "vars": []
    },
    {
      "type": "camel_case",
      "total_count": 5,
      "type_count": 0,
      "vars": []
    },
    {
      "type": "pascal_case",
      "total_count": 5,
      "type_count": 5,
      "vars": [
        {
          "variable": "MyVariable",
          "line_number": 3
        },
        {
          "variable": "AnotherVariable",
          "line_number": 4
        },
        {
          "variable": "MyVariable",
          "line_number": 5
        },
        {
          "variable": "AnotherVariable",
          "line_number": 5
        },
        {
          "variable": "MyFunction",
          "line_number": 2
        }
      ]
    }
  ],
  "success": True,
  "error": None
}



@pytest.fixture
def mixed_case_response():
    return {
        "inconsistent_naming": [
            {
                "type": "snake_case",
                "total_count": 10,
                "type_count": 1,
                "vars": [
                    {"variable": "my_function", "line_number": 2},
                ],
            },
            {
                "type": "camel_case",
                "total_count": 10,
                "type_count": 5,
                "vars": [
                    {"variable": "myVariable", "line_number": 3},
                    {"variable": "anotherVariable", "line_number": 6},
                    {"variable": "wishVariable", "line_number": 7},
                    {"variable": "myVariable", "line_number": 8},
                    {"variable": "anotherVariable", "line_number": 8},
                ],
            },
            {
                "type": "pascal_case",
                "total_count": 10,
                "type_count": 4,
                "vars": [
                    {"variable": "AnotherVariable", "line_number": 4},
                    {"variable": "SomeVariable", "line_number": 5},
                    {"variable": "AnotherVariable", "line_number": 8},
                    {"variable": "SomeVariable", "line_number": 8},
                ],
            },
        ],
        "success": True,
        "error": None,
    }




@pytest.mark.asyncio
async def test_sample_snake_case(sample_snake_case, snake_case_response):
    url = f"{BASE_URL}/naming-convention"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_snake_case})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = InconsistentNamingResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        snake_case_response = InconsistentNamingResponse(**snake_case_response)
        assert validated_response == snake_case_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")



@pytest.mark.asyncio
async def test_sample_camel_case(sample_camel_case, camel_case_response):
    url = f"{BASE_URL}/naming-convention"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_camel_case})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = InconsistentNamingResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        camel_case_response = InconsistentNamingResponse(**camel_case_response)
        assert validated_response == camel_case_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")


@pytest.mark.asyncio
async def test_sample_pascal_case(sample_pascal_case, pascal_case_response):
    url = f"{BASE_URL}/naming-convention"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_pascal_case})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = InconsistentNamingResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        pascal_case_response = InconsistentNamingResponse(**pascal_case_response)
        assert validated_response == pascal_case_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}") 

@pytest.mark.asyncio
async def test_sample_mixed_case(sample_mixed_case, mixed_case_response):
    url = f"{BASE_URL}/naming-convention"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_mixed_case})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = InconsistentNamingResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        mixed_case_response = InconsistentNamingResponse(**mixed_case_response)
        assert validated_response == mixed_case_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}") 