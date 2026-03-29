from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ArtifactHardFact(BaseModel):
    artifact_id: str
    name: str
    era: str
    material: str
    excavation_site: str
    current_location: str
    dimensions: str
    features: List[str]

class KnowledgeBundle(BaseModel):
    hard_facts: ArtifactHardFact
    semantic_docs: List[str]
    creative_tags: List[str]

class Intent(BaseModel):
    artifact_query: str
    style: str
    duration: str
    content_type: str

class ExtractedFacts(BaseModel):
    era: Optional[str] = Field(description="脚本中提到的年代")
    location: Optional[str] = Field(description="脚本中提到的地点")
    features: List[str] = Field(default_factory=list, description="脚本中提到的具体特征")

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    matched_facts: List[str]

class VisualPrompt(BaseModel):
    positive_prompt: str = Field(description="多模态生成工具的正向提示词")
    negative_prompt: str = Field(default="low quality, blurry, distorted", description="负向提示词")
    camera_motion: str = Field(description="镜头运动描述")
    aspect_ratio: str = Field(default="16:9")

class Scene(BaseModel):
    scene_id: int
    time_range: str
    visual_subject: str = Field(description="画面主体描述")
    emotion: str = Field(description="情感氛围")
    script_text: str = Field(description="对应的脚本台词/旁白")
    visual_prompt: Optional[VisualPrompt] = None
