from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.schemas.models import ExtractedFacts
from src.utils.llm_factory import LLMFactory

class FactExtractor:
    def __init__(self):
        # 使用低温模型确保提取准确
        self.llm = LLMFactory.get_deepseek_llm(temperature=0.0)
        self.parser = PydanticOutputParser(pydantic_object=ExtractedFacts)
        
        self.prompt = ChatPromptTemplate.from_template(
            "你是一个精密的事实提取助手。请从给定的脚本中提取出所有关于文物的核心事实。\n"
            "脚本内容: {script}\n"
            "\n{format_instructions}\n"
            "如果脚本中没有提到某个字段，请设为 null 或空列表。"
        )

    def extract(self, script: str) -> ExtractedFacts:
        chain = self.prompt | self.llm | self.parser
        return chain.invoke({
            "script": script,
            "format_instructions": self.parser.get_format_instructions()
        })
