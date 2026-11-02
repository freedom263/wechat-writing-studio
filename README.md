# 文思 · 微信公众号创作工作台 (WeChat Writing Studio)

> 基于正规互联网公司标准产研流程（PRD $\to$ 架构设计 $\to$ 接口契约 $\to$ Sprint 敏捷交付 $\to$ 回归测试）打造的高质量公众号 AI 创作平台。

---

## 🌟 核心特色与设计亮点

1. **为专业医生与健康科普量身定制**：
   * 首期内置**「中医健康 / 医疗养生」**重点赛道。
   * 预置 5 款医生专属科普模板：**时令节气调理**、**常见病辨证科普**、**本草与穴位速懂**、**门诊医案叙事**、**中西医健康辟谣**。
   * 内置**医疗合规护栏**：严禁绝对化神效词汇、自动挂载微信合规免责声明，保障账号安全。
2. **11 大垂直内容赛道支持**：
   * 中医健康、读书书评、时事观点、职场成长、情感心理、科技商业、生活方式、家庭教育、历史人文、旅行游记、产品运营。
3. **提示词（Prompt）资产化独立中台**：
   * 彻底告别提示词写死在代码里的痛点，支持在界面中针对任一赛道模板的 System/User Prompt 进行**在线热调优**，即时保存生效。
4. **高质量创作闭环与流式响应**：
   * **多模式输入**：自由主题输入 / 微信文章外部链接一键抓取清洗 / 素材库调用。
   * **DeepSeek SSE 流式输出**：一键生成 3 组差异化候选大纲 $\to$ 选定大纲流式生成万字长文。
   * **双栏实时编辑与排版**：左侧 Markdown 源码编辑，右侧微信移动端排版样式实时预览，支持**一键复制富文本至微信后台（格式完全保留）**。
5. **平滑商用过渡架构**：
   * 接口契约和数据库模型预留 `user_id`，当前自用阶段采用单文件轻量 SQLite（零安装门槛），未来商业化时一行配置无痛切换至云端 PostgreSQL。

---

## 🚀 极速一键启动

### 方式 1：双击批处理（推荐）
在项目根目录下双击运行：
```text
start_services.bat
```
它将自动并行拉起后端服务与前端工作台。

### 方式 2：终端手动启动
* **启动后端 (FastAPI)**：
  ```bash
  $env:PYTHONPATH="backend"
  backend\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
  ```
  * Swagger 交互式接口文档：[http://localhost:8000/docs](http://localhost:8000/docs)
* **启动前端 (React + Vite)**：
  ```bash
  cd frontend
  npm run dev
  ```
  * 前端访问地址：[http://localhost:5173](http://localhost:5173)

---

## ⚙️ 模型配置说明 (DeepSeek)

系统支持两种模式无缝运行：
1. **真实 DeepSeek API 模式**：
   * 打开 `backend/.env`，填入你在 [DeepSeek 开放平台](https://platform.deepseek.com/) 申请的 API Key：
     ```ini
     DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```
   * 即可调用真实的 DeepSeek V3 (`deepseek-chat`) 或 R1 (`deepseek-reasoner`) 进行实时流式创作。
2. **拟真开发演示模式（无 Key 亦可畅玩）**：
   * 若未填写 API Key，系统会自动激活内置的高质量专业医学/书评流式演示引擎，完整模拟打字机 SSE 输出、3 组大纲对比与微信排版，便于随时自测与向家人展示！

---

## 📚 产研过程归档文档

* 📋 [产品需求规格说明书 (PRD v1.1.0)](file:///C:/Users/HUAWEI/.gemini/antigravity/brain/245f0a3b-f9eb-4f51-bef7-2717bc949fce/PRD_Wechat_Writing_Studio.md)
* 📐 [系统架构与接口契约规范 (Tech Spec v1.0)](file:///C:/Users/HUAWEI/.gemini/antigravity/brain/245f0a3b-f9eb-4f51-bef7-2717bc949fce/SYSTEM_DESIGN_AND_API_SPEC.md)
* 🧪 **自动化回归测试集**：
  * `backend/tests/test_api.py`（元数据与提示词端点覆盖测试）
  * `backend/tests/test_creation_flow.py`（端到端大纲生成、长文流式、合规免责及草稿持久化完整闭环测试）
