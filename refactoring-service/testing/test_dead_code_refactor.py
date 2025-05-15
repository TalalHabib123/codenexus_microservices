import pytest
from endpoints_url import REFACTOR_SERVICE_URL
from pydantic import ValidationError
import httpx
from app.refactoring_models.refactor_models import RefactorResponse

# Fixture for code with dead function
@pytest.fixture
def dead_function_code():
    return """
def live_function():
    print("This function is used")
    return True

def dead_function():
    print("This function is never called")
    return False

# Call the live function
result = live_function()
"""

# Fixture for code with dead class
@pytest.fixture
def dead_class_code():
    return """
class LiveClass:
    def __init__(self):
        self.value = 10
    
    def get_value(self):
        return self.value

class DeadClass:
    def __init__(self):
        self.value = 20
    
    def get_value(self):
        return self.value

# Create an instance of the live class
live_instance = LiveClass()
print(live_instance.get_value())
"""

# Fixture for complex code with dead methods
@pytest.fixture
def complex_dead_code():
    return """
class Calculator:
    def __init__(self):
        self.value = 0
    
    def add(self, x):
        self.value += x
        return self.value
    
    def subtract(self, x):
        self.value -= x
        return self.value
    
    def multiply(self, x):
        # Dead method, never used
        self.value *= x
        return self.value
    
    def divide(self, x):
        # Dead method, never used
        if x == 0:
            raise ValueError("Cannot divide by zero")
        self.value /= x
        return self.value

# Use the calculator
calc = Calculator()
print(calc.add(10))
print(calc.subtract(5))
"""

# Fixture for code with nested entities
@pytest.fixture
def nested_entities_code():
    return """
class OuterClass:
    class InnerClass:
        def inner_method(self):
            print("Inner method")
    
    def outer_method(self):
        print("Outer method")

# Only use the outer method
obj = OuterClass()
obj.outer_method()
"""

# Fixture for code with partial name matches
@pytest.fixture
def partial_name_match_code():
    return """
def prefix_dead_function():
    return True

def dead_function_suffix():
    return True

def dead_function():
    return True

# Use the functions with similar names
prefix_dead_function()
dead_function_suffix()
"""

# Expected response fixtures
@pytest.fixture
def remove_dead_function_response():
    return {
        'refactored_code': """
def live_function():
    print("This function is used")
    return True

# Call the live function
result = live_function()
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.fixture
def remove_dead_class_response():
    return {
        'refactored_code': """
class LiveClass:
    def __init__(self):
        self.value = 10
    
    def get_value(self):
        return self.value

# Create an instance of the live class
live_instance = LiveClass()
print(live_instance.get_value())
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.fixture
def remove_dead_method_response():
    return {
        'refactored_code': """
class Calculator:
    def __init__(self):
        self.value = 0
    
    def add(self, x):
        self.value += x
        return self.value
    
    def subtract(self, x):
        self.value -= x
        return self.value

# Use the calculator
calc = Calculator()
print(calc.add(10))
print(calc.subtract(5))
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.mark.asyncio
async def test_remove_dead_function(dead_function_code, remove_dead_function_response):
    """Test removing a dead function via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/dead-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": dead_function_code,
            "entity_name": "dead_function",
            "entity_type": "function"
        })
    
    assert response.status_code == 200

    # Validate the response against the RefactorResponse model
    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        # Assert the success and error fields
        assert validated_response.success is True
        assert validated_response.error is None
        
        # Verify the refactored code contains expected content
        assert "def live_function():" in validated_response.refactored_code
        assert "print(\"This function is used\")" in validated_response.refactored_code
        assert "def dead_function():" not in validated_response.refactored_code
        assert "print(\"This function is never called\")" not in validated_response.refactored_code
        
        expected_response = RefactorResponse(**remove_dead_function_response)
        assert validated_response.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_remove_dead_class(dead_class_code, remove_dead_class_response):
    """Test removing a dead class via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/dead-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": dead_class_code,
            "entity_name": "DeadClass",
            "entity_type": "class"
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "class LiveClass:" in validated_response.refactored_code
        assert "def get_value(self):" in validated_response.refactored_code
        assert "class DeadClass:" not in validated_response.refactored_code
        
        expected_response = RefactorResponse(**remove_dead_class_response)
        assert validated_response.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_remove_dead_method(complex_dead_code, remove_dead_method_response):
    """Test removing dead methods from a class via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/dead-code"
    
    # First remove the multiply method
    async with httpx.AsyncClient() as client:
        response1 = await client.post(url, json={
            "code": complex_dead_code,
            "entity_name": "multiply",
            "entity_type": "method"
        })
    
    assert response1.status_code == 200
    response1_data = response1.json()
    validated_response1 = RefactorResponse(**response1_data)
    
    # Then remove the divide method from the already refactored code
    async with httpx.AsyncClient() as client:
        response2 = await client.post(url, json={
            "code": validated_response1.refactored_code,
            "entity_name": "divide",
            "entity_type": "method"
        })
    
    assert response2.status_code == 200

    try:
        response2_data = response2.json()
        validated_response2 = RefactorResponse(**response2_data)
        
        assert validated_response2.success is True
        assert validated_response2.error is None
        
        assert "def add(self, x):" in validated_response2.refactored_code
        assert "def subtract(self, x):" in validated_response2.refactored_code
        assert "def multiply(self, x):" not in validated_response2.refactored_code
        assert "def divide(self, x):" not in validated_response2.refactored_code
        
        expected_response = RefactorResponse(**remove_dead_method_response)
        assert validated_response2.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_entity_not_found(dead_function_code):
    """Test when the specified entity doesn't exist in the code."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/dead-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": dead_function_code,
            "entity_name": "nonexistent_function",
            "entity_type": "function"
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        # Code should remain unchanged
        assert validated_response.refactored_code.strip() == dead_function_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_invalid_entity_type(dead_function_code):
    """Test with an invalid entity type."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/dead-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": dead_function_code,
            "entity_name": "dead_function",
            "entity_type": "invalid_type"
        })
    
    assert response.status_code == 400  # Expecting a bad request