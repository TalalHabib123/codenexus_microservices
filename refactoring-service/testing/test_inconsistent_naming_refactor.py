import pytest
from endpoints_url import REFACTOR_SERVICE_URL
from pydantic import ValidationError
import httpx
from app.refactoring_models.refactor_models import RefactorResponse, Dependency, Weight

# Fixture for snake case code
@pytest.fixture
def snake_case_code():
    return """
def some_function():
    my_variable = 10
    return my_variable

class SomeClass:
    def another_method(self):
        local_var = 20
        return local_var
"""

# Fixture for camel case code
@pytest.fixture
def camel_case_code():
    return """
def someFunction():
    myVariable = 10
    return myVariable

class SomeClass:
    def anotherMethod(self):
        localVar = 20
        return localVar
"""

# Fixture for mixed convention code
@pytest.fixture
def mixed_convention_code():
    return """
def some_function():
    myVariable = 10
    another_var = 20
    localVal = 30
    return myVariable + another_var + localVal

class SomeClass:
    def another_method(self):
        some_local_var = 20
        anotherLocalVar = 30
        return some_local_var + anotherLocalVar
"""

# Fixture for mock dependency
@pytest.fixture
def mock_dependency():
    return {
        "name": "test_dependency.py",
        "valid": True,
        "fileContent": "def helper_function(): return 42",
        "weight": [
            {
                "name": "helper_function",
                "type": "function",
                "source": "Exporting"
            }
        ]
    }

# Expected response fixtures
@pytest.fixture
def snake_to_camel_response():
    return {
        'refactored_code': """
def someFunction():
    myVariable = 10
    return myVariable

class SomeClass:
    def anotherMethod(self):
        localVar = 20
        return localVar
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.fixture
def camel_to_snake_response():
    return {
        'refactored_code': """
def some_function():
    my_variable = 10
    return my_variable

class SomeClass:
    def another_method(self):
        local_var = 20
        return local_var
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.fixture
def mixed_to_snake_response():
    return {
        'refactored_code': """
def some_function():
    my_variable = 10
    another_var = 20
    local_val = 30
    return my_variable + another_var + local_val

class SomeClass:
    def another_method(self):
        some_local_var = 20
        another_local_var = 30
        return some_local_var + another_local_var
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.mark.asyncio
async def test_snake_to_camel_case(snake_case_code, snake_to_camel_response):
    """Test converting from snake_case to camelCase via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/inconsistent-naming"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": snake_case_code,
            "target_convention": "camelCase",
            "naming_convention": "auto-detect"
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "someFunction" in validated_response.refactored_code
        assert "myVariable" in validated_response.refactored_code
        assert "anotherMethod" in validated_response.refactored_code
        assert "localVar" in validated_response.refactored_code
        assert "some_function" not in validated_response.refactored_code
        assert "my_variable" not in validated_response.refactored_code
        
        expected_response = RefactorResponse(**snake_to_camel_response)
        assert validated_response.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_camel_to_snake_case(camel_case_code, camel_to_snake_response):
    """Test converting from camelCase to snake_case via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/inconsistent-naming"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": camel_case_code,
            "target_convention": "snake_case",
            "naming_convention": "auto-detect"
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "some_function" in validated_response.refactored_code
        assert "my_variable" in validated_response.refactored_code
        assert "another_method" in validated_response.refactored_code
        assert "local_var" in validated_response.refactored_code
        assert "someFunction" not in validated_response.refactored_code
        assert "myVariable" not in validated_response.refactored_code
        
        expected_response = RefactorResponse(**camel_to_snake_response)
        assert validated_response.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_mixed_to_snake_case(mixed_convention_code, mixed_to_snake_response):
    """Test converting mixed naming conventions to snake_case via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/inconsistent-naming"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": mixed_convention_code,
            "target_convention": "snake_case",
            "naming_convention": "mixed"
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "some_function" in validated_response.refactored_code
        assert "my_variable" in validated_response.refactored_code
        assert "another_var" in validated_response.refactored_code
        assert "local_val" in validated_response.refactored_code
        assert "some_local_var" in validated_response.refactored_code
        assert "another_local_var" in validated_response.refactored_code
        assert "myVariable" not in validated_response.refactored_code
        assert "localVal" not in validated_response.refactored_code
        assert "anotherLocalVar" not in validated_response.refactored_code
        
        expected_response = RefactorResponse(**mixed_to_snake_response)
        assert validated_response.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_with_dependencies(snake_case_code, mock_dependency):
    """Test refactoring with dependencies via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/inconsistent-naming"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": snake_case_code,
            "target_convention": "camelCase",
            "naming_convention": "auto-detect",
            "dependencies": [mock_dependency]
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dependencies is not None
        assert len(validated_response.dependencies) == 1
        assert validated_response.dependencies[0].name == "test_dependency.py"
        # Verify the dependency was not modified
        assert "helper_function" in validated_response.dependencies[0].fileContent
        assert "helperFunction" not in validated_response.dependencies[0].fileContent
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_invalid_target_convention(snake_case_code):
    """Test with an invalid target convention."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/inconsistent-naming"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": snake_case_code,
            "target_convention": "invalidConvention",
            "naming_convention": "auto-detect"
        })
    
    assert response.status_code == 400  # Expecting a bad request