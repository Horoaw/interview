import os
import json
import requests
from typing import List, Optional
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from src.schemas.models import ArtifactHardFact, KnowledgeBundle

class VolcEngineEmbeddings:
    def __init__(self, model: str, api_key: str, base_url: str = "https://ark.cn-beijing.volces.com/api/v3"):
        self.model = model
        self.api_key = api_key
        self.url = f"{base_url.rstrip('/')}/embeddings/multimodal"

    def _get_embedding(self, text: str) -> List[float]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "input": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=20)
            if response.status_code != 200:
                raise Exception(f"API Error {response.status_code}: {response.text}")
            result = response.json()
            data = result.get("data")
            if isinstance(data, dict):
                return data["embedding"]
            elif isinstance(data, list) and len(data) > 0:
                return data[0]["embedding"]
            else:
                raise Exception(f"无法从响应中解析 embedding 数据: {result}")
        except Exception as e:
            print(f"\n[Embedding Error] 多模态接口调用失败。")
            print(f"Model: {self.model}, Error: {str(e)}")
            raise e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._get_embedding(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._get_embedding(text)

class RelicDataLoader:
    def __init__(self, persist_directory: str = "db/chroma_db", artifacts_path: str = "data/artifacts.json"):
        self.persist_directory = persist_directory
        self.artifacts_path = artifacts_path
        
        self.embeddings = VolcEngineEmbeddings(
            model=os.getenv("VOLC_EMBEDDING_ENDPOINT_ID"),
            api_key=os.getenv("VOLC_API_KEY"),
            base_url=os.getenv("VOLC_EMBEDDING_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        )
        
        self.vector_db = None
        self._init_vector_db()

    def _init_vector_db(self):
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            self.vector_db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            self.ingest_raw_data("data/raw")

    def ingest_raw_data(self, raw_dir: str):
        documents = []
        if not os.path.exists(raw_dir):
            os.makedirs(raw_dir)
            
        for file in os.listdir(raw_dir):
            if file.endswith(".pdf"):
                loader = PyMuPDFLoader(os.path.join(raw_dir, file))
                documents.extend(loader.load())
        
        if not documents:
            print(f"Warning: No PDF files found in {raw_dir}")
            return

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, 
            chunk_overlap=150,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
        splits = text_splitter.split_documents(documents)
        
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)

        self.vector_db = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print(f"Successfully ingested {len(splits)} chunks into vector database.")

    def load_hard_facts(self, artifact_id: str) -> Optional[ArtifactHardFact]:
        if not os.path.exists(self.artifacts_path):
            return None
        with open(self.artifacts_path, 'r', encoding='utf-8') as f:
            artifacts = json.load(f)
            for item in artifacts:
                if item['artifact_id'] == artifact_id:
                    return ArtifactHardFact(**item)
        return None

    def load_semantic_content(self, query: str, top_k: int = 4) -> List[str]:
        if not self.vector_db:
            return []
        
        # 多路查询扩展
        queries = [
            query,
            f"{query} 的历史背景和特征",
            f"{query} 与三星堆文明的关系"
        ]
        
        all_docs = []
        for q in queries:
            docs = self.vector_db.max_marginal_relevance_search(
                q, k=2, fetch_k=10, lambda_mult=0.6
            )
            all_docs.extend(docs)
            
        # 去重
        unique_contents = list(set([doc.page_content for doc in all_docs]))
        return unique_contents[:top_k]

    def get_knowledge_bundle(self, artifact_id: str, query: str) -> KnowledgeBundle:
        hard_facts = self.load_hard_facts(artifact_id)
        if not hard_facts:
            raise ValueError(f"Artifact ID '{artifact_id}' not found.")
        semantic_docs = self.load_semantic_content(query)
        return KnowledgeBundle(
            hard_facts=hard_facts,
            semantic_docs=semantic_docs,
            creative_tags=["史实背景", "文化研究"]
        )
