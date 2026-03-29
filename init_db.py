import os
from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark
from src.data_loader.relic_loader import RelicDataLoader

# 1. 加载环境变量
load_dotenv()

def diagnostic_test():
    """使用 requests 模拟多模态接口诊断测试"""
    api_key = os.getenv("VOLC_API_KEY")
    endpoint_id = os.getenv("VOLC_EMBEDDING_ENDPOINT_ID")
    base_url = os.getenv("VOLC_EMBEDDING_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3").rstrip('/')
    url = f"{base_url}/embeddings/multimodal"

    print(f"--- 最终诊断测试 (Multimodal Only) ---")
    print(f"Endpoint: {url}")
    print(f"Model: {endpoint_id}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": endpoint_id,
        "input": [{"type": "text", "text": "测试文本"}]
    }
    
    try:
        import requests
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        print(f"HTTP Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            try:
                # 兼容字典格式和列表格式
                data = result.get("data")
                if isinstance(data, dict):
                    vec = data["embedding"]
                else:
                    vec = data[0]["embedding"]
                print(f"多模态接口诊断成功！向量维度: {len(vec)}")
                return True
            except (KeyError, IndexError, TypeError) as e:
                print(f" 响应解析失败。实际返回结构: {result}")
                print(f"解析错误详情: {e}")
                return False
        else:
            print(f"诊断失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"诊断执行出错: {e}")
    return False

def init_db():
    print("\n--- 正在初始化向量数据库 ---")
    try:
        loader = RelicDataLoader(persist_directory="db/chroma_db", artifacts_path="data/artifacts.json")
        print(f"数据库初始化完成，存储路径: {loader.persist_directory}")
        
        test_query = "纵目面具的特征是什么？"
        results = loader.load_semantic_content(test_query, top_k=2)
        print(f"\n测试检索结果 (Query: '{test_query}'):")
        if not results:
            print("未找到相关内容，请检查 PDF 内容或增加检索 Top-K。")
        for i, res in enumerate(results):
            print(f"[{i+1}] {res[:100]}...")
            
    except Exception as e:
        print(f"初始化过程中出错: {e}")

if __name__ == "__main__":
    if diagnostic_test():
        init_db()
    else:
        print("\n[错误] 所有接口尝试均失败。")
        print("建议：请检查控制台输出的错误信息，并确认控制台中的 Endpoint ID 是否已启用且拼写正确。")
