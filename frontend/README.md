# 前端部署说明

## 本地开发

\`\`\`bash
npm install
npm run dev
\`\`\`

前端会在 `http://localhost:5173` 启动，并通过 Vite 代理连接到 `http://127.0.0.1:8000` 的后端。

## Render 部署（生产环境）

### 重要提示

Render 的 Static Site **不支持运行时环境变量**，必须在构建时将后端 API 地址编译进代码。

### 部署配置

在 Render Dashboard 中创建 Static Site 时，使用以下配置：

- **Name**: `wechat-frontend`
- **Branch**: `master` 或 `main`
- **Root Directory**: `frontend`
- **Build Command**（**关键**）:
  \`\`\`bash
  npm install && VITE_API_BASE_URL=https://你的后端服务名.onrender.com npm run build
  \`\`\`
  **必须将 URL 替换为你的后端实际域名**

- **Publish Directory**: `dist`

### 更新部署

如果需要更改后端 URL：

1. 前往 Render Dashboard → 前端服务 → Settings
2. 找到 **Build Command**
3. 修改 `VITE_API_BASE_URL` 的值
4. 点击 **Save Changes**
5. 点击 **Manual Deploy** → **Clear build cache & deploy**

### 验证部署

部署成功后：

1. 打开前端 URL
2. 按 F12 打开开发者工具
3. 查看 Network 标签，应该能看到对后端 `/api/v1/...` 的请求
4. 确认状态码为 200（成功）

### 常见问题

**问题**：前端显示空白或 API 请求 404

**解决**：检查构建命令中的 `VITE_API_BASE_URL` 是否正确，必须包含完整的后端域名（包括 `https://`）

**问题**：CORS 错误

**解决**：检查后端环境变量 `FRONTEND_URL` 是否与前端实际域名一致
