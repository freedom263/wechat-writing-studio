# 免费云平台部署指南 - 微信公众号AI写作工具

> **注意**：Railway 目前需要邀请码才能注册新账号。本指南推荐使用 **Render** 或 **Zeabur** 作为替代方案。

## 🎯 推荐平台对比

| 平台 | 免费额度 | 优势 | 劣势 |
|------|---------|------|------|
| **Render** | 750 小时/月 | 无需邀请码，稳定可靠 | 冷启动较慢（闲置后需 30s 唤醒） |
| **Zeabur** | $5/月免费额度 | 中文界面，国内访问快 | 额度较少 |
| **Vercel** | 100GB 流量/月 | 前端部署极快 | 仅适合前端，后端需配合其他平台 |

**本指南以 Render 为主**，操作简单且完全免费。

---

## 📦 前置准备

1. **注册 Render 账号**
   - 访问 https://render.com
   - 使用 GitHub 账号登录（推荐）
   - 无需邀请码，直接可用

2. **准备 GitHub 仓库**
   - 将代码推送到 GitHub
   - 确保仓库包含所有配置文件

3. **获取 DeepSeek API Key**（可选，不配置则使用演示模式）
   - 访问 https://platform.deepseek.com
   - 获取 API Key

---

## 🚀 部署步骤（使用 Render）

### 第一步：创建 PostgreSQL 数据库

1. 登录 Render Dashboard：https://dashboard.render.com

2. 点击 **New +** → **PostgreSQL**

3. 配置数据库：
   - **Name**: `wechat-writing-db`
   - **Database**: `wechat_db`
   - **User**: `wechat_user`（自动生成）
   - **Region**: 选择 **Singapore**（距离中国最近）
   - **PostgreSQL Version**: 选择最新版本
   - **Plan**: 选择 **Free**

4. 点击 **Create Database**

5. 创建后，进入数据库详情页，复制 **Internal Database URL**（以 `postgresql://` 开头）

### 第二步：部署后端服务

1. 回到 Render Dashboard，点击 **New +** → **Web Service**

2. 连接 GitHub 仓库：
   - 点击 **Connect account** 授权 GitHub
   - 选择 `wechat-writing-studio` 仓库
   
   echo "# wechat-writing-studio" >> README.md
   git init
   git add README.md
   git commit -m "first commit"
   git branch -M main
   git remote add origin https://github.com/freedom263/wechat-writing-studio.git
   git push -u origin main

配置后端服务：
- **Name**: `wechat-backend`
- **Region**: **Singapore**
- **Branch**: `main` 或 `master`
- **Root Directory**: `backend`
- **Runtime**: **Python 3**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Plan**: 选择 **Free**

1. 点击 **Advanced**，添加环境变量：

```bash
DATABASE_URL=<粘贴第一步复制的 Internal Database URL>
DEEPSEEK_API_KEY=<你的 DeepSeek API Key>
DEEPSEEK_BASE_URL=https://api.deepseek.com
FRONTEND_URL=https://wechat-frontend-h64p.onrender.com
```

**注意**：`FRONTEND_URL` 先用占位符，第三步部署前端后再回来更新

5. 点击 **Create Web Service**
6. 等待 5-10 分钟构建部署
7. 部署成功后，Render 会分配域名，你的后端地址：
   - https://wechat-backend-49g7.onrender.com

### 第三步：部署前端服务

1. 回到 Render Dashboard，点击 **New +** → **Static Site**
2. 选择同一个 GitHub 仓库 `wechat-writing-studio`
3. 配置前端服务：
   - **Name**: `wechat-frontend`
   - **Branch**: `main` 或 `master`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && VITE_API_BASE_URL=https://wechat-backend-49g7.onrender.com npm run build`
   - **Publish Directory**: `dist`
4. **重要**：Render 的 Static Site 不支持运行时环境变量，必须在构建命令中内联设置。将上面 Build Command 中的 URL 替换为第二步中后端服务的实际域名。

5. 点击 **Create Static Site**
6. 等待构建完成，访问你的前端域名：
   - https://wechat-frontend-h64p.onrender.com

### 第四步：更新后端环境变量

1. 返回后端服务页面
2. 进入 **Environment** 标签
3. 更新 `FRONTEND_URL` 为前端实际域名：
   ```
   FRONTEND_URL=https://wechat-frontend-h64p.onrender.com
   ```
4. 点击 **Save Changes**，后端会自动重新部署（约 2-3 分钟）

---

## ✅ 验证部署

### 1. 检查后端健康状态
访问：https://wechat-backend-49g7.onrender.com/

应该返回：
```json
{
  "status": "online",
  "service": "文思·微信公众号创作工作台",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### 2. 检查 API 文档
访问：https://wechat-backend-49g7.onrender.com/docs

应该能看到完整的 API 文档页面

### 3. 检查前端应用
访问：https://wechat-frontend-h64p.onrender.com/

应该能正常打开应用界面

### 4. 测试创作流程
1. 选择赛道和模板
2. 输入创作主题
3. 生成大纲候选方案
4. 选择方案生成全文
5. 编辑并导出内容

---

## 🔧 常见问题排查

### 问题 1：前端无法连接后端（CORS 错误）

**症状**：浏览器控制台显示 CORS 错误

**解决方案**：
1. 检查后端环境变量 `FRONTEND_URL` 是否正确配置
2. 确认后端已重新部署（修改环境变量后自动触发）
3. 清除浏览器缓存并刷新

### 问题 2：数据库连接失败

**症状**：后端日志显示数据库连接错误

**解决方案**：
1. 确认 PostgreSQL 服务正常运行（Render Dashboard → PostgreSQL → Status）
2. 检查后端环境变量 `DATABASE_URL` 是否正确
3. 在 Render Dashboard 中，进入后端服务 → **Environment**
4. 确认 `DATABASE_URL` 使用的是 **Internal Database URL**

### 问题 3：部署失败（构建错误）

**症状**：Render 显示构建失败

**解决方案**：
1. 查看详细日志：服务页面 → **Logs** 标签
2. 常见原因：
   - Python 依赖安装失败 → 检查 `requirements.txt`
   - Node 依赖安装失败 → 检查 `package.json`
   - 构建超时 → 免费计划有 15 分钟构建时限
3. 修复代码后推送到 GitHub，Render 会自动重新部署

### 问题 4：DeepSeek API 调用失败

**症状**：生成内容时报错

**解决方案**：
1. 确认 `DEEPSEEK_API_KEY` 环境变量已正确配置
2. 检查 API Key 是否有效（登录 DeepSeek 平台查看）
3. 如果没有 API Key，系统会自动使用演示模式

### 问题 5：前端 API 请求 404

**症状**：前端报告 API 请求 404 错误

**解决方案**：
1. 确认前端环境变量 `VITE_API_BASE_URL` 配置正确
2. 确认后端域名可访问（访问 `/docs` 检查）
3. 在 Render Dashboard → 前端服务 → **Environment** → 修改后点击 **Save Changes**
4. Render 会自动触发重新构建

### 问题 6：后端服务冷启动慢

**症状**：首次访问等待 30-60 秒

**解决方案**：
这是 Render 免费计划的正常现象（闲置 15 分钟后休眠）
1. **接受现状**：个人项目可以接受
2. **定时 ping**：使用 UptimeRobot 每 5 分钟访问一次后端（https://uptimerobot.com 免费）
3. **升级付费**：$7/月 Starter 计划无休眠限制

---

## 💰 成本管理

### 免费额度（Render）
- **后端服务**：750 小时/月（约 31 天，完全够用）
- **PostgreSQL**：1GB 存储空间，90 天后自动删除（需定期备份）
- **前端静态站**：100GB 流量/月
- **限制**：
  - 闲置 15 分钟后自动休眠
  - 唤醒需要 30-60 秒（首次访问会慢）

### 预估使用量
- **后端服务**：自动休眠机制，实际使用 < 500 小时/月
- **前端服务**：静态托管，无休眠问题
- **数据库**：小规模使用 < 100MB

**结论**：个人使用或小团队完全免费，唯一缺点是冷启动较慢

### 成本优化建议
1. **避免频繁休眠唤醒**
   - 使用 UptimeRobot 每 5 分钟 ping 一次后端（保持活跃）
   - 免费方案：https://uptimerobot.com

2. **数据库备份**
   - Render 免费数据库 90 天后删除
   - 每周导出一次备份：
   ```bash
   # 在 Render Dashboard → PostgreSQL → Connect
   # 复制 External Database URL，然后本地运行：
   pg_dump <External_Database_URL> > backup.sql
   ```

3. **升级到付费计划**（如果需要）
   - **Starter**: $7/月，去除休眠限制
   - **Standard**: $25/月，更多资源和优先支持

---

## 🔄 更新部署

### 自动部署（推荐）
1. 修改代码
2. 提交到 GitHub：
   ```bash
   git add .
   git commit -m "更新功能"
   git push origin main
   ```
3. Render 会自动检测推送并重新部署
4. 等待 5-10 分钟构建完成（可在 Logs 中查看进度）

### 手动触发部署
1. Render Dashboard → 选择服务
2. 点击右上角 **Manual Deploy** → **Deploy latest commit**
3. 或者选择 **Clear build cache & deploy**（构建缓存有问题时使用）

---

## 🔒 安全建议

### 1. 保护敏感信息
- ❌ 不要将 `.env` 文件提交到 Git
- ✅ 使用 Render 的环境变量功能
- ✅ 在 `.gitignore` 中排除 `.env*` 文件

### 2. API Key 管理
- 定期轮换 DeepSeek API Key
- 在 DeepSeek 平台设置使用限额

### 3. 监控日志
- 定期查看 Render 日志
- 关注异常错误和访问模式

---

## 📊 监控和维护

### 查看日志
1. Render Dashboard → 选择服务
2. 点击 **Logs** 标签
3. 实时查看应用日志和错误信息
4. 可以按日期范围过滤日志

### 查看指标
1. Render Dashboard → 选择服务
2. 点击 **Metrics** 标签
3. 查看 CPU、内存、请求量、响应时间

### 数据库备份
```bash
# 方法1：在 Render Dashboard 复制 External Database URL
# 方法2：使用以下命令导出（需要本地安装 PostgreSQL）
pg_dump <External_Database_URL> > backup_$(date +%Y%m%d).sql

# 恢复数据库
psql <External_Database_URL> < backup.sql
```

**重要**：Render 免费数据库会在 90 天后删除，建议每周备份一次

---

## 🎯 下一步优化

1. **自定义域名**
   - Render 支持绑定自定义域名
   - Settings → **Custom Domain** → 添加你的域名

2. **配置监控告警**
   - 集成 UptimeRobot 监控网站可用性
   - 配置邮件告警

3. **性能优化**
   - 启用 Redis 缓存（Render 支持）
   - 优化数据库查询

4. **功能扩展**
   - 添加用户认证系统
   - 集成更多 AI 模型

---

## 📞 获取帮助

- **Render 文档**：https://docs.render.com/
- **Render 社区**：https://community.render.com/
- **项目 Issues**：在 GitHub 仓库创建 Issue

---

## 📝 快速命令参考

```bash
# 安装 Render CLI（可选）
npm install -g render

# 查看服务日志（在 Dashboard 中查看更方便）
render logs <service-name>

# 本地连接数据库（需要 External Database URL）
psql <External_Database_URL>

# 导出数据库备份
pg_dump <External_Database_URL> > backup_$(date +%Y%m%d).sql

# 恢复数据库
psql <External_Database_URL> < backup.sql
```

---

## 🔄 其他平台选择

### 使用 Zeabur（中文友好）

如果你想要中文界面和更快的国内访问速度，可以选择 Zeabur：

1. 访问 https://zeabur.com
2. 使用 GitHub 登录
3. 部署流程类似 Render，但界面全中文
4. 免费额度：$5/月，约 100 小时运行时间
5. 优势：国内访问快，无需科学上网

### 使用 Vercel + Supabase

**适合只部署前端，后端本地运行的场景**：

1. **前端部署到 Vercel**（极快）
   - 访问 https://vercel.com
   - 连接 GitHub 仓库的 `frontend` 目录
   - 自动构建部署，CDN 加速

2. **数据库使用 Supabase**（PostgreSQL）
   - 访问 https://supabase.com
   - 创建项目，获取数据库连接字符串
   - 免费额度：500MB 数据库，50MB 文件存储

3. **后端部署到 Render 或本地运行**

---

**恭喜！🎉 你的微信公众号AI写作工具已成功部署到云端！**

现在可以分享你的前端域名给朋友试用了。
