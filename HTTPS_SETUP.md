# HTTPS 配置说明

## 问题解决

✅ **已解决**：通过 IP 地址访问时麦克风录音功能异常的问题

## 解决方案

为 Vite 开发服务器配置了 HTTPS 支持，使浏览器能够正常访问麦克风权限。

## 配置内容

### 1. 生成自签名 SSL 证书

已在 `frontend/ssl/` 目录下生成：
- `server.crt` - SSL 证书
- `server.key` - SSL 私钥

### 2. 更新 Vite 配置

修改了 `frontend/vite.config.js`，启用 HTTPS：

```javascript
server: {
  host: '0.0.0.0',
  port: 30002,
  https: {
    key: fs.readFileSync(path.resolve(__dirname, 'ssl/server.key')),
    cert: fs.readFileSync(path.resolve(__dirname, 'ssl/server.crt'))
  },
  allowedHosts: [
    '.lan',
    '.local',
    '.localnet'
  ]
}
```

## 使用方法

### 启动服务器

```bash
cd frontend
npm run dev
```

### 访问应用

现在可以通过以下方式访问：

1. **HTTPS + IP 地址**（推荐）：
   ```
   https://你的IP地址:30002
   例如：https://192.168.1.100:30002
   ```

2. **HTTPS + localhost**：
   ```
   https://localhost:30002
   ```

3. **HTTP + localhost**（仍然有效）：
   ```
   http://localhost:30002
   ```

## 浏览器安全提示

由于使用的是自签名证书，浏览器会显示安全警告：

### Chrome/Edge
1. 点击"高级"或"详细信息"
2. 点击"继续访问 192.168.x.x（不安全）"
3. 或点击"不安全"图标 → "证书无效" → "仍然继续"

### Firefox
1. 点击"高级"按钮
2. 点击"接受风险并继续"

### Safari
1. 点击"显示详情"
2. 点击"访问此网站"

⚠️ **安全说明**：自签名证书仅适用于开发环境，生产环境需要使用 CA 颁发的有效证书。

## 验证麦克风功能

访问 `https://你的IP:30002` 后：

1. 进入任意字母学习页面
2. 点击"发音"按钮进入录音页面
3. 浏览器会弹出麦克风权限请求
4. 点击"允许"
5. 现在可以通过按住按钮录音了！

## 测试步骤

### 1. 启动前端服务器
```bash
cd frontend
npm run dev
```

### 2. 查看启动信息
控制台应显示：
```
  ➜  Local:   https://localhost:30002/
  ➜  Network: https://你的IP:30002/
```

### 3. 测试录音功能
1. 在手机或其他设备上访问：`https://你的IP:30002`
2. 登录账户
3. 选择任意字母 → 点击"发音"
4. 尝试录音功能

## API 请求修复

✅ **已解决**：前端HTTPS页面发送HTTP请求导致"混合内容"错误

### 问题描述
使用HTTPS证书后，前端运行在HTTPS，但API请求仍然是HTTP，导致：
- 浏览器阻止混合内容请求
- 前端无法与后端通信
- 控制台出现CORS或网络错误

### 解决方案

**1. 前端API配置自动适配协议**
修改了 `frontend/src/api/http.js`，现在会根据当前页面协议自动选择：

```javascript
const protocol = window.location.protocol === 'https:' ? 'https' : 'http'
const http = axios.create({
  baseURL: `${protocol}://${window.location.hostname}:20000`,
  // ...
})
```

**2. 后端HTTPS支持**
- 添加了SSL证书配置支持（`backend/app/config.py`）
- 更新了启动脚本（`backend/start.sh`）
- 自动检测frontend/ssl/目录下的证书并启用HTTPS

### 启动方式

**后端启动（自动检测HTTPS）**
```bash
cd backend
./start.sh
```

启动脚本会自动：
1. 检查 `../frontend/ssl/server.key` 和 `../frontend/ssl/server.crt`
2. 如果存在，使用HTTPS启动后端
3. 否则，使用HTTP启动后端

**前端启动**
```bash
cd frontend
npm run dev
```

### 验证HTTPS连接

1. 访问前端：`https://你的IP:30002`
2. 打开浏览器开发者工具 → Network选项卡
3. 点击任意字母，检查API请求：
   - ✅ 正确：显示协议为 `https://你的IP:20000/api/...`
   - ❌ 错误：显示协议为 `http://你的IP:20000/api/...`

## 故障排除

### 问题1：API请求仍为HTTP

**检查步骤**：
1. 确认后端使用HTTPS启动：
   ```
   检测到SSL证书，启动HTTPS服务器...
   ```
2. 清除浏览器缓存和localStorage
3. 刷新页面并重新登录

**解决方法**：
```bash
# 重新启动后端
cd backend
./start.sh

# 清除浏览器存储
# 开发者工具 → Application/应用 → Storage → Clear Storage
```

### 问题2：端口被占用

**错误**：Error: listen EADDRINUSE: address already in use :::30002

**解决**：
```bash
# 查找占用进程
lsof -i :30002

# 杀死进程（替换 PID）
kill -9 <PID>

# 或直接重启
npm run dev
```

### 问题2：自签名证书警告

**现象**：浏览器显示"不安全"或证书错误

**解决**：
- 这是正常的，点击"继续访问"即可
- 为避免此警告，可以将证书导入系统信任列表：
  - **Windows**: 双击 `server.crt` → 安装到"受信任的根证书颁发机构"
  - **macOS**: 双击 `server.crt` → 钥匙串访问 → 始终信任
  - **Linux**: 复制到 `/usr/local/share/ca-certificates/`，然后运行 `sudo update-ca-certificates`

### 问题3：仍无法录音

**解决步骤**：
1. 确认使用 `https://` 协议（不是 `http://`）
2. 检查浏览器控制台是否有错误
3. 访问诊断页面：`https://你的IP:30002/diagnostic.html`
4. 确认浏览器支持 `navigator.mediaDevices.getUserMedia`
5. 在浏览器设置中允许麦克风权限

### 问题4：局域网其他设备无法访问

**检查**：
1. 确认防火墙允许 30002 端口
2. 确认设备在同一局域网
3. 确认 Vite 配置中的 `allowedHosts` 包含你的域名后缀

## 技术细节

### HTTPS vs HTTP

| 协议 | localhost | IP地址 | 麦克风权限 |
|------|-----------|--------|-----------|
| HTTP | ✅ | ❌ | ❌ |
| HTTPS | ✅ | ✅ | ✅ |

### 浏览器安全策略

现代浏览器要求：
- **安全上下文**（HTTPS 或 localhost）
- **用户手势**（用户主动操作）
- **权限声明**（明确的权限请求）

### 为什么 localhost 例外？

`localhost` 被浏览器视为安全上下文，因为：
1. 不会暴露到公网
2. 域名解析到本地回环地址
3. 无法被外部网络访问

## 生产环境建议

### 使用有效 SSL 证书

1. **Let's Encrypt（免费）**：
   ```bash
   certbot --nginx -d yourdomain.com
   ```

2. **云服务商证书**：
   - 阿里云、腾讯云等都提供免费 SSL 证书

3. **反向代理**：
   ```nginx
   server {
       listen 443 ssl;
       server_name yourdomain.com;

       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       location / {
           proxy_pass http://localhost:30002;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### 完整部署架构

```
[用户] → [HTTPS] → [Nginx 反向代理] → [Vite Dev Server]
                     ↓
                [FastAPI Backend]
                     ↓
               [PostgreSQL]
```

## 相关文件

- `frontend/vite.config.js` - Vite HTTPS 配置
- `frontend/ssl/server.crt` - SSL 证书
- `frontend/ssl/server.key` - SSL 私钥
- `frontend/src/views/Record.vue` - 录音组件
- `frontend/public/diagnostic.html` - 诊断页面

## 参考资源

- [Vite HTTPS 配置](https://vitejs.dev/config/server-options.html#server-https)
- [MDN - getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- [Chrome - Secure Contexts](https://developer.chrome.com/blog/secure-contexts/)
- [Let's Encrypt](https://letsencrypt.org/)

## 完成 ✅

麦克风权限问题已解决！现在可以通过 IP 地址 + HTTPS 访问应用，录音功能将正常工作。