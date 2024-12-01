import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.models.ast_models import VariableConflictResponse

@pytest.fixture
def sample_conflict_code():
    return """
global_var = "helloWorld"
def fun(): 
    global_var = 3
    a = 10
    return global_var + a
neww = fun()
print(global_var)
"""

@pytest.fixture
def no_conflict_code():
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
def sample_conflict_code2():
    return """
x=1 
y=1
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
def conflict_code_response():
    return {'conflicts_report': 
            [
                {
                    'variable': 'global_var', 
                    'assignments': [('module', 2)],
                    'local_assignments': [('fun', 4)], 
                    'usages': [], 
                    'conflicts': ["Multiple assignments to 'global_var' detected. Potential conflict!", "Shadowing issue in function 'fun': Local variable 'global_var' may shadow the global variable."], 
                    'warnings': []
                    }
             ],
             'success': True,
             'error':None
             }

@pytest.fixture
def no_conflict_code_response():
    return {
        'conflicts_report': [{'variable': 'global', 'assignments': [], 'local_assignments': [], 'usages': [], 'conflicts': [], 'warnings': []}],
        'success': True,
        'error': None
    }

@pytest.fixture
def conflict_code_response_2():
    return {
        'conflicts_report': [
            {
            'variable': 'x', 
            'assignments': [('module', 2)], 
            'local_assignments': [('fun', 6)], 
            'usages': [], 
            'conflicts': ["Multiple assignments to 'x' detected. Potential conflict!", 
                          "Shadowing issue in function 'fun': Local variable 'x' may shadow the global variable."], 
            'warnings': []
            },
            {
               'variable': 'y',
                'assignments': [('module', 3)],
                'local_assignments': [('fun', 7)], 
                'usages': [], 
                'conflicts': ["Multiple assignments to 'y' detected. Potential conflict!", 
                              "Shadowing issue in function 'fun': Local variable 'y' may shadow the global variable."], 
                'warnings': []
            }
        ],
        'success': True,
        'error': None
    }

@pytest.mark.asyncio
async def test_conflict_code(sample_conflict_code, conflict_code_response):
    url = f"{BASE_URL}/global-conflict"
    async with httpx.AsyncClient() as client:
        global_variables = ["global_var"]
        response = await client.post(url, json={"code": sample_conflict_code, "global_variables": global_variables})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = VariableConflictResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dict() == conflict_code_response
            
    except ValidationError as e:
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_no_conflict_code(no_conflict_code, no_conflict_code_response):
    url = f"{BASE_URL}/global-conflict"
    async with httpx.AsyncClient() as client:
        global_variables = ["global"]
        response = await client.post(url, json={"code": no_conflict_code, "global_variables": global_variables})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = VariableConflictResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dict() == no_conflict_code_response
            
    except ValidationError as e:
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_2_conflict_code(sample_conflict_code2, conflict_code_response_2):
    url = f"{BASE_URL}/global-conflict"
    async with httpx.AsyncClient() as client:
        global_variables = ['x','y']
        print("sampke",sample_conflict_code2,"global", global_variables)
        response = await client.post(url, json={"code": sample_conflict_code2, "global_variables": global_variables})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = VariableConflictResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert validated_response.dict() == conflict_code_response_2
            
    except ValidationError as e:
        pytest.fail(f"Response validation failed: {e}")