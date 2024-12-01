from transformers import pipeline
import torch

def load_model_pipeline():
    model_id = 'models/Llama3.1-8B-Instruct'
    device = -1  # CPU by default

    # Load the LLM model pipeline
    try:
        if torch.cuda.is_available():
            device = 0  # GPU device
        model_pipeline = pipeline(
            "text-generation",
            model=model_id,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map={0: device},
        )
        return model_pipeline
    except Exception as e:
        print(f"Error loading model: {e}")
        exit(1)

def process_with_llm(model_pipeline, prompt):
    # Process the task using the LLM
    outputs = model_pipeline(
        prompt,
        max_new_tokens=256,
        return_full_text=False,
    )
    processed_result = outputs[0]["generated_text"]
    return processed_result
