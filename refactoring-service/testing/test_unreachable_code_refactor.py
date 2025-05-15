import pytest
from endpoints_url import REFACTOR_SERVICE_URL
from pydantic import ValidationError
import httpx
from app.refactoring_models.refactor_models import RefactorResponse

# Fixture for simple unreachable code
@pytest.fixture
def simple_unreachable_code():
    return """
def test_function():
    print("This will be executed")
    return True
    print("This will never be executed")  # Line 5
    x = 10
    y = 20
"""

# Fixture for multiple unreachable code blocks
@pytest.fixture
def multiple_unreachable_code_blocks():
    return """
def test_function():
    if True:
        print("This will be executed")
        return
        print("This will never be executed")  # Line 6
    
    print("This will never be executed either")  # Line 8
    
    x = 10
    if x > 5:
        print("This would be executed")
        return
        print("This is unreachable")  # Line 14
    else:
        print("This might be executed")
        return
        print("This is also unreachable")  # Line 18
"""

# Fixture for complex unreachable code
@pytest.fixture
def complex_unreachable_code():
    return """
def test_function(condition):
    if condition:
        print("Condition is True")
        return True
    else:
        print("Condition is False")
        return False
    
    # Everything below is unreachable
    print("This is unreachable")  # Line 10
    
    x = 10
    y = 20
    
    if x > y:
        print("x is greater")
    else:
        print("y is greater")
        
    return "This will never return"  # Line 19
"""

# Expected response fixtures
@pytest.fixture
def single_unreachable_line_response():
    return {
        'refactored_code': """
def test_function():
    print("This will be executed")
    return True
    
    x = 10
    y = 20
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.fixture
def multiple_unreachable_lines_response():
    return {
        'refactored_code': """
def test_function():
    if True:
        print("This will be executed")
        return
        
    
    
    
    x = 10
    if x > 5:
        print("This would be executed")
        return
        
    else:
        print("This might be executed")
        return
        
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.fixture
def unreachable_block_response():
    return {
        'refactored_code': """
def test_function(condition):
    if condition:
        print("Condition is True")
        return True
    else:
        print("Condition is False")
        return False
    
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.mark.asyncio
async def test_single_unreachable_line(simple_unreachable_code, single_unreachable_line_response):
    """Test removing a single unreachable line via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/unreachable-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": simple_unreachable_code,
            "unreachable_code_lines": [5]
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "This will be executed" in validated_response.refactored_code
        assert "return True" in validated_response.refactored_code
        assert "This will never be executed" not in validated_response.refactored_code
        assert "x = 10" in validated_response.refactored_code
        assert "y = 20" in validated_response.refactored_code
        
        expected_response = RefactorResponse(**single_unreachable_line_response)
        assert validated_response.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_multiple_unreachable_lines(multiple_unreachable_code_blocks, multiple_unreachable_lines_response):
    """Test removing multiple unreachable lines via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/unreachable-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": multiple_unreachable_code_blocks,
            "unreachable_code_lines": [6, 8, 14, 18]
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "This will be executed" in validated_response.refactored_code
        assert "This will never be executed" not in validated_response.refactored_code
        assert "This will never be executed either" not in validated_response.refactored_code
        assert "This is unreachable" not in validated_response.refactored_code
        assert "This is also unreachable" not in validated_response.refactored_code
        
        assert "return" in validated_response.refactored_code
        assert "x = 10" in validated_response.refactored_code
        assert "This would be executed" in validated_response.refactored_code
        assert "This might be executed" in validated_response.refactored_code
        
        expected_response = RefactorResponse(**multiple_unreachable_lines_response)
        assert validated_response.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_unreachable_block(complex_unreachable_code, unreachable_block_response):
    """Test removing an unreachable block of code via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/unreachable-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": complex_unreachable_code,
            "unreachable_code_lines": list(range(10, 20))  # Lines 10-19
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "def test_function(condition):" in validated_response.refactored_code
        assert "if condition:" in validated_response.refactored_code
        assert "Condition is True" in validated_response.refactored_code
        assert "return True" in validated_response.refactored_code
        assert "Condition is False" in validated_response.refactored_code
        assert "return False" in validated_response.refactored_code
        
        assert "This is unreachable" not in validated_response.refactored_code
        assert "x = 10" not in validated_response.refactored_code
        assert "y = 20" not in validated_response.refactored_code
        assert "x is greater" not in validated_response.refactored_code
        assert "y is greater" not in validated_response.refactored_code
        assert "This will never return" not in validated_response.refactored_code
        
        expected_response = RefactorResponse(**unreachable_block_response)
        assert validated_response.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_no_unreachable_lines():
    """Test with no unreachable lines."""
    code = """
def test_function():
    print("All reachable code")
    if True:
        return True
    else:
        return False
"""
    url = f"{REFACTOR_SERVICE_URL}/refactor/unreachable-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": code,
            "unreachable_code_lines": []
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        # Code should remain unchanged
        assert validated_response.refactored_code.strip() == code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_line_number_out_of_range(simple_unreachable_code):
    """Test with line numbers that don't exist in the code."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/unreachable-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": simple_unreachable_code,
            "unreachable_code_lines": [100, 200]  # Lines that don't exist
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        # Code should remain unchanged
        assert validated_response.refactored_code.strip() == simple_unreachable_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_empty_code():
    """Test with empty code."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/unreachable-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": "",
            "unreachable_code_lines": [1, 2, 3]
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        # Empty code should remain empty
        assert validated_response.refactored_code == ""
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_all_lines_unreachable():
    """Test when all lines are marked as unreachable."""
    code = """
def test_function():
    print("Line 1")
    print("Line 2")
    return True
"""
    url = f"{REFACTOR_SERVICE_URL}/refactor/unreachable-code"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": code,
            "unreachable_code_lines": [2, 3, 4, 5]
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "def test_function():" in validated_response.refactored_code
        assert "print(\"Line 1\")" not in validated_response.refactored_code
        assert "print(\"Line 2\")" not in validated_response.refactored_code
        assert "return True" not in validated_response.refactored_code
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")