from typing import List
from src.schemas.models import ArtifactHardFact, ExtractedFacts, ValidationResult

class RuleValidator:
    @staticmethod
    def validate(extracted: ExtractedFacts, hard_facts: ArtifactHardFact) -> ValidationResult:
        """
        基于确定性规则校验提取出的事实是否符合硬事实。
        """
        errors = []
        warnings = []
        matched_facts = []

        # 1. 年代校验
        if extracted.era and extracted.era != hard_facts.era:
            errors.append(f"年代冲突: 脚本提到 '{extracted.era}'，但数据库记录为 '{hard_facts.era}'")
        elif extracted.era:
            matched_facts.append(f"年代匹配: {extracted.era}")

        # 2. 地点校验 (出土地/现藏地)
        if extracted.location:
            if extracted.location not in [hard_facts.excavation_site, hard_facts.current_location]:
                warnings.append(f"未知地点: '{extracted.location}' 不在已知地点库中")
            else:
                matched_facts.append(f"地点匹配: {extracted.location}")

        # 3. 特征校验 (模糊匹配/包含关系)
        for feat in extracted.features:
            found = False
            for hard_feat in hard_facts.features:
                if feat in hard_feat or hard_feat in feat:
                    found = True
                    matched_facts.append(f"特征匹配: {feat}")
                    break
            if not found:
                warnings.append(f"新增描述: '{feat}' 为脚本新增特征，请人工确认是否符合史实")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            matched_facts=list(set(matched_facts))
        )
