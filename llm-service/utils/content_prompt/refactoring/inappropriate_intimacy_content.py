from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_refactoring_docs_for_

def create_inappropriate_intimacy_content(task_data, knowledge_base_refactoring, nn_model):
    code_snippet = task_data.get("code_snippet", "")

    relevant_docs = retrieve_relevant_refactoring_docs_for_(
        "Inappropriate Intimacy",
        code_snippet,
        knowledge_base_refactoring,
        nn_model
    )

    content = f"""
You will now refactor the following Python class or method to eliminate the "Inappropriate Intimacy" code smell while adhering to the system's guidelines. The logic and functionality must remain unchanged, but you should ensure that the class or method no longer exposes or manipulates another class's internal details inappropriately. Document your changes as specified in the system prompt.

Here is the Python code that requires refactoring:

```python
{code_snippet}
```
Refactor this class or method by reducing direct access to another class’s private or protected attributes, improving encapsulation, and introducing proper delegation where needed. If changes in other classes are required, provide them in separate code blocks with appropriate comments. """.strip()

    # If additional references are available, append them
    if relevant_docs:
        content += "\n\n### Additional References:\n"
        content += "If applicable, use the following documents for guidance on refactoring 'Inappropriate Intimacy':\n\n"
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
