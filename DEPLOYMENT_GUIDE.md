# 文思 · 微信公众号创作工作台 生产环境部署与域名上线指南

> 适用场景：异地家庭共享使用（如母亲在异地手机端访问）、团队协作及未来商业化上线。

---

## 目录
1. [服务器与域名选型建议（国内 vs 香港免备案）](#1-服务器与域名选型建议)
2. [方案 A：今天立即可用·零成本临时公网隧道（Cloudflare Tunnel）](#2-方案-a今天立即可用零成本临时公网隧道)
3. [方案 B：标准企业级云服务器 + 独立域名部署（推荐长期使用）](#3-方案-b标准企业级云服务器--独立域名部署)
4. [Nginx 与 SSE 流式打字机传输关键优化](#4-nginx-与-sse-流式优化)
5. [数据持久化与安全管理](#5-数据持久化与安全管理)

---

## 1. 服务器与域名选型建议

在上线生产环境前，需明确国内对于域名的法规要求：

| 对比维度 | 境内大陆节点（北上广深等） | 中国香港 / 亚太海外轻量服务器 |
| :--- | :--- | :--- |
| **工信部 ICP 备案** | **强制必须备案**（耗时 3~15 个工作日，需身份证核验） | **完全免备案**（域名购买后解析秒级生效） |
| **异地访问速度** | 本地极速（5~15ms） | BGP 直连优化极速（20~40ms，体验无差异） |
| **成本推荐** | 腾讯云/阿里云国内轻量（约 60~99元/年） | 腾讯云轻量香港 / 阿里云香港（约 24~34元/月） |
| **上线推荐度** | 适合已有备案企业/个人 | **强烈推荐（个人跨地自用/免等待首选）** |

### 域名选购建议
- **注册商**：腾讯云 DNSPod、阿里云万网，或 Cloudflare。
- **后缀推荐**：
  - 正式商业感：`.com`、`.cn`（首年约 30~65 元）；
  - 高性价比：`.xyz`、`.top`、`.site`（首年约 8~18 元）。

---

## 2. 方案 A：今天立即可用·零成本临时公网隧道

如果今天尚未购买服务器，但希望**今天马上让异地的母亲在手机上打开体验**：

1. **下载 Cloudflare Tunnel 官方 CLI (`cloudflared`)**：
   - 官网免安装单文件，运行：
     ```bash
     cloudflared tunnel --url http://localhost:5173
     ```
2. **获取专属 HTTPS 链接**：
   - 终端会立即输出一个全球可达的加密链接（如 `https://random-word-abc.trycloudflare.com`）。
   - 将此链接直接通过微信发送给母亲，手机浏览器打开即可全功能使用（含中医模板、AI 扩写与一键复制）。
   - **特点**：0 成本、免买服务器、免备案、自带 HTTPS 安全小绿锁。

---

## 3. 方案 B：标准企业级云服务器 + 独立域名部署

当租用好 Linux 服务器（推荐 Ubuntu 22.04 LTS 或 Debian 12）并买好域名后：

### 第一步：服务器环境准备
在服务器终端运行：
```bash
# 安装 Docker 与 Docker Compose
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker
```

### 第二步：上传代码与配置环境变量
```bash
# 将项目上传至服务器 /opt/wechat-writing-studio
cd /opt/wechat-writing-studio

# 复制生产环境变量
cp .env.production.example .env

# 编辑 .env 文件填入你的 DeepSeek API Key
nano .env
```

### 第三步：一键构建并启动服务
```bash
# 启动前端与后端容器
docker compose up -d --build

# 查看运行状态
docker compose ps
```
此时通过服务器 IP（如 `http://<服务器公网IP>`）即可访问系统。

### 第四步：域名解析与免费 SSL 证书（HTTPS）
1. 在域名管理后台添加一条 `A 记录`：
   - 主机记录：`@` 或 `studio`
   - 记录值：你的服务器公网 IP
2. 在服务器上使用 Certbot 自动化申请免费 Let's Encrypt 证书：
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```
   Certbot 会自动配置 HTTPS 并设置 90 天自动续期。

---

## 4. Nginx 与 SSE 流式优化

本项目核心功能包含 **大纲流式生成** 与 **正文打字机实时输出**（基于 Server-Sent Events, SSE）。
项目自带的 [`frontend/nginx.conf`](file:///E:/SchoolFiles/idea/wechat-writing-studio/frontend/nginx.conf) 已预置生产级流式反向代理规则：

```nginx
location /api/ {
    proxy_pass http://backend:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    
    # 关键：彻底关闭缓冲，保障 SSE 打字机流式平滑传输
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header X-Accel-Buffering no;
    proxy_read_timeout 300s;
}
```

---

## 5. 数据持久化与安全管理

1. **数据库安全**：
   - 本地 SQLite 数据库挂载在 Docker Volume `wechat_studio_data` 中，即使容器更新重启，历史文章与 Prompt 资产绝不丢失。
2. **API Key 安全隔离**：
   - 生产环境中，`DEEPSEEK_API_KEY` 存放在服务器宿主机的 `.env` 中，前端代码构建为静态文件时不包含任何密钥，彻底防止客户端源码泄露。
