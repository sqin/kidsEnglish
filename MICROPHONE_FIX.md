# 麦克风权限问题修复说明

## 问题描述

录音页面无法正常获取麦克风权限，即使授权后依旧提示授权，无法录音。

**错误信息**: `录音失败: Cannot read properties of undefined (reading 'getUserMedia')`

## 根本原因

1. **浏览器兼容性不足**: 没有检查 `navigator.mediaDevices` 是否存在
2. **重复请求权限**: 每次录音都调用 `getUserMedia()`，导致浏览器不断弹出授权对话框
3. **缺少权限状态管理**: 没有检查和缓存权限状态
4. **权限被拒绝后无重试机制**: 用户拒绝后无法重新授权
5. **资源泄漏**: 音频流和MediaRecorder没有正确清理
6. **API降级处理缺失**: 未考虑旧版浏览器的 `getUserMedia` API

## 修复方案

### 1. 增强的浏览器兼容性检查

```javascript
const checkMicrophonePermission = async () => {
  // 检查 navigator 对象
  if (!navigator) {
    throw new Error('浏览器不支持')
  }

  // 检查 navigator.mediaDevices
  if (!navigator.mediaDevices) {
    // 尝试使用旧版 API
    if (navigator.getUserMedia) {
      const stream = await new Promise((resolve, reject) => {
        navigator.getUserMedia(
          { audio: true },
          (stream) => {
            stream.getTracks().forEach(track => track.stop())
            resolve(stream)
          },
          (error) => reject(error)
        )
      })
      hasPermission.value = true
      return true
    } else {
      throw new Error('您的浏览器不支持录音功能')
    }
  }

  // 检查 getUserMedia 方法
  if (typeof navigator.mediaDevices.getUserMedia !== 'function') {
    throw new Error('getUserMedia 方法不可用')
  }

  // ... 权限检查逻辑
}
```

### 2. 改进的录音流程（支持API降级）

```javascript
const startRecording = async () => {
  let stream

  // 尝试使用现代API
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { ... } })
    } catch (err) {
      // 如果现代API失败，尝试旧版API
      if (navigator.getUserMedia) {
        stream = await new Promise((resolve, reject) => {
          navigator.getUserMedia(
            { audio: true },
            (stream) => resolve(stream),
            (error) => reject(error)
          )
        })
      } else {
        throw err
      }
    }
  } else if (navigator.getUserMedia) {
    // 直接使用旧版API
    stream = await new Promise((resolve, reject) => {
      navigator.getUserMedia(
        { audio: true },
        (stream) => resolve(stream),
        (error) => reject(error)
      )
    })
  } else {
    throw new Error('您的浏览器不支持录音功能')
  }

  // 创建 MediaRecorder
  let mimeType = 'audio/webm;codecs=opus'
  if (!MediaRecorder.isTypeSupported(mimeType)) {
    // 降级到其他格式
    if (MediaRecorder.isTypeSupported('audio/webm')) {
      mimeType = 'audio/webm'
    } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
      mimeType = 'audio/mp4'
    } else {
      mimeType = '' // 让浏览器自动选择
    }
  }

  mediaRecorder = new MediaRecorder(mediaStream, { mimeType })
  // ... 录音逻辑
}
```

### 3. 浏览器不支持的UI提示

```vue
<!-- 浏览器不支持提示 -->
<div class="permission-prompt" v-if="!navigator.mediaDevices && !navigator.getUserMedia && !loading">
  <div class="prompt-content">
    <span class="prompt-icon">🌐</span>
    <h3>浏览器不支持</h3>
    <p>您的浏览器不支持录音功能</p>
    <p class="browser-list">
      请使用以下浏览器：
      <br>
      • Chrome 14+<br>
      • Firefox 29+<br>
      • Safari 14.1+<br>
      • Edge 79+
    </p>
  </div>
</div>
```

### 4. 添加权限状态管理

```javascript
const hasPermission = ref(false)        // 是否有权限
const permissionDenied = ref(false)     // 权限是否被拒绝
const permissionRequested = ref(false)  // 是否已请求过权限
```

### 2. 初始化时检查权限

组件挂载时自动检查麦克风权限：

```javascript
onMounted(async () => {
  await checkMicrophonePermission()
})
```

### 3. 改进的权限检查函数

```javascript
const checkMicrophonePermission = async () => {
  try {
    // 检查浏览器支持
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('您的浏览器不支持录音功能')
    }

    // 检查麦克风设备
    const devices = await navigator.mediaDevices.enumerateDevices()
    const audioDevices = devices.filter(device => device.kind === 'audioinput')

    if (audioDevices.length === 0) {
      throw new Error('未检测到麦克风设备')
    }

    // 验证权限但不录音
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,    // 回声消除
        noiseSuppression: true,    // 降噪
        autoGainControl: true      // 自动增益
      }
    })
    stream.getTracks().forEach(track => track.stop())

    hasPermission.value = true
    permissionDenied.value = false
    return true
  } catch (err) {
    hasPermission.value = false
    if (err.name === 'NotAllowedError') {
      permissionDenied.value = true
    }
    return false
  }
}
```

### 4. 改进的录音流程

```javascript
const startRecording = async () => {
  // 首次录音前请求权限
  if (!hasPermission.value && !permissionRequested.value) {
    const granted = await requestMicrophonePermission()
    if (!granted) return
  }

  // 权限被拒绝时显示提示
  if (permissionDenied.value) {
    alert('请允许访问麦克风，然后刷新页面重试')
    return
  }

  // 获取音频流并录音
  mediaStream = await navigator.mediaDevices.getUserMedia({ audio: { ... } })
  mediaRecorder = new MediaRecorder(mediaStream, { mimeType: 'audio/webm;codecs=opus' })
  // ... 录音逻辑
}
```

### 5. 权限被拒绝的UI提示

添加了专门的权限提示页面：

```vue
<div class="permission-prompt" v-if="permissionDenied && !loading">
  <div class="prompt-content">
    <span class="prompt-icon">🔒</span>
    <h3>需要麦克风权限</h3>
    <p>请允许访问麦克风以进行语音评分</p>
    <button class="retry-permission-btn" @click="requestMicrophonePermission">
      重新授权
    </button>
  </div>
</div>
```

### 6. 资源清理

组件卸载时自动清理所有音频资源：

```javascript
onBeforeUnmount(() => {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
  }
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop()
  }
  if (audioContext && audioContext.state !== 'closed') {
    audioContext.close()
  }
})
```

## 关键改进点

### ✅ 解决了重复授权问题
- 权限只在首次需要时请求一次
- 状态缓存，避免重复请求

### ✅ 更好的错误处理
- 区分不同错误类型（无设备、权限被拒绝、不支持等）
- 提供针对性的错误提示

### ✅ 优雅的权限管理
- 组件加载时自动检查权限
- 权限被拒绝时有清晰的重试UI
- 支持重新授权

### ✅ 资源管理优化
- 音频流正确释放
- MediaRecorder状态检查
- 组件卸载时自动清理

### ✅ 音频质量优化
- 启用回声消除
- 启用噪声抑制
- 启用自动增益控制
- 使用WebM格式减少文件大小

## 使用说明

### 首次访问
1. 进入录音页面时自动检查麦克风权限
2. 浏览器弹出授权对话框
3. 点击"允许"即可正常使用

### 权限被拒绝
1. 页面显示权限提示
2. 点击"重新授权"按钮
3. 或手动在浏览器设置中允许网站麦克风权限

### 浏览器设置（如果需要手动操作）
- **Chrome**: 地址栏左侧 → 锁定图标 → 麦克风 → 允许
- **Firefox**: 地址栏左侧 → 摄像头图标 → 权限设置
- **Safari**: 偏好设置 → 网站 → 麦克风 → 允许

## 技术细节

### 权限状态
- `hasPermission`: true/false - 是否已获得权限
- `permissionDenied`: true/false - 权限是否被拒绝
- `permissionRequested`: true/false - 是否已请求过权限

### 错误类型处理
- `NotAllowedError`: 权限被拒绝
- `NotFoundError`: 未找到麦克风设备
- `NotSupportedError`: 浏览器不支持
- `TypeError`: 其他错误

### 音频格式
- 使用 `audio/webm;codecs=opus` 格式
- 兼容性好的现代格式
- 文件小，音质高

## 测试验证

1. **正常流程测试**
   - 进入录音页面 → 授权 → 正常录音 → 获得评分

2. **拒绝权限测试**
   - 进入录音页面 → 拒绝授权 → 显示重试提示 → 重新授权成功

3. **设备检测测试**
   - 无麦克风设备时显示相应错误提示

4. **资源清理测试**
   - 多次录音 → 检查浏览器是否泄漏资源（Task Manager）

## 浏览器支持矩阵

| 浏览器 | 最低版本 | 状态 | 备注 |
|--------|----------|------|------|
| Chrome | 14+ | ✅ 完全支持 | 最佳体验 |
| Firefox | 29+ | ✅ 完全支持 | |
| Safari | 14.1+ | ✅ 支持 | 需要用户交互 |
| Edge | 79+ | ✅ 完全支持 | |
| IE | ❌ 不支持 | 不支持 | 需要升级浏览器 |
| 旧版移动浏览器 | ❌ 可能不支持 | 部分支持 | 取决于版本 |

## 诊断工具

创建了诊断页面帮助排查问题：

**访问**: `http://localhost:30002/diagnostic.html`

诊断页面会检查：
- ✅ navigator 对象存在性
- ✅ HTTPS 连接（录音需要安全上下文）
- ✅ navigator.mediaDevices 支持
- ✅ navigator.getUserMedia 支持（兼容旧版）
- ✅ MediaRecorder API 支持
- ✅ 音频设备检测
- ✅ 实际录音测试

## 文件修改

- **修改文件**: `/frontend/src/views/Record.vue`
- **修改行数**: ~200行
- **新增文件**: `/frontend/public/diagnostic.html` (诊断工具)
- **主要变更**:
  - 添加增强的浏览器兼容性检查
  - 支持旧版 `getUserMedia` API 降级
  - 添加权限状态变量
  - 新增权限检查函数
  - 改进录音流程
  - 添加浏览器不支持UI
  - 添加权限被拒绝UI
  - 完善资源清理
  - 修复import位置语法错误
  - 音频格式自动降级

## 部署说明

修改后的代码无需额外配置，重新启动前端即可：

```bash
cd frontend
npm run dev
```

麦克风权限功能现在应该可以正常工作了！

## 故障排除

### 1. 仍然出现 "Cannot read properties of undefined"

**解决方案**:
- 确保使用现代浏览器（Chrome 90+, Firefox 88+, Safari 14+）
- 检查浏览器是否允许访问 `navigator.mediaDevices`
- 访问诊断页面检查支持情况

### 2. 权限被拒绝但没有提示

**解决方案**:
- 检查 `permissionDenied` 状态是否正确设置
- 查看浏览器控制台是否有错误日志
- 尝试使用诊断工具

### 3. 录音无声音

**解决方案**:
- 检查麦克风设备是否正确连接
- 在浏览器设置中允许麦克风权限
- 测试其他录音应用确认设备正常

### 4. 部分浏览器录制失败

**解决方案**:
- 代码已自动降级音频格式（WebM → MP4 → 自动）
- 旧版浏览器可能不支持 MediaRecorder，可使用诊断工具确认

## 测试清单

- [ ] 在 Chrome 中测试录音
- [ ] 在 Firefox 中测试录音
- [ ] 在 Safari 中测试录音
- [ ] 拒绝权限后重新授权
- [ ] 无麦克风设备的错误处理
- [ ] HTTP vs HTTPS 环境测试
- [ ] 移动端浏览器测试（iOS Safari, Android Chrome）
