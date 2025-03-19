from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_refactoring_docs_for_

def create_feature_envy_content(task_data, knowledge_base_refactoring, nn_model):
    code_snippet = task_data.get("code_snippet", "")

    # Retrieve any relevant documentation for the "Feature Envy" code smell
    relevant_docs = retrieve_relevant_refactoring_docs_for_(
        "Feature Envy",
        code_snippet,
        knowledge_base_refactoring,
        nn_model
    )

    # Build the main content of the user prompt
    content = f"""
You will now refactor the following Python function to eliminate the "Feature Envy" code smell while adhering to the system's guidelines. The logic and functionality must remain unchanged, but you should ensure that the function's responsibilities are handled in the appropriate class, reducing its dependency on external classes or their data. Document your changes as specified in the system prompt.

Here is the Python code that requires refactoring:

```python
{code_snippet}
```
Refactor this function by moving or delegating functionality to the correct class if it is overly reliant on that class’s data or methods. Each class modification should be provided in a separate code block, commented with the respective class name. Remember to preserve the same function name, inputs, and outputs. """.strip()

    # If additional references are available, append them
    if relevant_docs:
        content += "\n\n### Additional References:\n"
        content += "If applicable, use the following documents for guidance on refactoring 'Feature Envy':\n\n"
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
