Run the Service Using this command
uvicorn app.main:app --reload

or 

python -m uvicorn app.main:app --reload

Testing the Endpoint 

http://127.0.0.1:8000/analyze-ast

This is URL

{
    "code": "import os\nimport sys as system\nfrom src.utils.utility import Bag , Feet as ft\nfrom .local_module import LocalClass\ndef f1():\n    pass\n    def f2():\n        pass\n        \ndef f3():\n    pass\n    \nclass A:\n    def __init__(self):\n        self.x = 10\n    def f4():\n        self.y = 20\n    def f5():\n        pass\n        \nMAX = [100, 200]\nMAX_2 = A()\n\n\nf3()\n"
}

Dummy code structure to get results 

Add Header of Content-Type -> application/json

This return the following Data (Done)

    AST of Code

    All Functions Within a File (Includes Nested Functions as Well (f1.f2  where f2 is a nested function within f1. Used this to highlight))

    All Classes with there name, variables and inner functions

    All imports for now

    Main File Check (if "__name" == .....)

    Standalone File Check as well
