# llm_utils.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class LLMManager:
    """Singleton class to manage LLM model loading and inference."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMManager, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.tokenizer = None
            cls._instance.device = "cuda" if torch.cuda.is_available() else "cpu"
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """Loads the model and tokenizer."""
        try:
            model_path = "path/to/your/fine-tuned/model"  # Change to actual path
            print(f"Loading model from {model_path} on {self.device}...")

            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            )
            self.model.to(self.device)
            print("✅ Model loaded successfully!")

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None  # Keep model as None if loading fails

    def generate_response(self, message, user_profile=None):
        """Generates a response using the AI model."""
        if self.model is None or self.tokenizer is None:
            return "⚠️ AI Model is unavailable. Please try again later."

        try:
            # Constructing the prompt with user profile data
            if user_profile:
                prompt = (
                    f"User Info:\n- Dosha: {user_profile.dosha_type}\n"
                    f"- Conditions: {user_profile.chronic_conditions}\n\n"
                    f"User: {message}\nAI:"
                )
            else:
                prompt = f"User: {message}\nAI:"

            # Tokenize input
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

            # Generate response with model
            output = self.model.generate(
                input_ids,
                max_new_tokens=1024,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            # Decode the output tokens into text
            response = self.tokenizer.decode(output[0][input_ids.shape[1]:], skip_special_tokens=True)
            return response.strip()

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "⚠️ I encountered an error while processing your request. Please try again."

# Singleton instance for external use
llm_manager = LLMManager()

def process_user_message(user_input, user_profile=None):
    """Processes user input through the AI model."""
    return llm_manager.generate_response(user_input, user_profile)
