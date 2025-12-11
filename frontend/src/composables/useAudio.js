import { ref } from 'vue'

/**
 * 音频播放组合式函数
 */
export function useAudio() {
  const isPlaying = ref(false)
  const currentAudio = ref(null)

  /**
   * 公共播放函数，支持字母和单词音频
   * @param {string} path - 相对 public 的音频路径
   * @param {string} fallbackText - 当音频缺失时使用语音合成播报的文本
   */
  const playAudioFile = (path, fallbackText) => {
    // 停止当前播放的音频
    if (currentAudio.value) {
      currentAudio.value.pause()
      currentAudio.value = null
    }

    try {
      const audio = new Audio(path)
      audio.volume = 0.8

      audio.onplay = () => {
        isPlaying.value = true
      }

      audio.onended = () => {
        isPlaying.value = false
        currentAudio.value = null
      }

      audio.onerror = () => {
        console.log(`音频文件不存在，使用语音合成: ${fallbackText}`)
        playWithSpeechSynthesis(fallbackText)
      }

      currentAudio.value = audio
      audio.play()
    } catch (error) {
      console.log('使用语音合成:', error)
      playWithSpeechSynthesis(fallbackText)
    }
  }

  /**
   * 播放字母发音
   * @param {string} letter - 字母 (a-z)
   */
  const playLetterSound = (letter) => {
    playAudioFile(`/audio/${letter.toLowerCase()}.mp3`, letter)
  }

  /**
   * 播放单词发音
   * @param {string} word - 单词，使用小写/包含连字符的文件名
   */
  const playWordSound = (word) => {
    const normalized = word.toLowerCase()
    playAudioFile(`/audio/${normalized}.mp3`, word)
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
    playWordSound,
    playRewardSound,
    stop
  }
}
