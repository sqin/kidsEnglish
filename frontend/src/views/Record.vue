<template>
  <div class="record-page">
    <!-- 返回按钮 -->
    <button class="back-btn" @click="$router.back()">
      ← 返回
    </button>

    <!-- 字母展示 -->
    <div class="letter-preview">
      <span class="letter">{{ currentLetter.letter }}</span>
      <span class="word">{{ currentLetter.word }}</span>
    </div>

    <!-- 浏览器不支持提示 -->
    <div class="permission-prompt" v-if="browserNotSupported && !loading">
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
        <p class="help-text">
          建议使用最新版本的浏览器
        </p>
      </div>
    </div>

    <!-- 权限被拒绝提示 -->
    <div class="permission-prompt" v-else-if="permissionDenied && !loading">
      <div class="prompt-content">
        <span class="prompt-icon">🔒</span>
        <h3>需要麦克风权限</h3>
        <p>请允许访问麦克风以进行语音评分</p>
        <button class="retry-permission-btn" @click="requestMicrophonePermission">
          重新授权
        </button>
        <p class="help-text">
          如果问题持续，请检查浏览器设置中的网站权限
        </p>
      </div>
    </div>

    <!-- 录音区域 -->
    <div class="record-area" v-else-if="!browserNotSupported">
      <button
        class="record-button"
        :class="{ recording: isRecording, scored: hasScore, loading: loading }"
        :disabled="loading"
        @mousedown.prevent="handleRecordStart"
        @mouseup.prevent="handleRecordStop"
        @mouseleave.prevent="handleRecordStop"
        @touchstart.prevent="handleRecordStart"
        @touchend.prevent="handleRecordStop"
        @touchcancel.prevent="handleRecordStop"
      >
        <span class="record-icon" v-if="!isRecording && !hasScore && !loading">🎤</span>
        <span class="record-icon pulse" v-else-if="isRecording">🔴</span>
        <span class="record-icon" v-else-if="loading">⏳</span>
        <span class="record-icon" v-else>✅</span>
      </button>
      <p class="record-hint" v-if="!isRecording && !hasScore && !loading">
        按住按钮，大声读出字母 "{{ currentLetter.letter }}"
      </p>
      <p class="record-hint recording" v-else-if="isRecording">
        正在录音... 松开结束
      </p>
      <p class="record-hint" v-else-if="loading">
        正在评分...
      </p>
      <p class="permission-check" v-if="!hasPermission && !permissionDenied && !permissionRequested">
        正在检查麦克风权限...
      </p>
    </div>

    <!-- 评分结果 -->
    <div class="score-result" v-if="hasScore" ref="scoreRef">
      <div class="score-stars">
        <span
          v-for="i in 3"
          :key="i"
          class="star"
          :class="{ earned: i <= score }"
        >
          ⭐
        </span>
      </div>
      <p class="score-text">
        {{ scoreText }}
      </p>
      <div class="action-btns">
        <button class="retry-btn" @click="retry">再试一次</button>
        <button class="next-btn" @click="goNext" v-if="score >= 1">
          下一个 →
        </button>
      </div>
    </div>

    <!-- 撒花动画 -->
    <div class="confetti" v-if="showConfetti">
      <span v-for="i in 20" :key="i" class="confetti-piece">🎉</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLearningStore } from '../stores/learning'
import { speechAPI } from '../api/speech'
import { progressAPI } from '../api/progress'
import gsap from 'gsap'

const route = useRoute()
const router = useRouter()
const store = useLearningStore()

const isRecording = ref(false)
const hasScore = ref(false)
const score = ref(0)
const showConfetti = ref(false)
const scoreRef = ref(null)
const loading = ref(false)
const hasPermission = ref(false)
const permissionDenied = ref(false)
const permissionRequested = ref(false)
const browserNotSupported = ref(false)

let mediaRecorder = null
let audioChunks = []
let audioContext = null
let mediaStream = null
let recordingStartTime = null
const MIN_RECORDING_DURATION = 500 // 最小录音时长500毫秒

const currentLetter = computed(() => {
  const letter = route.params.letter.toUpperCase()
  return store.letters.find(l => l.letter === letter) || store.letters[0]
})

const scoreText = computed(() => {
  if (score.value === 3) return '太棒了！发音非常标准！🎉'
  if (score.value === 2) return '很好！继续加油！👍'
  if (score.value === 1) return '不错的开始，再练练！💪'
  return '再试一次吧！🔄'
})

// 检查浏览器支持
const checkBrowserSupport = () => {
  browserNotSupported.value = !navigator || (!navigator.mediaDevices && !navigator.getUserMedia)
}

// 检查麦克风权限
const checkMicrophonePermission = async () => {
  try {
    // 检查 navigator.mediaDevices
    if (!navigator.mediaDevices) {
      console.warn('navigator.mediaDevices 不存在，尝试旧版API')
      // 尝试使用旧版 API
      if (navigator.getUserMedia) {
        try {
          const stream = await new Promise((resolve, reject) => {
            navigator.getUserMedia(
              { audio: true },
              (stream) => {
                // 旧版API回调风格，立即停止
                stream.getTracks().forEach(track => track.stop())
                resolve(stream)
              },
              (error) => reject(error)
            )
          })
          hasPermission.value = true
          permissionDenied.value = false
          return true
        } catch (err) {
          if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            permissionDenied.value = true
          }
          hasPermission.value = false
          return false
        }
      } else {
        // 真的没有录音API
        console.error('浏览器不支持录音功能')
        hasPermission.value = false
        return false
      }
    }

    // 检查 getUserMedia 方法
    if (typeof navigator.mediaDevices.getUserMedia !== 'function') {
      console.error('getUserMedia 方法不可用')
      hasPermission.value = false
      return false
    }

    // 检查权限状态
    const devices = await navigator.mediaDevices.enumerateDevices()
    const audioDevices = devices.filter(device => device.kind === 'audioinput')

    if (audioDevices.length === 0) {
      console.warn('未检测到麦克风设备，但可能存在权限问题')
      // 不抛出错误，继续尝试获取权限
    }

    // 尝试获取权限但不录音
    const constraints = {
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    }

    // 尝试获取流
    let stream
    try {
      stream = await navigator.mediaDevices.getUserMedia(constraints)
    } catch (getUserMediaErr) {
      console.error('getUserMedia 失败:', getUserMediaErr)
      throw getUserMediaErr
    }

    // 立即停止流，只为验证权限
    stream.getTracks().forEach(track => track.stop())

    hasPermission.value = true
    permissionDenied.value = false
    return true
  } catch (err) {
    console.error('麦克风权限检查失败:', err)
    hasPermission.value = false

    // 只处理权限相关错误，不设置 browserNotSupported
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      permissionDenied.value = true
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      // 设备未找到，不设置 permissionDenied
      permissionDenied.value = false
    } else if (err.name === 'NotSupportedError') {
      permissionDenied.value = false
    }
    // 注意：不要在 catch 中设置 browserNotSupported，它应该在 checkBrowserSupport 中设置
    return false
  }
}

// 请求麦克风权限
const requestMicrophonePermission = async () => {
  permissionRequested.value = true
  return await checkMicrophonePermission()
}

// 处理录音开始（防止事件冲突）
const handleRecordStart = (event) => {
  event.preventDefault()
  event.stopPropagation()
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:258',message:'handleRecordStart被调用',data:{eventType:event.type,isRecording:isRecording.value},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
  // #endregion
  if (!isRecording.value) {
    startRecording(event)
  }
}

// 处理录音停止（防止事件冲突）
const handleRecordStop = (event) => {
  event.preventDefault()
  event.stopPropagation()
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:271',message:'handleRecordStop被调用',data:{eventType:event.type,isRecording:isRecording.value,recordingDuration:recordingStartTime?Date.now()-recordingStartTime:null},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
  // #endregion
  if (isRecording.value && recordingStartTime) {
    const recordingDuration = Date.now() - recordingStartTime
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:278',message:'检查录音时长',data:{recordingDuration,minDuration:MIN_RECORDING_DURATION},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    // 如果录音时间太短，等待到最小时长
    if (recordingDuration < MIN_RECORDING_DURATION) {
      const remainingTime = MIN_RECORDING_DURATION - recordingDuration
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:282',message:'录音时长太短，延迟停止',data:{recordingDuration,remainingTime},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
      // #endregion
      setTimeout(() => {
        if (isRecording.value) {
          stopRecording(event)
        }
      }, remainingTime)
      return
    }
    stopRecording(event)
  }
}

// 开始录音
const startRecording = async (event) => {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:257',message:'startRecording被调用',data:{eventType:event?.type,isRecording:isRecording.value,hasMediaRecorder:!!mediaRecorder,mediaRecorderState:mediaRecorder?.state,hasMediaStream:!!mediaStream},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
  // #endregion
  
  // 防止重复触发
  if (isRecording.value) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:261',message:'已经在录音中，忽略重复调用',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    return
  }
  
  // 如果正在加载评分，不允许开始新的录音
  if (loading.value) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:267',message:'正在加载评分，忽略录音请求',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    return
  }
  
  // 检查浏览器支持
  if (browserNotSupported.value) {
    alert('您的浏览器不支持录音功能')
    return
  }
  
  // 清理之前的资源（如果存在）
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:275',message:'清理之前的mediaRecorder',data:{state:mediaRecorder.state},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    try {
      if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop()
      }
    } catch (e) {
      console.error('清理mediaRecorder失败:', e)
    }
    mediaRecorder = null
  }
  
  if (mediaStream) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:285',message:'清理之前的mediaStream',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }

  // 如果还没有权限，先请求权限
  if (!hasPermission.value && !permissionRequested.value) {
    const granted = await requestMicrophonePermission()
    if (!granted) {
      return
    }
  }

  // 如果权限被拒绝，显示重试提示
  if (permissionDenied.value) {
    alert('请允许访问麦克风，然后刷新页面重试')
    return
  }

  try {
    // 增强的浏览器检查
    if (!navigator) {
      browserNotSupported.value = true
      console.error('浏览器不支持录音功能')
      return
    }

    let stream

    // 尝试使用现代API
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        })
      } catch (err) {
        // 如果现代API失败，尝试旧版API
        if (navigator.getUserMedia) {
          console.log('尝试使用旧版 getUserMedia API')
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
      // 使用旧版API
      console.log('使用旧版 getUserMedia API')
      stream = await new Promise((resolve, reject) => {
        navigator.getUserMedia(
          { audio: true },
          (stream) => resolve(stream),
          (error) => reject(error)
        )
      })
    } else {
      console.error('您的浏览器不支持录音功能')
      return
    }

    mediaStream = stream

    // 检查 MediaRecorder 支持
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

    // 创建 MediaRecorder
    try {
      mediaRecorder = new MediaRecorder(mediaStream, {
        mimeType: mimeType || undefined
      })
    } catch (recorderErr) {
      console.error('MediaRecorder 创建失败，尝试无参数创建:', recorderErr)
      mediaRecorder = new MediaRecorder(mediaStream)
    }

    audioChunks = []

    mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        audioChunks.push(event.data)
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:355',message:'收到音频数据块',data:{chunkSize:event.data.size,chunksCount:audioChunks.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
      }
    }

    mediaRecorder.onstop = async () => {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:361',message:'MediaRecorder停止事件触发',data:{chunksCount:audioChunks.length,state:mediaRecorder.state},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      
      // 确保获取所有剩余数据
      if (mediaRecorder.state !== 'inactive') {
        mediaRecorder.requestData()
      }
      
      const audioType = mediaRecorder.mimeType || 'audio/webm'
      const audioBlob = new Blob(audioChunks, { type: audioType })
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:370',message:'录音停止，生成Blob',data:{audioChunksCount:audioChunks.length,audioChunksTotalSize:audioChunks.reduce((sum,chunk)=>sum+(chunk.size||0),0),audioType,blobSize:audioBlob.size,blobType:audioBlob.type},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      
      // 验证音频数据有效性
      if (audioBlob.size < 1000) {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:442',message:'音频文件太小，可能录音失败',data:{blobSize:audioBlob.size,chunksCount:audioChunks.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
        console.warn('录音数据过小，放弃上传:', audioBlob.size, 'bytes')
        // 不显示alert，静默失败，让用户可以重试
        loading.value = false
        hasScore.value = false
        score.value = 0
        // 清理资源
        if (mediaStream) {
          mediaStream.getTracks().forEach(track => track.stop())
          mediaStream = null
        }
        mediaRecorder = null
        audioChunks = []
        return
      }
      
      await evaluateSpeech(audioBlob)

      // 清理资源
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop())
        mediaStream = null
      }
      mediaRecorder = null
      audioChunks = []
    }

    // 使用 timeslice 参数，每100ms采集一次数据，确保数据能够及时收集
    mediaRecorder.start(100)
    isRecording.value = true
    recordingStartTime = Date.now()
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:474',message:'录音已启动',data:{mediaRecorderState:mediaRecorder.state,mimeType:mimeType,startTime:recordingStartTime},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
  } catch (err) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:404',message:'录音启动失败',data:{errorName:err.name,errorMessage:err.message},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    console.error('录音启动失败:', err)

    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      permissionDenied.value = true
      alert('麦克风权限被拒绝，请在浏览器设置中允许麦克风权限')
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      alert('未找到麦克风设备，请检查设备连接')
    } else if (err.name === 'NotSupportedError') {
      alert('您的浏览器不支持录音功能，请使用最新版本的 Chrome、Firefox 或 Safari')
    } else {
      // 检查错误消息是否包含关键信息
      const errorMsg = err.message || String(err)
      if (errorMsg.includes('getUserMedia') || errorMsg.includes('undefined')) {
        alert('您的浏览器不支持录音功能，请升级浏览器或使用最新版本的 Chrome、Firefox、Safari')
      } else {
        alert(`录音失败: ${errorMsg}`)
      }
    }

    // 清理失败的资源
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
      mediaStream = null
    }
  }
}

// 停止录音
const stopRecording = (event) => {
  const recordingDuration = recordingStartTime ? Date.now() - recordingStartTime : 0
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:488',message:'stopRecording被调用',data:{eventType:event?.type,isRecording:isRecording.value,hasMediaRecorder:!!mediaRecorder,mediaRecorderState:mediaRecorder?.state,recordingDuration},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
  // #endregion
  
  if (!isRecording.value) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:492',message:'当前未在录音，忽略停止请求',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    return
  }
  
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:497',message:'停止录音',data:{state:mediaRecorder.state,recordingDuration},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    mediaRecorder.stop()
    isRecording.value = false
    recordingStartTime = null
  } else {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:502',message:'mediaRecorder状态异常',data:{hasMediaRecorder:!!mediaRecorder,state:mediaRecorder?.state},timestamp:Date.now(),sessionId:'debug-session',runId:'run3',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    isRecording.value = false
    recordingStartTime = null
  }
}

// 组件挂载时检查权限
onMounted(async () => {
  // 先检查浏览器支持
  checkBrowserSupport()

  // 如果浏览器支持，再检查权限
  if (!browserNotSupported.value) {
    try {
      await checkMicrophonePermission()
    } catch (err) {
      console.error('权限检查失败:', err)
      // 静默处理错误，不影响页面显示
    }
  }
})

// 组件卸载时清理资源
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

// 评估语音
const evaluateSpeech = async (audioBlob) => {
  loading.value = true
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:443',message:'evaluateSpeech开始，准备调用API',data:{letter:currentLetter.value.letter,blobSize:audioBlob.size,blobType:audioBlob.type},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
  // #endregion
  try {
    // 调用后端API评估语音
    const result = await speechAPI.evaluate(currentLetter.value.letter, audioBlob)
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:448',message:'API调用成功，收到结果',data:{score:result.score,accuracy:result.accuracy,feedback:result.feedback,resultKeys:Object.keys(result)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
    // #endregion
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:449',message:'设置评分结果',data:{score:result.score,scoreType:typeof result.score},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
    // #endregion
    score.value = result.score
    hasScore.value = true

    // 同步到后端进度
    try {
      await progressAPI.updateProgress(currentLetter.value.id, 2, score.value)
      await progressAPI.checkin()
    } catch (err) {
      console.error('同步进度失败:', err)
    }

    // 更新本地进度
    store.updateProgress(currentLetter.value.id, 2, score.value)
    store.checkin()

    // 动画效果
    nextTick(() => {
      if (scoreRef.value) {
        gsap.from(scoreRef.value, {
          scale: 0,
          duration: 0.5,
          ease: 'back.out(1.7)'
        })
      }
    })

    // 3星触发撒花
    if (score.value === 3) {
      showConfetti.value = true
      setTimeout(() => {
        showConfetti.value = false
      }, 3000)
    }
  } catch (err) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Record.vue:481',message:'evaluateSpeech失败',data:{errorMessage:err.message,errorName:err.name,errorStack:err.stack},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    console.error('语音评分失败:', err)
    alert('评分失败，请重试')
    // 重试
    hasScore.value = false
    score.value = 0
  } finally {
    loading.value = false
  }
}

// 重试
const retry = () => {
  hasScore.value = false
  score.value = 0
}

// 下一个字母
const goNext = () => {
  const currentIndex = store.letters.findIndex(l => l.letter === currentLetter.value.letter)
  const nextIndex = (currentIndex + 1) % store.letters.length
  const nextLetter = store.letters[nextIndex]
  router.replace(`/learn/${nextLetter.letter}`)
}
</script>

<style scoped>
.record-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.back-btn {
  align-self: flex-start;
  background: rgba(255,255,255,0.3);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 18px;
  cursor: pointer;
  margin-bottom: 20px;
}

.letter-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40px;
}

.letter-preview .letter {
  font-size: 80px;
  font-weight: bold;
  color: white;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.letter-preview .word {
  font-size: 28px;
  color: rgba(255,255,255,0.9);
}

.record-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40px;
}

.record-button {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: none;
  background: white;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.record-button:active,
.record-button.recording {
  transform: scale(1.1);
  box-shadow: 0 15px 50px rgba(0,0,0,0.3);
  background: #ff6b6b;
}

.record-icon {
  font-size: 60px;
}

.record-icon.pulse {
  animation: pulse 0.5s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.record-hint {
  margin-top: 20px;
  font-size: 20px;
  color: white;
  text-align: center;
  max-width: 280px;
}

.record-hint.recording {
  color: #ffeb3b;
  font-weight: bold;
}

.score-result {
  background: white;
  border-radius: 30px;
  padding: 30px 50px;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.score-stars {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.star {
  font-size: 50px;
  filter: grayscale(100%);
  transition: filter 0.3s, transform 0.3s;
}

.star.earned {
  filter: none;
  animation: starPop 0.5s ease-out;
}

@keyframes starPop {
  0% { transform: scale(0); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

.score-text {
  font-size: 22px;
  color: #333;
  margin-bottom: 25px;
}

.action-btns {
  display: flex;
  gap: 15px;
}

.retry-btn, .next-btn {
  padding: 15px 30px;
  border: none;
  border-radius: 15px;
  font-size: 18px;
  cursor: pointer;
  transition: transform 0.2s;
}

.retry-btn {
  background: #f0f0f0;
  color: #333;
}

.next-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.retry-btn:active, .next-btn:active {
  transform: scale(0.95);
}

.confetti {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.confetti-piece {
  position: absolute;
  font-size: 30px;
  animation: confettiFall 3s ease-out forwards;
}

.confetti-piece:nth-child(1) { left: 5%; animation-delay: 0s; }
.confetti-piece:nth-child(2) { left: 15%; animation-delay: 0.1s; }
.confetti-piece:nth-child(3) { left: 25%; animation-delay: 0.2s; }
.confetti-piece:nth-child(4) { left: 35%; animation-delay: 0.15s; }
.confetti-piece:nth-child(5) { left: 45%; animation-delay: 0.05s; }
.confetti-piece:nth-child(6) { left: 55%; animation-delay: 0.25s; }
.confetti-piece:nth-child(7) { left: 65%; animation-delay: 0.1s; }
.confetti-piece:nth-child(8) { left: 75%; animation-delay: 0.2s; }
.confetti-piece:nth-child(9) { left: 85%; animation-delay: 0.15s; }
.confetti-piece:nth-child(10) { left: 95%; animation-delay: 0.05s; }
.confetti-piece:nth-child(n+11) { left: calc((var(--i) - 10) * 10%); animation-delay: calc(var(--i) * 0.1s); }

@keyframes confettiFall {
  0% { top: -10%; opacity: 1; transform: rotate(0deg); }
  100% { top: 110%; opacity: 0; transform: rotate(720deg); }
}

/* 权限提示样式 */
.permission-prompt {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.prompt-content {
  background: white;
  border-radius: 30px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  max-width: 350px;
}

.prompt-icon {
  font-size: 80px;
  display: block;
  margin-bottom: 20px;
}

.prompt-content h3 {
  font-size: 28px;
  color: #333;
  margin-bottom: 15px;
}

.prompt-content p {
  font-size: 18px;
  color: #666;
  margin-bottom: 25px;
  line-height: 1.5;
}

.retry-permission-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 15px 40px;
  border-radius: 15px;
  font-size: 18px;
  cursor: pointer;
  transition: transform 0.2s;
  margin-bottom: 15px;
}

.retry-permission-btn:active {
  transform: scale(0.95);
}

.help-text {
  font-size: 14px !important;
  color: #999 !important;
  margin-bottom: 0 !important;
}

.permission-check {
  margin-top: 20px;
  font-size: 16px;
  color: rgba(255,255,255,0.8);
}

.browser-list {
  font-size: 16px !important;
  color: #666 !important;
  text-align: left;
  background: #f5f5f5;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 15px;
  line-height: 1.8;
}
</style>
