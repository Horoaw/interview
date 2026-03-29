from langchain_core.prompts import ChatPromptTemplate
from src.schemas.models import KnowledgeBundle
from src.utils.llm_factory import LLMFactory

class ScriptGenerator:
    def __init__(self):
        # 中温生成创意
        self.llm = LLMFactory.get_deepseek_llm(temperature=0.7)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个资深的文化短视频编剧。你将基于提供的【事实资料包】进行创作。\n"
                       "### 核心规则：\n"
                       "1. 必须严格遵守【事实资料包】中的 hard_facts（硬事实），不得编造历史年代、出土地、特征等具体信息。\n"
                       "2. 可以结合 semantic_docs 中的背景资料进行深度挖掘。\n"
                       "3. 风格必须符合用户要求的：{style}。\n"
                       "4. 脚本时长约为：{duration}。\n"
                       "5. 生成内容必须包含引用标注，如 [引用1] 表示引用了资料包中的内容。"),
            ("user", "【事实资料包】：\n{knowledge_bundle}\n\n"
                     "请为文物“{artifact_name}”撰写一个{content_type}脚本。")
        ])

    def generate(self, intent, knowledge_bundle: KnowledgeBundle):
        chain = self.prompt | self.llm
        return chain.invoke({
            "style": intent.style,
            "duration": intent.duration,
            "artifact_name": knowledge_bundle.hard_facts.name,
            "content_type": intent.content_type,
            "knowledge_bundle": knowledge_bundle.model_dump_json(indent=2)
        })
