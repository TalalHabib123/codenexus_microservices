from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import InferenceClient
import torch
from logger_config import get_logger
import os

logger = get_logger(__name__)

def load_model_pipeline(use_inference_api=False, hf_model_id="meta-llama/Llama-3.1-70B-Instruct"):
    if use_inference_api:
        # Use the Hugging Face Inference API
        # Ensure you have your HF_TOKEN set in environment variables for private/gated models:
        hf_token = os.getenv("HF_TOKEN", None)
        
        if not hf_token:
            logger.error("HF_TOKEN is not set. Cannot use inference API without a token.")
            exit(1)

        logger.info(f"Loading model pipeline from Hugging Face API: {hf_model_id}")
        try:
            # Using pipeline directly with `use_auth_token=True` will route through inference if 
            # the model is on the hub and you have an HF token. You may need `revision` if model is gated.
            # Note: If you want to specifically use the hosted Inference API endpoint, you can configure `pipeline`
            # with `model=hf_model_id` and `use_auth_token=hf_token`. The pipeline should handle this.
            model_pipeline = InferenceClient(
                provider="auto",
                api_key="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"
            )
            logger.info("Model Client loaded from Hugging Face Inference API")
            return model_pipeline
        except Exception as e:
            logger.error(f"Error loading model pipeline from Inference API: {hf_model_id}")
            logger.error(e)
            exit(1)

    else:
        # Load the local LLM model pipeline
        current_dir = os.path.dirname(os.path.abspath(__file__))
        relative_model_path = os.path.join('models', 'LLAMA-3.1_8_I')
        model_id = os.path.join(current_dir, relative_model_path)
        logger.info(f"Models directory: {model_id}")

        try:
            logger.info(f"Loading local model pipeline: {model_id}")
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map='auto')
            model_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512
            )
            logger.info(f"Local model pipeline loaded: {model_id}")
            return model_pipeline
        except Exception as e:
            logger.error(f"Error loading model pipeline: {model_id}")
            print(e)
            exit(1)


def process_with_llm(model_pipeline, prompt, use_inference_api=False, hf_model_id="meta-llama/Llama-3.1-70B-Instruct"):
    processed_result = ""
    logger.info(f"Processing task with LLM model pipeline")
    if use_inference_api:
        completion = model_pipeline.chat.completions.create(
            model=hf_model_id,
            messages=prompt,
            max_tokens=2048,
        )
        processed_result = completion.choices[0].message.content
    else:
        outputs = model_pipeline(
            prompt,
            max_new_tokens=512,
            return_full_text=False,
        )
        processed_result = outputs[0]["generated_text"]
        
    logger.info(f"Processed result: {processed_result}")
    return processed_result
