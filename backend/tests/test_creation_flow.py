import asyncio
import json
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

async def run_flow_test():
    print(">>> 开始测试 AI 创作流（大纲生成与全文生成）...")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. 模拟提交大纲生成请求
        payload = {
            "category_id": "tcm_health",
            "template_id": "tcm_seasonal",
            "input_type": "topic",
            "topic": "霜降节气老胃肠防寒调养指南",
            "supplementary": "给老母亲和中老年朋友的科普，推荐代茶饮",
            "word_count": 1500,
            "tone": "专业温和",
            "target_reader": "中老年人与养生爱好者"
        }
        
        article_id = None
        candidates_received = []

        async with ac.stream("POST", "/api/v1/creation/generate-outline-stream", json=payload) as response:
            assert response.status_code == 200, f"Generate outline failed: {response.status_code}"
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    try:
                        data_json = json.loads(data_str)
                        if "candidate_count" in data_json:
                            article_id = data_json["article_id"]
                        elif "index" in data_json and "title" in data_json:
                            candidates_received.append(data_json)
                    except Exception:
                        pass
        
        assert article_id is not None, "Article ID was not returned"
        assert len(candidates_received) >= 1, "No outline candidate was received"
        print(f"[PASS] 成功流式生成大纲方案，获取到 {len(candidates_received)} 组候选方案")
        selected_cand = candidates_received[0]
        print(f"       首选标题: {selected_cand['title']}")

        # 2. 模拟选定方案生成全文正文
        article_payload = {
            "article_id": article_id,
            "selected_title": selected_cand["title"],
            "confirmed_outline": "\n".join(selected_cand.get("outline_sections", []))
        }

        generated_text = ""
        is_completed = False
        async with ac.stream("POST", "/api/v1/creation/generate-article-stream", json=article_payload) as response:
            assert response.status_code == 200, f"Generate article failed: {response.status_code}"
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data_json = json.loads(line[6:])
                        if "content" in data_json:
                            generated_text += data_json["content"]
                        if data_json.get("status") == "completed":
                            is_completed = True
                    except Exception:
                        pass

        assert is_completed, "Article generation did not mark complete"
        assert len(generated_text) > 200, f"Generated text too short ({len(generated_text)} chars)"
        assert "健康提示" in generated_text, "Medical compliance disclaimer is missing!"
        print(f"[PASS] 全文流式生成成功，字数: {len(generated_text)}，已自动注入医疗免责声明！")

        # 3. 检查文章草稿箱读取
        get_res = await ac.get(f"/api/v1/articles/{article_id}")
        assert get_res.status_code == 200
        art_detail = get_res.json()
        assert art_detail["status"] == "completed"
        print(f"[PASS] 文章草稿箱归档与数据持久化校验通过！")

    print(">>> 创作全链路端到端闭环验证 100% 成功！")

if __name__ == "__main__":
    asyncio.run(run_flow_test())
