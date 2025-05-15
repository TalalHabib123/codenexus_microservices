import pytest
from app.utils.Analysis.unused_variables_refactor import unused_variables_refactor

# Test data
simple_unused_variable = """
def test_function():
    x = 10  # Unused variable
    y = 20
    return y
"""

multiple_unused_variables = """
def test_function():
    x = 10  # Unused variable
    y = 20  # Unused variable
    z = 30
    return z
"""

complex_code_with_unused_variables = """
def complex_function(param1, param2):
    result = 0
    temp = param1 * 2  # Unused variable
    
    for i in range(10):
        j = i * 2  # Unused variable
        result += param2
    
    intermediate = result / 2  # Unused variable
    
    return result

class TestClass:
    def __init__(self):
        self.value = 10
        self.unused_attr = 20  # Unused attribute
    
    def test_method(self):
        local_var = 30  # Unused variable
        return self.value
"""

def test_single_unused_variable():
    """Test removing a single unused variable."""
    unused_vars = ["x"]
    result = unused_variables_refactor(unused_vars, simple_unused_variable)
    
    assert "x = 10" not in result
    assert "y = 20" in result
    assert "return y" in result

def test_multiple_unused_variables():
    """Test removing multiple unused variables."""
    unused_vars = ["x", "y"]
    result = unused_variables_refactor(unused_vars, multiple_unused_variables)
    
    assert "x = 10" not in result
    assert "y = 20" not in result
    assert "z = 30" in result
    assert "return z" in result

def test_complex_code_unused_variables():
    """Test removing unused variables in complex code."""
    unused_vars = ["temp", "j", "intermediate", "unused_attr", "local_var"]
    result = unused_variables_refactor(unused_vars, complex_code_with_unused_variables)
    
    assert "def complex_function(param1, param2):" in result
    assert "result = 0" in result
    assert "temp = param1 * 2" not in result
    assert "j = i * 2" not in result
    assert "intermediate = result / 2" not in result
    assert "self.unused_attr = 20" not in result
    assert "local_var = 30" not in result
    
    assert "result += param2" in result
    assert "return result" in result
    assert "self.value = 10" in result
    assert "return self.value" in result

def test_no_unused_variables():
    """Test with no unused variables."""
    code = """
def test_function():
    x = 10
    return x
"""
    result = unused_variables_refactor([], code)
    assert result == code

def test_variable_not_in_code():
    """Test with variables that don't exist in the code."""
    unused_vars = ["nonexistent_var"]
    result = unused_variables_refactor(unused_vars, simple_unused_variable)
    # Code should remain unchanged
    assert result == simple_unused_variable

def test_empty_code():
    """Test with empty code."""
    unused_vars = ["x", "y", "z"]
    result = unused_variables_refactor(unused_vars, "")
    assert result == ""

def test_variable_in_comment():
    """Test with variable mentioned in comment but not in code."""
    code = """
def test_function():
    # This is a comment about variable x
    y = 10
    return y
"""
    unused_vars = ["x"]
    result = unused_variables_refactor(unused_vars, code)
    # Code should remain unchanged since x is only in a comment
    assert result == code

def test_variable_as_part_of_another_name():
    """Test to ensure variables that are part of other identifiers aren't removed."""
    code = """
def test_function():
    x = 10  # This should be removed
    my_x_value = 20  # This should NOT be removed
    return my_x_value
"""
    unused_vars = ["x"]
    result = unused_variables_refactor(unused_vars, code)
    
    assert "x = 10" not in result
    assert "my_x_value = 20" in result
    assert "return my_x_value" in result

def test_function_parameters():
    """Test with unused function parameters."""
    code = """
def test_function(used_param, unused_param):
    return used_param
"""
    # Note: refactoring unused parameters is typically not done automatically
    # as it could break API compatibility
    unused_vars = ["unused_param"]
    result = unused_variables_refactor(unused_vars, code)
    # Parameters should remain unchanged
    assert "def test_function(used_param, unused_param):" in result
