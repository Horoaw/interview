from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.schemas.models import Scene, VisualPrompt
from src.utils.llm_factory import LLMFactory

class PromptConverter:
    def __init__(self):
        self.llm = LLMFactory.get_deepseek_llm(temperature=0.3)
        self.parser = PydanticOutputParser(pydantic_object=VisualPrompt)
        
        self.prompt = ChatPromptTemplate.from_template(
            "你是一个专业的 AI 绘画/视频提示词专家。请根据分镜描述，将其转化为高质量的生成工具提示词。\n"
            "分镜描述: {scene_description}\n"
            "画面主体: {subject}\n"
            "情感氛围: {emotion}\n"
            "\n{format_instructions}\n"
            "提示词应包含：构图、光影、材质（如青铜锈迹）、艺术风格（如电影感、悬疑风）。"
        )

    def convert(self, scene: Scene) -> VisualPrompt:
        chain = self.prompt | self.llm | self.parser
        return chain.invoke({
            "scene_description": scene.script_text,
            "subject": scene.visual_subject,
            "emotion": scene.emotion,
            "format_instructions": self.parser.get_format_instructions()
        })
