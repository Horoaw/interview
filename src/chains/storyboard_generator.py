from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from src.schemas.models import Scene
from src.utils.llm_factory import LLMFactory

class SceneList(BaseModel):
    scenes: List[Scene]

class StoryboardGenerator:
    def __init__(self):
        # 使用低温模型确保结构化拆解准确
        self.llm = LLMFactory.get_deepseek_llm(temperature=0.0)
        self.parser = PydanticOutputParser(pydantic_object=SceneList)
        
        self.prompt = ChatPromptTemplate.from_template(
            "你是一个专业的短视频分镜师。请将给定的脚本内容拆解为结构化的分镜（Storyboard）。\n"
            "脚本内容: {script}\n"
            "\n{format_instructions}\n"
            "请确保每个分镜的视觉主体（visual_subject）描述具体，且符合脚本意境。"
        )

    def generate_storyboard(self, script: str) -> List[Scene]:
        chain = self.prompt | self.llm | self.parser
        result = chain.invoke({
            "script": script,
            "format_instructions": self.parser.get_format_instructions()
        })
        return result.scenes
