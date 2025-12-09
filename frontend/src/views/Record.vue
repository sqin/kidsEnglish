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

    <!-- 权限被拒绝提示 -->
    <div class="permission-prompt" v-if="permissionDenied && !loading">
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
    <div class="record-area" v-else>
      <button
        class="record-button"
        :class="{ recording: isRecording, scored: hasScore, loading: loading }"
        :disabled="loading"
        @mousedown="startRecording"
        @mouseup="stopRecording"
        @touchstart.prevent="startRecording"
        @touchend.prevent="stopRecording"
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

let mediaRecorder = null
let audioChunks = []
let audioContext = null
let mediaStream = null

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

// 检查麦克风权限
const checkMicrophonePermission = async () => {
  try {
    // 检查浏览器是否支持
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('您的浏览器不支持录音功能')
    }

    // 检查权限状态
    const devices = await navigator.mediaDevices.enumerateDevices()
    const audioDevices = devices.filter(device => device.kind === 'audioinput')

    if (audioDevices.length === 0) {
      throw new Error('未检测到麦克风设备')
    }

    // 尝试获取权限但不录音
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    })

    // 立即停止流，只为验证权限
    stream.getTracks().forEach(track => track.stop())

    hasPermission.value = true
    permissionDenied.value = false
    return true
  } catch (err) {
    console.error('麦克风权限检查失败:', err)
    hasPermission.value = false

    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      permissionDenied.value = true
    }
    return false
  }
}

// 请求麦克风权限
const requestMicrophonePermission = async () => {
  permissionRequested.value = true
  return await checkMicrophonePermission()
}

// 开始录音
const startRecording = async () => {
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
    // 获取音频流
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    })

    // 创建 MediaRecorder
    mediaRecorder = new MediaRecorder(mediaStream, {
      mimeType: 'audio/webm;codecs=opus'
    })
    audioChunks = []

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      await evaluateSpeech(audioBlob)

      // 清理资源
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop())
        mediaStream = null
      }
      mediaRecorder = null
      audioChunks = []
    }

    mediaRecorder.start()
    isRecording.value = true
  } catch (err) {
    console.error('录音启动失败:', err)
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      permissionDenied.value = true
      alert('麦克风权限被拒绝，请在浏览器设置中允许麦克风权限')
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      alert('未找到麦克风设备，请检查设备连接')
    } else {
      alert(`录音失败: ${err.message}`)
    }

    // 清理失败的资源
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
      mediaStream = null
    }
  }
}

// 停止录音
const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop()
    isRecording.value = false
  }
}

// 组件挂载时检查权限
onMounted(async () => {
  await checkMicrophonePermission()
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
  try {
    // 调用后端API评估语音
    const result = await speechAPI.evaluate(currentLetter.value.letter, audioBlob)
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
</style>
