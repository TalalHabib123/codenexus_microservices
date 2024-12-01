import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
from app.models.ast_models import UnusedVariablesResponse, UnusedVariablesDetails

@pytest.fixture
def sample_one_unused_variable():
    return """
def my_function():
    myVariable = 10
    AnotherVariable = 20
    SomeVariable = 30
    anotherVariable = 40
    wishVariable = 50
    return myVariable + AnotherVariable + SomeVariable + anotherVariable
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
def sample_dead_conditional():
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
def sample_dead_variable():
    return """
def fun():
    print("This is a function")
    unusedVariable = 100
    
    var2=23
"""

@pytest.fixture
def unused_variable_response():
    unused_variable = UnusedVariablesDetails(variable_name="wishVariable", line_number=7)
    return {
        "unused_variables": [unused_variable],
        "success": True,
        "error": None,
    }

@pytest.fixture
def no_unused_variable_response():
    return {
        "unused_variables": [],
        "success": True,
        "error": None,
    }

@pytest.fixture
def sample_dead_variable_response():
    unused_variable1 = UnusedVariablesDetails(variable_name="unusedVariable", line_number=4)
    unused_variable2 = UnusedVariablesDetails(variable_name="var2", line_number=6)
    return {
        "unused_variables": [unused_variable1, unused_variable2],
        "success": True,
        "error": None,
    }

@pytest.mark.asyncio
async def test_one_unused_variable(sample_one_unused_variable, unused_variable_response):
    url = f"{BASE_URL}/unused-variables"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_one_unused_variable})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = UnusedVariablesResponse(**response_data)

        assert validated_response.success is True
        assert validated_response.error is None
        assert validated_response.unused_variables == unused_variable_response["unused_variables"]

    except ValidationError as e:
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_no_unused_variable(sample_no_variables, no_unused_variable_response):
    url = f"{BASE_URL}/unused-variables"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_no_variables})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = UnusedVariablesResponse(**response_data)

        assert validated_response.success is True
        assert validated_response.error is None
        assert validated_response.unused_variables == no_unused_variable_response["unused_variables"]

    except ValidationError as e:
        pytest.fail(f"Response validation failed: {e}")
        
@pytest.mark.asyncio
async def test_dead_var(sample_dead_variable, sample_dead_variable_response):
    url = f"{BASE_URL}/unused-variables"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_dead_variable})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = UnusedVariablesResponse(**response_data)

        assert validated_response.success is True
        assert validated_response.error is None
        assert validated_response.unused_variables == sample_dead_variable_response["unused_variables"]

    except ValidationError as e:
        pytest.fail(f"Response validation failed: {e}")
