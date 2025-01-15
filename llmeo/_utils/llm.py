import os
from typing import Optional
import yaml

class LLMError(Exception):
    """Base exception for LLM-related errors"""
    pass

class LLMConfig:
    """Configuration for LLM models"""
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        temperature: float = 0.5,
        top_p: float = 1.0,
        max_tokens: int = 4096,
        system_prompt: str = "You are a helpful assistant."
    ):
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.gemini_api_key = gemini_api_key
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt

    @classmethod
    def from_yaml(cls, config_path: str) -> "LLMConfig":
        """Load configuration from a YAML file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r") as file:
            config_data = yaml.safe_load(file)
            
        return cls(
            openai_api_key=config_data.get("OPENAI_API_KEY"),
            anthropic_api_key=config_data.get("ANTHROPIC_API_KEY"),
            gemini_api_key=config_data.get("GEMINI_API_KEY"),
            temperature=config_data.get("temperature", 0.5),
            top_p=config_data.get("top_p", 1.0),
            max_tokens=config_data.get("max_tokens", 4096),
            system_prompt=config_data.get(
                "system_prompt", 
                "You are a helpful assistant."
            )
        )

class GPT4:
    """GPT-4 model implementation"""
    def __init__(self, config: LLMConfig):
        self.config = config
        self.name = "gpt-4"
        self.client = None

    def create(self) -> None:
        """Initialize the model"""
        try:
            from openai import OpenAI
            if not self.config.openai_api_key:
                raise LLMError("OpenAI API key not found")
            self.client = OpenAI(api_key=self.config.openai_api_key)
        except Exception as e:
            raise LLMError(f"Failed to initialize GPT-4: {str(e)}")

    def call(self, content: str, system: Optional[str] = None) -> str:
        """Call the model with content"""
        try:
            messages = [
                {
                    "role": "system", 
                    "content": system or self.config.system_prompt
                },
                {"role": "user", "content": content}
            ]
            
            response = self.client.chat.completions.create(
                model=self.name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                temperature=self.config.temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMError(f"GPT-4 API call failed: {str(e)}")

class GPTo1:
    """GPT-o1 model implementation"""
    def __init__(self, config: LLMConfig, name: str = "o1-preview"):
        self.config = config
        self.name = name
        self.client = None

    def create(self) -> None:
        """Initialize the model"""
        try:
            from openai import OpenAI
            if not self.config.openai_api_key:
                raise LLMError("OpenAI API key not found")
            self.client = OpenAI(api_key=self.config.openai_api_key)
        except Exception as e:
            raise LLMError(f"Failed to initialize GPT-o1: {str(e)}")

    def call(self, content: str, system: Optional[str] = None) -> str:
        """Call the model with content"""
        try:
            if system:
                content = system + "\n" + content
            messages = [{"role": "user", "content": content}]
            response = self.client.chat.completions.create(
                model=self.name, 
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMError(f"GPT-o1 API call failed: {str(e)}")

class Claude3:
    """Claude-3 model implementation"""
    def __init__(self, config: LLMConfig):
        self.config = config
        self.name = "claude-3-5-sonnet-20240620"
        self.client = None

    def create(self) -> None:
        """Initialize the model"""
        try:
            import anthropic
            if not self.config.anthropic_api_key:
                raise LLMError("Anthropic API key not found")
            self.client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)
        except Exception as e:
            raise LLMError(f"Failed to initialize Claude-3: {str(e)}")

    def call(self, content: str, system: Optional[str] = None) -> str:
        """Call the model with content"""
        try:
            system = system or self.config.system_prompt
            messages = [{"role": "user", "content": content}]
            
            response = self.client.messages.create(
                model=self.name,
                system=system,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
            )
            return response.content[0].text
        except Exception as e:
            raise LLMError(f"Claude-3 API call failed: {str(e)}")

      
class Gemini:
    """Gemini model implementation"""
    def __init__(self, config: LLMConfig, name: str = "gemini-2.0-flash-thinking-exp"):
        self.config = config
        self.name = name
        self.client = None

    def create(self) -> None:
        """Initialize the model"""
        try:    
            from google import genai
            self.client = genai.Client(api_key=self.config.gemini_api_key, http_options={'api_version':'v1alpha'})
        except Exception as e:
            raise LLMError(f"Failed to initialize Gemini: {str(e)}")
        
    def call(self, content: str, system: Optional[str] = None) -> str:
        """Call the model with content"""
        try:
            response = self.client.models.generate_content(
                model=self.name, contents=content
            )
            return response.candidates[0].content.parts[1].text
        except Exception as e:
            raise LLMError(f"Gemini API call failed: {str(e)}")

def test_models(config: LLMConfig):
    """Test different LLM models"""
    test_prompt = "Tell me a joke."
    
    models = [
        ("GPT-4", GPT4(config)),
        ("Claude-3", Claude3(config)),
        ("o1-preview", GPTo1(config)),
        ("o1-mini", GPTo1(config, name="o1-mini")),
    ]

    for model_name, model in models:
        print(f"\n{'*' * 15}{model_name}{'*' * 15}")
        try:
            model.create()
            response = model.call(test_prompt)
            print(response)
        except LLMError as e:
            print(f"Error with {model_name}: {str(e)}")

if __name__ == "__main__":
    # Load configuration from YAML file
    config_path = "../llm_config.yaml"
    config = LLMConfig.from_yaml(config_path)
    test_models(config)