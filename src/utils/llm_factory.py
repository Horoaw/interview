import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class LLMFactory:
    @staticmethod
    def get_deepseek_llm(temperature: float = 0.0, model: str = "deepseek-chat"):
        """
        Returns a ChatOpenAI instance configured for DeepSeek.
        Ensures DEEPSEEK_API_KEY and DEEPSEEK_BASE_URL are in .env
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        return ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=temperature
        )
