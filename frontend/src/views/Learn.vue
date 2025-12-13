<template>
  <div class="learn-page">
    <!-- 顶部栏：返回按钮和进度指示 -->
    <div class="top-bar">
      <button class="back-btn" @click="$router.back()">
        ← 返回
      </button>
      <div class="progress-indicator">
        <div
          class="progress-dot"
          :class="{ active: progress.stage >= 1 }"
        >1</div>
        <div class="progress-line" :class="{ active: progress.stage >= 2 }"></div>
        <div
          class="progress-dot"
          :class="{ active: progress.stage >= 2 }"
        >2</div>
        <div class="progress-line" :class="{ active: progress.stage >= 3 }"></div>
        <div
          class="progress-dot"
          :class="{ active: progress.stage >= 3 }"
        >3</div>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="main-content">
      <!-- 字母和单词组合展示 -->
      <div class="letter-word-group">
        <div class="letter-display" ref="letterRef" @click="handlePlayLetter">
          <div class="big-letter">{{ currentLetter.letter }}</div>
          <div class="small-letter">{{ currentLetter.letter.toLowerCase() }}</div>
        </div>
        <div class="word-section" @click="handlePlayWord">
          <span class="word-image">{{ currentLetter.image }}</span>
          <span class="word-text">{{ currentLetter.word }}</span>
        </div>
      </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <!-- Back按钮 -->
      <a 
        class="nav-btn back-nav-btn" 
        :href="`/learn/${prevLetter}`"
        @click.prevent="goBack"
      >
        <span class="nav-icon">←</span>
      </a>
      <!-- 跟读练习 -->
      <button 
        class="action-btn record-btn" 
        :class="{ recording: isRecording, loading: loading }"
        :disabled="loading || browserNotSupported"
        @mousedown.prevent="handleRecordStart"
        @mouseup.prevent="handleRecordStop"
        @touchstart.prevent="handleRecordStart"
        @touchend.prevent="handleRecordStop"
      >
        <span class="btn-icon" v-if="!isRecording && !hasScore && !loading">🎤</span>
        <span class="btn-icon pulse" v-else-if="isRecording">🔴</span>
        <span class="btn-icon" v-else-if="loading">⏳</span>
        <span class="btn-icon" v-else>✅</span>
        <span v-if="!isRecording && !hasScore && !loading">跟读</span>
        <span v-else-if="isRecording">录音中...</span>
        <span v-else-if="loading">评分中...</span>
        <span v-else>完成</span>
      </button>
      <!-- Next按钮 -->
      <a 
        class="nav-btn next-btn" 
        :href="`/learn/${nextLetter}`"
        @click.prevent="goNext"
      >
        <span class="nav-icon">→</span>
      </a>
    </div>

    <!-- 录音提示 -->
    <div class="record-hint" v-if="!hasScore">
      <p v-if="!isRecording && !hasScore && !loading && !permissionDenied">
        按住按钮，大声读出字母 "{{ currentLetter.letter }}"
      </p>
      <p v-else-if="isRecording" class="recording">
        正在录音... 松开结束
      </p>
      <p v-else-if="loading">
        正在评分...
      </p>
      <p v-else-if="permissionDenied" class="error">
        需要麦克风权限，请允许访问麦克风
      </p>
      <p v-else-if="browserNotSupported" class="error">
        您的浏览器不支持录音功能
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
          <button class="playback-btn" @click="togglePlayback" v-if="recordedAudioUrl">
            {{ isPlaying ? '⏸️' : '▶️' }}
          </button>
          <button class="next-btn" @click="goNext" v-if="score >= 1">
            下一个 →
          </button>
        </div>
        <!-- 隐藏的音频元素用于回放 -->
        <audio 
          ref="audioPlayer" 
          @ended="isPlaying = false"
          @error="handleAudioError"
          style="display: none;"
        >
          <source v-if="recordedAudioUrl" :src="recordedAudioUrl" type="audio/webm">
          <source v-if="recordedAudioUrl" :src="recordedAudioUrl" type="audio/mpeg">
          <source v-if="recordedAudioUrl" :src="recordedAudioUrl" type="audio/wav">
          您的浏览器不支持音频播放
          <source :src="recordedAudioUrl" type="audio/webm">
          <source :src="recordedAudioUrl" type="audio/mpeg">
          <source :src="recordedAudioUrl" type="audio/wav">
          您的浏览器不支持音频播放
        </audio>
      </div>

      <!-- 阶段提示（紧凑版） -->
      <div class="stage-hint" v-if="!hasScore">
        <span v-if="progress.stage === 0">点击字母或单词听发音 👆</span>
        <span v-else-if="progress.stage === 1">按住按钮跟读 🎤</span>
        <span v-else-if="progress.stage >= 2">继续练习 🌟</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLearningStore } from '../stores/learning'
import { useAudio } from '../composables/useAudio'
import { speechAPI } from '../api/speech'
import { progressAPI } from '../api/progress'
import gsap from 'gsap'

const route = useRoute()
const router = useRouter()
const store = useLearningStore()
const letterRef = ref(null)
const scoreRef = ref(null)
const audioPlayer = ref(null)
const { playLetterSound, playWordSound, playRewardSound } = useAudio()

// 录音相关状态
const isRecording = ref(false)
const hasScore = ref(false)
const score = ref(0)
const showConfetti = ref(false)
const loading = ref(false)
const hasPermission = ref(false)
const permissionDenied = ref(false)
const permissionRequested = ref(false)
const browserNotSupported = ref(false)
const recordedAudioUrl = ref(null)
const recordedAudioId = ref(null)
const isPlaying = ref(false)

// 录音相关变量
let mediaRecorder = null
let audioChunks = []
let mediaStream = null
let recordingStartTime = null
let isStartingRecording = false // 标记是否正在启动录音
let delayedStopTimeout = null // 延迟停止的timeout ID
const MIN_RECORDING_DURATION = 500 // 最小录音时长500毫秒

const currentLetter = computed(() => {
  const letter = route.params.letter.toUpperCase()
  return store.letters.find(l => l.letter === letter) || store.letters[0]
})

const progress = computed(() => {
  return store.getLetterProgress(currentLetter.value.id)
})

const scoreText = computed(() => {
  if (score.value === 3) return '太棒了！发音非常标准！🎉'
  if (score.value === 2) return '很好！继续加油！👍'
  if (score.value === 1) return '不错的开始，再练练！💪'
  return '再试一次吧！🔄'
})

const nextLetter = computed(() => {
  const currentIndex = store.letters.findIndex(l => l.letter === currentLetter.value.letter)
  const nextIndex = (currentIndex + 1) % store.letters.length
  return store.letters[nextIndex].letter
})

const prevLetter = computed(() => {
  const currentIndex = store.letters.findIndex(l => l.letter === currentLetter.value.letter)
  const prevIndex = (currentIndex - 1 + store.letters.length) % store.letters.length
  return store.letters[prevIndex].letter
})

// 播放字母发音
const handlePlayLetter = () => {
  playLetterSound(currentLetter.value.letter)

  if (letterRef.value) {
    gsap.fromTo(letterRef.value,
      { scale: 1 },
      { scale: 1.1, duration: 0.3, yoyo: true, repeat: 1 }
    )
  }

  if (progress.value.stage === 0) {
    store.updateProgress(currentLetter.value.id, 1, 0)
  }
}

// 播放单词发音
const handlePlayWord = () => {
  playWordSound(currentLetter.value.word)

  if (progress.value.stage === 0) {
    store.updateProgress(currentLetter.value.id, 1, 0)
  }
}

// 检查浏览器支持
const checkBrowserSupport = () => {
  browserNotSupported.value = !navigator || (!navigator.mediaDevices && !navigator.getUserMedia)
}

// 检查麦克风权限
const checkMicrophonePermission = async () => {
  try {
    if (!navigator.mediaDevices) {
      if (navigator.getUserMedia) {
        try {
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
        hasPermission.value = false
        return false
      }
    }

    if (typeof navigator.mediaDevices.getUserMedia !== 'function') {
      hasPermission.value = false
      return false
    }

    const constraints = {
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    }

    let stream
    try {
      stream = await navigator.mediaDevices.getUserMedia(constraints)
    } catch (getUserMediaErr) {
      throw getUserMediaErr
    }

    stream.getTracks().forEach(track => track.stop())

    hasPermission.value = true
    permissionDenied.value = false
    return true
  } catch (err) {
    console.error('麦克风权限检查失败:', err)
    hasPermission.value = false

    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      permissionDenied.value = true
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      permissionDenied.value = false
    } else if (err.name === 'NotSupportedError') {
      permissionDenied.value = false
    }
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
  
  // 如果有一个延迟停止的timeout，取消它（用户再次按下，说明要继续录音）
  if (delayedStopTimeout !== null) {
    clearTimeout(delayedStopTimeout)
    delayedStopTimeout = null
  }
  
  if (!isRecording.value && !loading.value) {
    startRecording(event)
  }
}

// 处理录音停止（防止事件冲突）
const handleRecordStop = (event) => {
  event.preventDefault()
  event.stopPropagation()
  
  // 如果正在启动录音，取消启动
  if (isStartingRecording) {
    isStartingRecording = false
    return
  }
  
  if (isRecording.value && recordingStartTime) {
    const recordingDuration = Date.now() - recordingStartTime
    // 如果录音时间太短，判断是误触还是需要延迟停止
    if (recordingDuration < MIN_RECORDING_DURATION) {
      // 如果录音时间极短（<100ms），认为是误触，直接取消录音
      if (recordingDuration < 100) {
        // 取消之前的延迟停止（如果有）
        if (delayedStopTimeout !== null) {
          clearTimeout(delayedStopTimeout)
          delayedStopTimeout = null
        }
        // 直接停止并清理，不进行评分
        // 注意：不要调用stop()，因为这会触发onstop事件，导致loading状态混乱
        // 直接清理资源即可
        isRecording.value = false
        recordingStartTime = null
        loading.value = false  // 确保loading被重置
        // 清理资源
        if (mediaStream) {
          mediaStream.getTracks().forEach(track => track.stop())
          mediaStream = null
        }
        if (mediaRecorder) {
          // 如果recorder正在录音，直接停止track，不调用stop()避免触发onstop
          try {
            if (mediaRecorder.state === 'recording') {
              // 停止stream的track来终止录音，但不触发onstop事件
              if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop())
              }
            }
          } catch (e) {
            console.error('停止录音失败:', e)
          }
        }
        mediaRecorder = null
        audioChunks = []
        return
      }
      // 如果录音时间在100-500ms之间，延迟停止
      const remainingTime = MIN_RECORDING_DURATION - recordingDuration
      // 取消之前的延迟停止（如果有）
      if (delayedStopTimeout !== null) {
        clearTimeout(delayedStopTimeout)
      }
      // 设置新的延迟停止
      delayedStopTimeout = setTimeout(() => {
        delayedStopTimeout = null
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
  // 防止重复触发
  if (isRecording.value || isStartingRecording) {
    return
  }
  
  // 如果正在加载评分，不允许开始新的录音
  if (loading.value) {
    return
  }
  
  if (browserNotSupported.value) {
    alert('您的浏览器不支持录音功能')
    return
  }
  
  // 标记正在启动录音
  isStartingRecording = true
  
  // 清理之前的资源（如果存在）
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
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
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }

  if (!hasPermission.value && !permissionRequested.value) {
    const granted = await requestMicrophonePermission()
    if (!granted) {
      return
    }
  }

  if (permissionDenied.value) {
    alert('请允许访问麦克风，然后刷新页面重试')
    return
  }

  try {
    if (!navigator) {
      browserNotSupported.value = true
      console.error('浏览器不支持录音功能')
      return
    }

    let stream

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

    let mimeType = 'audio/webm;codecs=opus'
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      if (MediaRecorder.isTypeSupported('audio/webm')) {
        mimeType = 'audio/webm'
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4'
      } else {
        mimeType = ''
      }
    }

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
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      // 立即设置isRecording为false和loading为true，防止在清理过程中触发新的录音
      isRecording.value = false
      recordingStartTime = null
      loading.value = true // 立即设置loading，防止新录音在评估期间开始
      
      // 保存当前实例的引用，确保清理的是正确的实例
      const currentMediaRecorder = mediaRecorder
      const currentMediaStream = mediaStream
      const currentAudioChunks = [...audioChunks]
      
      try {
        const audioType = currentMediaRecorder ? (currentMediaRecorder.mimeType || 'audio/webm') : 'audio/webm'
        const audioBlob = new Blob(currentAudioChunks, { type: audioType })
        
        // 检查音频大小，如果太小（可能是误触或录音失败），静默失败
        if (audioBlob.size < 1000) {
          loading.value = false
          // 清理资源
          if (mediaStream === currentMediaStream && currentMediaStream) {
            currentMediaStream.getTracks().forEach(track => track.stop())
            if (mediaStream === currentMediaStream) {
              mediaStream = null
            }
          }
          if (mediaRecorder === currentMediaRecorder) {
            mediaRecorder = null
          }
          if (!isRecording.value && !isStartingRecording) {
            audioChunks = []
          }
          return
        }
        
        // evaluateSpeech内部也会设置loading，但我们已经提前设置了，确保一致性
        await evaluateSpeech(audioBlob)
      } catch (error) {
        console.error('录音处理错误:', error)
        loading.value = false  // 确保在错误情况下也重置loading
      }

      // 只清理当前实例，如果已经被新的录音替换，则不清理
      if (mediaStream === currentMediaStream && currentMediaStream) {
        currentMediaStream.getTracks().forEach(track => track.stop())
        if (mediaStream === currentMediaStream) {
          mediaStream = null
        }
      }
      
      if (mediaRecorder === currentMediaRecorder) {
        mediaRecorder = null
      }
      
      // 清理audioChunks，但只在没有新录音开始的情况下
      if (!isRecording.value && !isStartingRecording) {
        audioChunks = []
      }
    }

    // 检查是否在启动过程中被取消
    if (!isStartingRecording) {
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop())
        mediaStream = null
      }
      return
    }
    
    // 使用 timeslice 参数，每100ms采集一次数据，确保数据能够及时收集
    mediaRecorder.start(100)
    isRecording.value = true
    isStartingRecording = false // 清除启动标志
    recordingStartTime = Date.now()
  } catch (err) {
    isStartingRecording = false // 清除启动标志
    console.error('录音启动失败:', err)

    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      permissionDenied.value = true
      alert('麦克风权限被拒绝，请在浏览器设置中允许麦克风权限')
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      alert('未找到麦克风设备，请检查设备连接')
    } else if (err.name === 'NotSupportedError') {
      alert('您的浏览器不支持录音功能，请使用最新版本的 Chrome、Firefox 或 Safari')
    } else {
      const errorMsg = err.message || String(err)
      if (errorMsg.includes('getUserMedia') || errorMsg.includes('undefined')) {
        alert('您的浏览器不支持录音功能，请升级浏览器或使用最新版本的 Chrome、Firefox、Safari')
      } else {
        alert(`录音失败: ${errorMsg}`)
      }
    }

    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
      mediaStream = null
    }
    isStartingRecording = false // 清除启动标志
  }
}

// 停止录音
const stopRecording = (event) => {
  // 清除启动标志和延迟停止timeout
  isStartingRecording = false
  if (delayedStopTimeout !== null) {
    clearTimeout(delayedStopTimeout)
    delayedStopTimeout = null
  }
  
  if (!isRecording.value) {
    return
  }
  
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop()
    isRecording.value = false
    recordingStartTime = null
  } else {
    isRecording.value = false
    recordingStartTime = null
  }
}

// 评估语音
const evaluateSpeech = async (audioBlob) => {
  loading.value = true
  try {
    const result = await speechAPI.evaluate(currentLetter.value.letter, audioBlob)
    score.value = result.score
    hasScore.value = true

    // 保存录音到服务器
    try {
      const recordingResult = await speechAPI.saveRecording(
        currentLetter.value.letter,
        audioBlob,
        result.score
      )
      recordedAudioUrl.value = recordingResult.file_url
      recordedAudioId.value = recordingResult.id
    } catch (saveErr) {
      console.error('保存录音失败:', saveErr)
      // 即使保存失败，也创建本地URL用于回放
      recordedAudioUrl.value = URL.createObjectURL(audioBlob)
    }

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
    console.error('语音评分失败:', err)
    alert('评分失败，请重试')
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
  recordedAudioUrl.value = null
  recordedAudioId.value = null
  isPlaying.value = false
  if (audioPlayer.value) {
    audioPlayer.value.pause()
    audioPlayer.value.currentTime = 0
  }
}

// 处理音频错误
const handleAudioError = (e) => {
  console.error('音频加载错误:', e.target.error)
  isPlaying.value = false
  if (e.target.error && (e.target.error.code === 4 || e.target.error.message?.includes('NotSupportedError'))) {
    alert('当前浏览器不支持该音频格式，请使用Chrome、Firefox或Edge浏览器')
  }
}

// 切换回放
const togglePlayback = () => {
  if (!audioPlayer.value || !recordedAudioUrl.value) return

  if (isPlaying.value) {
    audioPlayer.value.pause()
    isPlaying.value = false
  } else {
    // 如果是相对URL，需要添加baseURL
    let audioUrl = recordedAudioUrl.value
    if (!audioUrl.startsWith('http') && !audioUrl.startsWith('blob:')) {
      const apiBase = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '') || ''
      audioUrl = `${apiBase}${audioUrl}`
    }
    
    // 如果URL已改变，更新src
    if (audioPlayer.value.src !== audioUrl && !audioUrl.startsWith('blob:')) {
      audioPlayer.value.src = audioUrl
    } else if (audioUrl.startsWith('blob:')) {
      // blob URL直接使用
      audioPlayer.value.src = audioUrl
    }
    
    // 添加错误处理
    audioPlayer.value.onerror = (e) => {
      console.error('音频播放错误:', e.target.error)
      isPlaying.value = false
      // 如果是格式不支持错误，提示用户
      if (e.target.error && (e.target.error.code === 4 || e.target.error.message?.includes('NotSupportedError'))) {
        alert('当前浏览器不支持该音频格式，请使用Chrome、Firefox或Edge浏览器')
      }
    }
    
    audioPlayer.value.play().catch(err => {
      console.error('播放失败:', err)
      isPlaying.value = false
      if (err.name === 'NotSupportedError') {
        alert('当前浏览器不支持该音频格式，请使用Chrome、Firefox或Edge浏览器')
      }
    })
    isPlaying.value = true
  }
}

// 下一个字母
const goNext = () => {
  const currentIndex = store.letters.findIndex(l => l.letter === currentLetter.value.letter)
  const nextIndex = (currentIndex + 1) % store.letters.length
  const nextLetter = store.letters[nextIndex]
  router.push(`/learn/${nextLetter.letter}`)
}

// 上一个字母
const goBack = () => {
  const currentIndex = store.letters.findIndex(l => l.letter === currentLetter.value.letter)
  const prevIndex = (currentIndex - 1 + store.letters.length) % store.letters.length
  const prevLetter = store.letters[prevIndex]
  router.push(`/learn/${prevLetter.letter}`)
}

// 入场动画
onMounted(async () => {
  if (letterRef.value) {
    gsap.from(letterRef.value, {
      scale: 0,
      rotation: -180,
      duration: 0.8,
      ease: 'back.out(1.7)'
    })
  }

  // 检查浏览器支持和权限
  checkBrowserSupport()
  if (!browserNotSupported.value) {
    try {
      await checkMicrophonePermission()
    } catch (err) {
      console.error('权限检查失败:', err)
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
  if (recordedAudioUrl.value && recordedAudioUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(recordedAudioUrl.value)
  }
  if (audioPlayer.value) {
    audioPlayer.value.pause()
  }
})
</script>

<style scoped>
.learn-page {
  min-height: 100vh;
  height: 100vh;
  overflow-y: auto;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 10px 15px 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
}

.top-bar {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.back-btn {
  background: rgba(255,255,255,0.3);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 16px;
  cursor: pointer;
}

.main-content {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  padding: 5px 0;
  overflow-y: auto;
}

.letter-word-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  width: 100%;
  flex-shrink: 0;
}

.letter-display {
  background: white;
  border-radius: 20px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
  cursor: pointer;
  width: 100%;
  max-width: 224px;
  aspect-ratio: 2 / 3;
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex-shrink: 0;
}

.big-letter {
  font-size: 100px;
  font-weight: bold;
  color: #333;
  line-height: 1;
}

.small-letter {
  font-size: 60px;
  color: #666;
  margin-top: 8px;
}

.word-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(255,255,255,0.9);
  padding: 15px 25px;
  border-radius: 18px;
  cursor: pointer;
  width: 100%;
  max-width: 350px;
  flex-shrink: 0;
}

.word-image {
  font-size: 42px;
}

.word-text {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
  max-width: 400px;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px 20px;
  border: none;
  border-radius: 15px;
  font-size: 24px;
  cursor: pointer;
  transition: transform 0.2s;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  min-width: 50px;
  width: 50px;
  height: 50px;
}

.nav-icon {
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 18px 25px;
  border: none;
  border-radius: 18px;
  font-size: 18px;
  cursor: pointer;
  transition: transform 0.2s;
  flex: 1;
  min-width: 120px;
  max-width: 200px;
}

.action-btn:active {
  transform: scale(0.95);
}

.listen-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.record-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.record-btn.recording {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  transform: scale(1.05);
}

.record-btn.loading {
  opacity: 0.7;
  cursor: not-allowed;
}

.nav-btn:active {
  transform: scale(0.95);
}

.btn-icon {
  font-size: 40px;
}

.btn-icon.pulse {
  animation: pulse 0.5s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.progress-indicator {
  display: flex;
  align-items: center;
  gap: 0;
}

.progress-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255,255,255,0.3);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  transition: background 0.3s;
}

.progress-dot.active {
  background: #4CAF50;
}

.progress-line {
  width: 40px;
  height: 3px;
  background: rgba(255,255,255,0.3);
  transition: background 0.3s;
}

.progress-line.active {
  background: #4CAF50;
}

.stage-hint {
  color: white;
  font-size: 14px;
  text-align: center;
  padding: 8px 16px;
  background: rgba(255,255,255,0.2);
  border-radius: 10px;
  width: 100%;
  max-width: 400px;
  flex-shrink: 0;
}

.record-hint {
  text-align: center;
  color: white;
  font-size: 14px;
  width: 100%;
  max-width: 400px;
  flex-shrink: 0;
}

.record-hint p {
  margin: 0;
  padding: 6px 14px;
  background: rgba(255,255,255,0.2);
  border-radius: 10px;
}

.record-hint p.recording {
  color: #ffeb3b;
  font-weight: bold;
}

.record-hint p.error {
  color: #ff6b6b;
}

.score-result {
  background: white;
  border-radius: 20px;
  padding: 15px 20px;
  text-align: center;
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
  width: 100%;
  max-width: 400px;
  flex-shrink: 0;
}

.score-stars {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-bottom: 10px;
}

.star {
  font-size: 32px;
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
  font-size: 16px;
  color: #333;
  margin-bottom: 12px;
  line-height: 1.3;
}

.action-btns {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.retry-btn, .playback-btn, .action-btns .next-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.2s;
  flex: 1;
  min-width: 80px;
}

.playback-btn {
  min-width: 50px;
  flex: 0 0 auto;
}

.retry-btn {
  background: #f0f0f0;
  color: #333;
}

.playback-btn {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
}

.action-btns .next-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.retry-btn:active, .playback-btn:active, .action-btns .next-btn:active {
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
  z-index: 1000;
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

/* 移动端优化 */
@media (max-width: 768px) {
  .learn-page {
    padding: 8px 15px 15px;
  }

  .top-bar {
    margin-bottom: 12px;
  }

  .back-btn {
    padding: 6px 12px;
    font-size: 14px;
  }

  .progress-dot {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }

  .progress-line {
    width: 30px;
  }

  .letter-display {
    padding: 20px 30px;
  }

  .big-letter {
    font-size: 70px;
  }

  .small-letter {
    font-size: 45px;
  }

  .word-section {
    padding: 10px 20px;
  }

  .word-image {
    font-size: 32px;
  }

  .word-text {
    font-size: 20px;
  }

  .action-btn {
    padding: 15px 20px;
    font-size: 16px;
  }

  .stage-hint {
    font-size: 14px;
    padding: 8px 16px;
  }
}
</style>
