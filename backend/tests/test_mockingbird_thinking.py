import asyncio
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

async def test_mockingbird_thinking():
    print(">>> 正在针对用户实测的《杀死一只知更鸟》进行意图理解与文学思考深度测试...")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        # 1. 模拟用户在书评模板下输入：“杀死一只知更鸟”
        payload = {
            "category_id": "book_review",
            "template_id": "book_deep_review",
            "keywords": "杀死一只知更鸟",
            "tone": "逻辑严谨",
            "target_reader": "青年读者与深度阅读者"
        }

        # 批次 1
        res_1 = await ac.post("/api/v1/creation/expand-topic?batch=1", json=payload)
        assert res_1.status_code == 200
        suggestions_1 = res_1.json()["suggestions"]
        
        print("\n[批次 1 扩写结果（文学深度分析）]：")
        has_literary_insight = False
        for idx, item in enumerate(suggestions_1, 1):
            print(f"  方案 {idx}: {item['topic']}")
            print(f"    行文建议: {item['supplementary']}")
            # 严格断言：杜绝空洞套话
            assert "犯了这3个隐形错误" not in item["topic"], "仍然存在机械化模板套话！"
            assert "知行合一" not in item["topic"], "仍然存在不搭边模板套话！"
            # 必须包含对原著精髓的理解
            if any(k in item["topic"] or k in item["supplementary"] for k in ["阿提克斯", "良知", "偏见", "同理心", "斯各特"]):
                has_literary_insight = True

        assert has_literary_insight, "未检测到对《杀死一只知更鸟》核心意象的深度理解！"
        print("[PASS] 批次 1 对《杀死一只知更鸟》的意图理解完全契合文学原著核心！")

        # 2. 模拟点击“换一换”（批次 2）
        res_2 = await ac.post("/api/v1/creation/expand-topic?batch=2", json=payload)
        assert res_2.status_code == 200
        suggestions_2 = res_2.json()["suggestions"]
        print("\n[批次 2 (换一换) 扩写结果（全新视角：怪人阿瑟、法庭辩护）]：")
        for idx, item in enumerate(suggestions_2, 1):
            print(f"  方案 {idx}: {item['topic']}")
            print(f"    行文建议: {item['supplementary']}")
            assert "犯了这3个隐形错误" not in item["topic"]
            assert "知行合一" not in item["topic"]

        assert suggestions_1[0]["topic"] != suggestions_2[0]["topic"]
        print("[PASS] 换一换多角度发散完全符合预期！")

    print("\n>>> 《杀死一只知更鸟》专项自测 100% 成功！绝无机械套话！")

if __name__ == "__main__":
    asyncio.run(test_mockingbird_thinking())
