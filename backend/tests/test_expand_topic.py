import asyncio
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

async def test_expand_topic_api():
    print(">>> 开始自动化测试 [AI 关键词智能扩写与换一换] 接口...")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        # 1. 模拟用户输入零散关键词：“立冬 萝卜 喝汤”
        payload_1 = {
            "category_id": "tcm_health",
            "template_id": "tcm_seasonal",
            "keywords": "立冬 萝卜 喝汤",
            "tone": "专业且通俗 (推荐)",
            "target_reader": "中老年人及养生关注者"
        }
        res_1 = await ac.post("/api/v1/creation/expand-topic?batch=1", json=payload_1)
        assert res_1.status_code == 200, f"Failed: {res_1.status_code}"
        data_1 = res_1.json()
        assert "suggestions" in data_1
        assert len(data_1["suggestions"]) == 3
        print(f"[PASS] 批次 1 获取到 3 组专业构思方案：")
        for i, s in enumerate(data_1["suggestions"], 1):
            print(f"   {i}. 主题: {s['topic']}")
            print(f"      行文要求: {s['supplementary'][:50]}...")
            assert len(s["topic"]) > 5
            assert len(s["supplementary"]) > 10

        # 2. 模拟点击“换一换”（batch=2）
        res_2 = await ac.post("/api/v1/creation/expand-topic?batch=2", json=payload_1)
        assert res_2.status_code == 200
        data_2 = res_2.json()
        assert len(data_2["suggestions"]) == 3
        print(f"[PASS] 批次 2 (换一换) 获取到全新视角的 3 组方案：")
        for i, s in enumerate(data_2["suggestions"], 1):
            print(f"   {i}. 主题: {s['topic']}")
        
        # 确保换一换的内容与第一批次不同
        assert data_1["suggestions"][0]["topic"] != data_2["suggestions"][0]["topic"], "换一换未生成不同方案！"
        print("[PASS] 换一换多角度发散校验成功！")

        # 3. 模拟书籍零散词：“被讨厌的勇气 讨好”
        payload_book = {
            "category_id": "book_review",
            "template_id": "book_deep_review",
            "keywords": "被讨厌的勇气 讨好",
            "tone": "逻辑严谨",
            "target_reader": "青年读者与深度阅读者"
        }
        res_book = await ac.post("/api/v1/creation/expand-topic?batch=1", json=payload_book)
        assert res_book.status_code == 200
        book_data = res_book.json()
        print(f"[PASS] 书籍关键词扩写成功：{book_data['suggestions'][0]['topic']}")

    print(">>> AI 关键词扩写与换一换端点自测 100% 通过！")

if __name__ == "__main__":
    asyncio.run(test_expand_topic_api())
