import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_volc_embedding():
    api_key = os.getenv("VOLC_API_KEY")
    endpoint_id = os.getenv("VOLC_EMBEDDING_ENDPOINT_ID")
    base_url = os.getenv("VOLC_EMBEDDING_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

    print(f"--- 正在测试火山引擎 Embedding 权限 ---")
    print(f"Endpoint ID: {endpoint_id}")
    print(f"Base URL: {base_url}")
    
    if not api_key or not endpoint_id:
        print("错误: 请确保 .env 中设置了 VOLC_API_KEY 和 VOLC_EMBEDDING_ENDPOINT_ID")
        return

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    try:
        response = client.embeddings.create(
            model=endpoint_id,
            input=["测试文本"]
        )
        print("✅ 权限校验通过！成功获取 Embedding。")
        print(f"向量维度: {len(response.data[0].embedding)}")
    except Exception as e:
        print(f"❌ 校验失败: {e}")
        print("\n排查建议:")
        print("1. 检查 Endpoint ID 是否包含 'ep-' 前缀 (例如 ep-2024xxxxxx-xxxxx)")
        print("2. 确认该 Endpoint ID 是在控制台中针对 'Doubao-embedding' 模型创建的")
        print("3. 确认 API Key 拥有访问该接入点 (Endpoint) 的权限")

if __name__ == "__main__":
    test_volc_embedding()
