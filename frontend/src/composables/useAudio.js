import { ref } from 'vue'

/**
 * 音频播放组合式函数
 */
export function useAudio() {
  const isPlaying = ref(false)
  const currentAudio = ref(null)

  /**
   * 播放字母发音
   * @param {string} letter - 字母 (a-z)
   */
  const playLetterSound = (letter) => {
    // 停止当前播放的音频
    if (currentAudio.value) {
      currentAudio.value.pause()
      currentAudio.value = null
    }

    // 尝试从本地文件加载
    try {
      const audio = new Audio(`/audio/${letter.toLowerCase()}.mp3`)
      audio.volume = 0.8

      audio.onplay = () => {
        isPlaying.value = true
      }

      audio.onended = () => {
        isPlaying.value = false
        currentAudio.value = null
      }

      audio.onerror = () => {
        // 如果文件不存在，使用Web Speech API
        console.log(`音频文件不存在，使用语音合成: ${letter}`)
        playWithSpeechSynthesis(letter)
      }

      currentAudio.value = audio
      audio.play()
    } catch (error) {
      // 如果加载失败，使用Web Speech API
      console.log('使用语音合成:', error)
      playWithSpeechSynthesis(letter)
    }
  }

  /**
   * 使用Web Speech API播放发音
   * @param {string} letter - 字母
   */
  const playWithSpeechSynthesis = (letter) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(letter.toUpperCase())
      utterance.lang = 'en-US'
      utterance.rate = 0.7
      utterance.pitch = 1.2
      utterance.volume = 0.8

      utterance.onstart = () => {
        isPlaying.value = true
      }

      utterance.onend = () => {
        isPlaying.value = false
      }

      speechSynthesis.speak(utterance)
    } else {
      console.warn('浏览器不支持语音合成')
      isPlaying.value = false
    }
  }

  /**
   * 播放奖励音效
   */
  const playRewardSound = () => {
    // 可以在这里添加奖励音效
    // 目前使用Web Audio API生成简单的提示音
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)

      oscillator.frequency.value = 800
      oscillator.type = 'sine'

      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)

      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.5)
    } catch (error) {
      console.warn('无法播放奖励音效:', error)
    }
  }

  /**
   * 停止播放
   */
  const stop = () => {
    if (currentAudio.value) {
      currentAudio.value.pause()
      currentAudio.value = null
    }
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel()
    }
    isPlaying.value = false
  }

  return {
    isPlaying,
    playLetterSound,
    playRewardSound,
    stop
  }
}
