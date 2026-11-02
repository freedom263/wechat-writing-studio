import httpx

def test_live_expand():
    print(">>> 正在向 8000 端口测试运行中的 AI 意图扩写与换一换接口...")
    url = "http://127.0.0.1:8000/api/v1/creation/expand-topic"
    
    # 1. 模拟用户只输入了零散词：“立冬 萝卜 喝汤”
    req_1 = {
        "category_id": "tcm_health",
        "template_id": "tcm_seasonal",
        "keywords": "立冬 萝卜 喝汤",
        "tone": "专业且通俗 (推荐)",
        "target_reader": "中老年人及养生关注者"
    }
    r1 = httpx.post(f"{url}?batch=1", json=req_1, timeout=10.0)
    assert r1.status_code == 200, f"Error {r1.status_code}: {r1.text}"
    sug_1 = r1.json()["suggestions"]
    print(f"\n[验证 1] 输入零散词「立冬 萝卜 喝汤」，第一批生成方案：")
    for i, s in enumerate(sug_1, 1):
        print(f"  {i}. {s['topic']}")
        print(f"     补充要求: {s['supplementary']}")

    # 2. 模拟点击“换一换” (batch=2)
    r2 = httpx.post(f"{url}?batch=2", json=req_1, timeout=10.0)
    assert r2.status_code == 200
    sug_2 = r2.json()["suggestions"]
    print(f"\n[验证 2] 点击「换一换」，第二批生成全新视角方案：")
    for i, s in enumerate(sug_2, 1):
        print(f"  {i}. {s['topic']}")

    assert sug_1[0]["topic"] != sug_2[0]["topic"]
    print("\n>>> 运行中的接口测试 100% 成功，换一换功能表现完美！")

if __name__ == "__main__":
    test_live_expand()
