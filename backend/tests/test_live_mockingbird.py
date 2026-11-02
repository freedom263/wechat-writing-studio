import httpx
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_live():
    res = httpx.post("http://127.0.0.1:8000/api/v1/creation/expand-topic?batch=1", json={
        "category_id": "book_review",
        "template_id": "book_deep_review",
        "keywords": "杀死一只知更鸟",
        "tone": "逻辑严谨",
        "target_reader": "青年读者与深度阅读者"
    })
    print("STATUS:", res.status_code)
    for i, s in enumerate(res.json()["suggestions"], 1):
        print(f"{i}. {s['topic']}")
        print(f"   建议: {s['supplementary']}")

if __name__ == "__main__":
    test_live()
