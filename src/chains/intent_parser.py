from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.schemas.models import Intent
from src.utils.llm_factory import LLMFactory

class IntentParser:
    def __init__(self):
        self.llm = LLMFactory.get_deepseek_llm(temperature=0.0)
        self.parser = PydanticOutputParser(pydantic_object=Intent)
        
        self.prompt = ChatPromptTemplate.from_template(
            "你是一个专业的意图解析助手。请根据用户的需求，解析出结构化的意图对象。\n"
            "用户需求: {user_input}\n"
            "\n{format_instructions}\n"
            "输出必须严格符合 JSON 格式。"
        )

    def parse(self, user_input: str) -> Intent:
        chain = self.prompt | self.llm | self.parser
        return chain.invoke({
            "user_input": user_input,
            "format_instructions": self.parser.get_format_instructions()
        })
