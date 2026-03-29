# 文物 IP 内容自动化生产链 —— 工程化 RAG 与去幻觉方案

本项目是针对“文化 + AI”方向设计的**内容自动化生产流水线**。核心目标是解决大语言模型（LLM）在创意生成中的“史实幻觉”痛点，通过工程化手段实现从原始文献组织到多模态分镜生成的全链路自动化。

---

运行示例：
![interview](https://github.com/user-attachments/assets/d2bdd099-67d2-46b7-858d-2ab22039a8fb)

<img width="757" height="507" alt="image" src="https://github.com/user-attachments/assets/9d8bd7d4-6ba5-4488-b475-0b02cae67871" />




在脚本输出里面都有向量库引用出处和与知识库中数据不符合或存疑的标注输出方便确认输出是否正确和人工核验。更直观的看到[召回结果是否正确](#输出示例)。
---

##  核心设计哲学

1.  **事实与创意解耦**：LLM 仅作为“语言组织者”，事实来源被外挂在向量库和结构化 JSON 中。
2.  **验证与生成解耦**：生成过程允许中温采样以保证创意，但验证过程采用 Python 确定性逻辑（Single Source of Truth），确保史实零差错。
3.  **闭环反馈机制**：通过“提取-对撞-拦截”机制，实现从“黑盒生成”到“白盒监控”的转变。

---

##  系统架构

### 全链路生产流程 (7-Step Pipeline)

```mermaid
graph TD
    classDef user fill:#f9f,stroke:#333,stroke-width:2px;
    classDef llm fill:#00c5ff,stroke:#0078a8,color:#fff;
    classDef data fill:#f96,stroke:#d35400,color:#fff;
    classDef logic fill:#2ecc71,stroke:#27ae60,color:#fff;
    classDef output fill:#f1c40f,stroke:#f39c12,color:#333;

    A([用户创意需求]) --> B[意图解析<br/>DeepSeek LLM]
    B --> C{Relic Data Loader}
    
    subgraph "资料组织层 (RAG Layer)"
        C --> D1[硬事实读取<br/>artifacts.json]
        C --> D2[多路查询改写<br/>Multi-Query Expansion]
        D2 --> D3[语义检索<br/>ChromaDB + Volcengine]
        D3 --> D4[多样性重排<br/>MMR Algorithm]
    end

    D1 & D4 --> E[知识包 Knowledge Bundle]
    
    subgraph "校验与生成层 (Logic Layer)"
        E --> F[召回质量评价<br/>Recall Judge]
        F --> G[受控脚本生成<br/>Controlled Generation]
        G --> H[实体事实提取<br/>Fact Extractor]
        H --> I{规则一致性校验<br/>Deterministic Engine}
        I -- 冲突重写 --> G
    end

    subgraph "多模态对接 (Integration)"
        I -- 校验通过 --> J[分镜拆解 Storyboard]
        J --> K[视觉 Prompt 专家]
    end

    K --> L([最终分镜与多模态 Prompts])

    class A user;
    class B,F,G,H,J,K llm;
    class D1,D2,D3,D4 data;
    class I logic;
    class L output;
```

---

##  关键技术细节

### 1. 深度检索优化 (RAG Optimization)
*   **多路查询改写 (Multi-Query Expansion)**：系统自动将用户查询扩展为“背景”、“特征”、“文化关联”等维度，极大提升了从海量 PDF 文献中检索相关信息的**召回率 (Recall Rate)**。
*   **MMR 重排算法 (Max Marginal Relevance)**：在向量搜索中平衡相关性与多样性，强制选取互补的文本片段，避免 LLM 上下文出现冗余。
*   **自适应 API 适配器**：针对火山引擎 `doubao-embedding-vision` 多模态模型的特殊接口（`/embeddings/multimodal`），自研了 `VolcEngineEmbeddings` 适配类，处理其非标准的输入结构与 JSON 响应。

### 2. 自动化一致性引擎 (Consistency Engine)
*   **确定性校验**：放弃 LLM 自检，改用 Python 逻辑。通过 `FactExtractor` 提取分镜实体，并与底座数据库（Single Source of Truth）进行对撞，强制约束年代、地点等关键硬事实。
*   **Recall Evaluation (LLM-as-a-Judge)**：在生成前对检索质量进行实时打分，量化评估资料对用户意图的覆盖度。

---

##  技术栈

*   **LLM**: DeepSeek-V3 / Chat (创意生成与逻辑解析)
*   **Embeddings**: Volcengine (Doubao) Multimodal Embedding (向量化)
*   **Vector DB**: ChromaDB (本地向量索引)
*   **Orchestration**: LangChain (链式调度)
*   **Logic**: Pydantic + Python Rule Engine (事实校验)

---

##  快速开始

### 1. 环境准备
```bash
conda activate interview_relic_env
pip install -r requirements.txt
```

### 2. 配置密钥
修改 `.env` 文件，填入：
* `DEEPSEEK_API_KEY`: 用于文本生成。
* `VOLC_API_KEY`: 用于向量检索。
* `VOLC_EMBEDDING_ENDPOINT_ID`: 设置为 `doubao-embedding-vision-251215`。

### 3. 初始化数据库 (PDF 向量化)
```bash
# 确保 data/raw 目录下存有原始 PDF 资料
rm -rf db/chroma_db
python init_db.py
```

### 4. 运行端到端演示
```bash
python demo.py
```

---

## 运行结果示例 (Execution Example)

```text
--- 步骤 1: 用户意图解析 ---
解析结果: {
  "artifact_query": "青铜纵目面具",
  "style": "悬疑",
  "duration": "60秒",
  "content_type": "短视频脚本"
}

--- 步骤 2: 资料组织 (Real Data Loading via PDF & RAG) ---
资料包就绪: 青铜纵目面具
检索到 4 条相关背景资料。

--- 召回质量评价 (Recall Evaluation) ---
召回评价: 评分: 0.95 | 理由: 检索资料完整覆盖了纵目面具的“柱状外突”眼球特征、蚕丛王传说及二号坑出土背景，足以支撑悬疑叙事。

--- 步骤 3: 脚本生成 (Controlled Generation) ---
生成脚本:
------------------------------
【标题：古蜀的凝视】
（场景：黑暗寂静的展厅）
旁白：三千年前，古蜀王蚕丛在鸭子河畔种下秘密 [引用1]。
（镜头特写：面具那双极度夸张、呈柱状外突的眼球）
旁白：这不仅是青铜的冷光，更是跨越时空的凝视。谁能解释这双“纵目”背后的神启？ [引用2]
------------------------------

--- 步骤 4: 事实提取 ---
提取事实: {
  "era": "商代晚期",
  "location": "三星堆遗址二号祭祀坑",
  "features": ["眼球柱状外突", "两耳展开"]
}

--- 步骤 5: 规则校验 (Engineering Layer) ---
校验结果: 通过
匹配事实: ['年代匹配: 商代晚期', '地点匹配: 三星堆遗址二号祭祀坑', '特征匹配: 眼球柱状外突']

--- 步骤 6: 分镜拆解 (Storyboarding) ---
生成分镜数量: 3

--- 步骤 7: 多模态 Prompt 转换 (Visual Logic) ---
[分镜 1 - 0-10s]
主体: 三星堆青铜纵目面具，极度夸张的柱状眼球
视觉提示词: Cinematic close-up of Sanxingdui Bronze Mask, exaggerated cylindrical protruding eyeballs, ancient bronze texture with green patina, mysterious atmosphere, dramatic side lighting, 8k resolution, historical suspense style --ar 16:9
镜头运动: 缓慢推进 (Slow Zoom-in)

---  自动化生产链执行完毕 ---
```

---

##  目录结构说明

- `src/chains/`：包含意图解析、脚本生成、事实提取、分镜拆解等核心逻辑。
- `src/data_loader/`：封装了自研的 `RelicDataLoader` 与 `VolcEngineEmbeddings` 适配器。
- `src/utils/`：LLM 工厂类及确定性校验规则引擎。
- `data/`：存放原始 PDF (RAG 数据源) 与 `artifacts.json` (硬事实数据源)。
- `db/`：ChromaDB 持久化存储。


---

