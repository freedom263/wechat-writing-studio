import asyncio
import json
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

async def test_dynamic_categories():
    print(">>> 开始测试跨赛道动态生成，确保绝对杜绝‘全屏中医’硬编码问题...")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        # 1. 测试【读书书评】赛道
        print("\n[1/3] 测试【读书书评】赛道...")
        book_payload = {
            "category_id": "book_review",
            "template_id": "book_deep_review",
            "input_type": "topic",
            "topic": "《被讨厌的勇气》：如何践行课题分离",
            "supplementary": "探讨当代青年的心理内耗与自由",
            "word_count": 1500,
            "tone": "逻辑严谨",
            "target_reader": "青年读者与深度阅读者"
        }
        
        book_article_id = None
        book_candidates = []
        async with ac.stream("POST", "/api/v1/creation/generate-outline-stream", json=book_payload) as resp:
            assert resp.status_code == 200
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    try:
                        d = json.loads(line[6:])
                        if "article_id" in d:
                            book_article_id = d["article_id"]
                        elif "title" in d and "index" in d:
                            book_candidates.append(d)
                    except Exception:
                        pass

        assert len(book_candidates) == 3, f"Expected 3 candidates, got {len(book_candidates)}"
        for c in book_candidates:
            print(f"   - 候选标题: {c['title']}")
            assert "脾胃" not in c["title"], f"Found TCM keyword in book candidate: {c['title']}"
            assert "中医" not in c["title"], f"Found TCM keyword in book candidate: {c['title']}"
            assert "《被讨厌的勇气》" in c["title"] or "课题分离" in c["title"] or "勇气" in c["title"], "Topic not reflected in candidate title"

        # 生成书评全文
        book_article_text = ""
        gen_payload = {
            "article_id": book_article_id,
            "selected_title": book_candidates[0]["title"],
            "confirmed_outline": "\n".join(book_candidates[0].get("outline_sections", []))
        }
        async with ac.stream("POST", "/api/v1/creation/generate-article-stream", json=gen_payload) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    try:
                        d = json.loads(line[6:])
                        if "content" in d:
                            book_article_text += d["content"]
                    except Exception:
                        pass
        assert "课题分离" in book_article_text or "被讨厌的勇气" in book_article_text
        assert "老胃肠" not in book_article_text
        assert "脾胃" not in book_article_text
        print(f"[PASS] 读书书评测试通过！正文字数: {len(book_article_text)}，完全脱离中医内容。")

        # 2. 测试【职场成长】赛道
        print("\n[2/3] 测试【职场成长】赛道...")
        wp_payload = {
            "category_id": "workplace",
            "template_id": "wp_communication",
            "input_type": "topic",
            "topic": "向上汇报的3个黄金法则",
            "supplementary": "结构化话术示例",
            "word_count": 1500,
            "tone": "专业通俗",
            "target_reader": "职场白领与青年"
        }
        wp_candidates = []
        wp_article_id = None
        async with ac.stream("POST", "/api/v1/creation/generate-outline-stream", json=wp_payload) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    try:
                        d = json.loads(line[6:])
                        if "article_id" in d:
                            wp_article_id = d["article_id"]
                        elif "title" in d and "index" in d:
                            wp_candidates.append(d)
                    except Exception:
                        pass
        assert len(wp_candidates) == 3
        for c in wp_candidates:
            print(f"   - 候选标题: {c['title']}")
            assert "脾胃" not in c["title"]
            assert "汇报" in c["title"] or "职场" in c["title"]
        print("[PASS] 职场成长测试通过！")

        # 3. 测试【中医健康】赛道（确保母亲要用的专属功能依然健壮）
        print("\n[3/3] 测试【中医健康】赛道...")
        tcm_payload = {
            "category_id": "tcm_health",
            "template_id": "tcm_seasonal",
            "input_type": "topic",
            "topic": "立冬节气温阳防寒调护",
            "supplementary": "药食同源代茶饮",
            "word_count": 1500,
            "tone": "专业且通俗 (推荐)",
            "target_reader": "中老年人及养生关注者"
        }
        tcm_candidates = []
        tcm_article_id = None
        async with ac.stream("POST", "/api/v1/creation/generate-outline-stream", json=tcm_payload) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    try:
                        d = json.loads(line[6:])
                        if "article_id" in d:
                            tcm_article_id = d["article_id"]
                        elif "title" in d and "index" in d:
                            tcm_candidates.append(d)
                    except Exception:
                        pass
        assert len(tcm_candidates) == 3
        print(f"   - 候选标题: {tcm_candidates[0]['title']}")
        print("[PASS] 中医健康测试通过！")

    print("\n>>> 所有跨赛道动态生成自测 100% 通过！")

if __name__ == "__main__":
    asyncio.run(test_dynamic_categories())
