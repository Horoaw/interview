import os
import sys

def check_env():
    # 简单的环境检查
    try:
        import langchain_chroma
        import langchain_openai
        import pydantic
    except ImportError as e:
        print(f"Error: 缺少必要依赖 ({e})。")
        print("请确保已激活 conda 环境: conda activate interview_relic_env")
        sys.exit(1)

check_env()

from src.chains.intent_parser import IntentParser
from src.chains.script_generator import ScriptGenerator
from src.chains.fact_extractor import FactExtractor
from src.utils.rule_validator import RuleValidator
from src.schemas.models import ArtifactHardFact, KnowledgeBundle

def run_demo():
    # 0. 检查 API Key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("Error: 请在 .env 文件中设置 DEEPSEEK_API_KEY")
        return

    print("--- 步骤 1: 用户意图解析 ---")
    user_input = "以青铜面具为主角，写一个60秒悬疑风短视频脚本"
    parser = IntentParser()
    intent = parser.parse(user_input)
    print(f"解析结果: {intent.model_dump_json(indent=2)}")

    print("\n--- 步骤 2: 资料组织 (Real Data Loading via PDF & RAG) ---")
    from src.data_loader.relic_loader import RelicDataLoader
    # 这里我们根据意图中的 artifact_query 匹配 ID，简单 demo 默认为 sanxingdui_bronze_mask_01
    loader = RelicDataLoader()
    try:
        knowledge_bundle = loader.get_knowledge_bundle(
            artifact_id="sanxingdui_bronze_mask_01", 
            query=intent.artifact_query
        )
        hard_facts = knowledge_bundle.hard_facts
        print(f"资料包就绪: {hard_facts.name}")
        print(f"检索到 {len(knowledge_bundle.semantic_docs)} 条相关背景资料。")
        
        # --- 召回率/覆盖率评价 (新增) ---
        print("\n--- 召回质量评价 (Recall Evaluation) ---")
        from src.utils.llm_factory import LLMFactory
        evaluator = LLMFactory.get_deepseek_llm(temperature=0.0)
        eval_prompt = (
            "你是一个检索质量评价专家。请对比【用户意图】和【检索到的资料】，评价资料是否覆盖了意图中的关键信息点。\n"
            f"用户意图: {user_input}\n"
            f"检索资料: {' | '.join(knowledge_bundle.semantic_docs)}\n"
            "请给出 0-1 之间的覆盖率评分，并简要说明理由。格式：评分: 0.xx | 理由: ..."
        )
        eval_res = evaluator.invoke(eval_prompt)
        print(f"召回评价: {eval_res.content}")
    except Exception as e:
        print(f"资料加载失败: {e}")
        return

    print("\n--- 步骤 3: 脚本生成 (Controlled Generation) ---")
    generator = ScriptGenerator()
    script_output = generator.generate(intent, knowledge_bundle)
    script_content = script_output.content
    print("生成脚本:")
    print("-" * 30)
    print(script_content)
    print("-" * 30)

    print("\n--- 步骤 4: 事实提取 ---")
    extractor = FactExtractor()
    extracted = extractor.extract(script_content)
    print(f"提取事实: {extracted.model_dump_json(indent=2)}")

    print("\n--- 步骤 5: 规则校验 (Engineering Layer) ---")
    validator = RuleValidator()
    result = validator.validate(extracted, hard_facts)
    print(f"校验结果: {'通过' if result.is_valid else '失败'}")
    if result.errors:
        print(f"错误: {result.errors}")
    if result.warnings:
        print(f"警告: {result.warnings}")
    print(f"匹配事实: {result.matched_facts}")

    if not result.is_valid:
        print("\n[中断] 脚本校验不通过，停止后续分镜生成。")
        return

    print("\n--- 步骤 6: 分镜拆解 (Storyboarding) ---")
    from src.chains.storyboard_generator import StoryboardGenerator
    storyboarder = StoryboardGenerator()
    scenes = storyboarder.generate_storyboard(script_content)
    print(f"生成分镜数量: {len(scenes)}")

    print("\n--- 步骤 7: 多模态 Prompt 转换 (Visual Logic) ---")
    from src.chains.prompt_converter import PromptConverter
    converter = PromptConverter()
    for scene in scenes:
        visual_prompt = converter.convert(scene)
        scene.visual_prompt = visual_prompt
        print(f"\n[分镜 {scene.scene_id} - {scene.time_range}]")
        print(f"主体: {scene.visual_subject}")
        print(f"视觉提示词: {visual_prompt.positive_prompt}")
        print(f"镜头运动: {visual_prompt.camera_motion}")

    print("\n---  脚本生成链执行完毕 ---")

if __name__ == "__main__":
    run_demo()
