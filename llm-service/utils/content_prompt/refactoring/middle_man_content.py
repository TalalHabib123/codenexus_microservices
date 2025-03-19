from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_refactoring_docs_for_

def create_middle_man_content(task_data, knowledge_base_refactoring, nn_model):
    code_snippet = task_data.get("code_snippet", "")

    # Retrieve any relevant documentation for the "Middle Man" code smell
    relevant_docs = retrieve_relevant_refactoring_docs_for_(
        "Middle Man",
        code_snippet,
        knowledge_base_refactoring,
        nn_model
    )

    content = f"""
You will now refactor the following Python class or method to eliminate the "Middle Man" code smell while adhering to the system's guidelines. The logic and functionality must remain unchanged unless the class or method is entirely redundant. Document any changes as specified in the system prompt.

Here is the Python code that requires refactoring:

```python
{code_snippet}
```
Refactor this code by removing unnecessary delegation. If you find that the class or method adds no meaningful logic, consider inlining or removing it. If it does remain, ensure it provides clear and necessary functionality instead of merely forwarding calls. Any modifications to other classes should be included in separate code blocks with clear comments. """.strip()

    # If we have additional references, append them
    if relevant_docs:
        content += "\n\n### Additional References:\n"
        content += "If applicable, use the following documents for guidance on refactoring 'Middle Man':\n\n"
        for index, doc in enumerate(relevant_docs, start=1):
            for key, value in doc.items():
                content += (
                    f"Reference {index} - {key}:\n\n"
                    "```\n"
                    f"{value}\n"
                    "```\n\n"
                )

    return {
        "role": "user",
        "content": content
    }
