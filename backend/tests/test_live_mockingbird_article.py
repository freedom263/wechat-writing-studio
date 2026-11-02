import httpx
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_article():
    # 1. 提交大纲
    outline_res = httpx.post("http://127.0.0.1:8000/api/v1/creation/generate-outline-stream", json={
        "category_id": "book_review",
        "template_id": "book_deep_review",
        "input_type": "topic",
        "topic": "《杀死一只知更鸟》：阿提克斯给全天下父母最震撼的一堂良知课",
        "supplementary": "深度书评",
        "word_count": 1500,
        "tone": "逻辑严谨",
        "target_reader": "青年读者与深度阅读者"
    })
    art_id = None
    for l in outline_res.text.split("\n"):
        if l.startswith("data: ") and "article_id" in l:
            art_id = json.loads(l[6:])["article_id"]
    
    assert art_id, "No article_id"
    print(f"Article ID created: {art_id}")

    # 2. 生成正文
    gen_res = httpx.post("http://127.0.0.1:8000/api/v1/creation/generate-article-stream", json={
        "article_id": art_id,
        "selected_title": "《杀死一只知更鸟》：阿提克斯给全天下父母最震撼的一堂良知课",
        "confirmed_outline": "一、杀死知更鸟是一种罪过\n二、唯有钻进别人的皮囊走一走\n三、真正的勇敢"
    })
    
    full_text = ""
    for l in gen_res.text.split("\n"):
        if l.startswith("data: ") and "content" in l:
            full_text += json.loads(l[6:])["content"]

    print("Generated full article length:", len(full_text))
    assert "阿提克斯" in full_text
    assert "哈珀·李" in full_text
    assert "知更鸟" in full_text
    assert "老寒胃" not in full_text
    assert "脾胃" not in full_text
    print(">>> 杀死一只知更鸟 全文深度生成自测 100% 成功！")

if __name__ == "__main__":
    test_article()
