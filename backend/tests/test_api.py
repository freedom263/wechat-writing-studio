import asyncio
from httpx import AsyncClient, ASGITransport
import sys
import os

# 确保导入路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

async def run_tests():
    print(">>> 开始运行 API 端点回归测试...")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. 根服务检测
        res = await ac.get("/")
        assert res.status_code == 200, f"Root endpoint failed: {res.status_code}"
        print(f"[PASS] 根路径检查通过: {res.json()['service']}")

        # 2. 赛道与模板列表
        res = await ac.get("/api/v1/categories")
        assert res.status_code == 200, f"Categories endpoint failed: {res.status_code}"
        categories = res.json()
        assert len(categories) == 11, f"Expected 11 categories, got {len(categories)}"
        print(f"[PASS] 成功获取 11 大赛道，包含首位：{categories[0]['name']}")

        # 3. 中医/医疗专属模板检查
        tcm_cat = next(c for c in categories if c["id"] == "tcm_health")
        assert len(tcm_cat["templates"]) == 5, f"Expected 5 TCM templates, got {len(tcm_cat['templates'])}"
        print(f"[PASS] 中医医疗 5 大专属模板已正确关联")

        # 4. 提示词资产与合规免责声明检查
        res_prompt = await ac.get("/api/v1/prompts/tcm_seasonal")
        assert res_prompt.status_code == 200, "Prompts endpoint failed"
        prompts = res_prompt.json()
        assert len(prompts) == 2, "Expected 2 prompts (outline & article)"
        assert prompts[0]["append_disclaimer"] is True, "Medical prompt disclaimer guard failed"
        print(f"[PASS] 中医提示词资产已正确绑定合规免责护栏")

    print(">>> 所有基础 API 测试通过！")

if __name__ == "__main__":
    asyncio.run(run_tests())
