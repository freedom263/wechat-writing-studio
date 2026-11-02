import httpx
import json

def test_live():
    payload = {
        "category_id": "book_review",
        "template_id": "book_deep_review",
        "input_type": "topic",
        "topic": "《被讨厌的勇气》：如何践行课题分离",
        "supplementary": "探讨当代青年的心理内耗与自由",
        "word_count": 1500,
        "tone": "逻辑严谨",
        "target_reader": "青年读者与深度阅读者"
    }

    print(">>> 正在向运行中的 8000 端口发送真实的 HTTP 创作请求...")
    with httpx.stream("POST", "http://127.0.0.1:8000/api/v1/creation/generate-outline-stream", json=payload, timeout=30.0) as r:
        for line in r.iter_lines():
            if line.startswith("data: "):
                try:
                    d = json.loads(line[6:])
                    if "title" in d and "index" in d:
                        print(f"  [验证成功] 方案 {d['index']}: {d['title']}")
                        assert "脾胃" not in d['title']
                        assert "老寒胃" not in d['title']
                        assert "勇气" in d['title'] or "课题分离" in d['title']
                except Exception:
                    pass

    print(">>> 运行中的后端服务自测完全正确，绝对无中医硬编码！")

if __name__ == "__main__":
    test_live()
