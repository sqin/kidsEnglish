import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useLearningStore = defineStore('learning', () => {
  // 26个字母数据
  const letters = ref([
    { id: 1, letter: 'A', word: 'Apple', image: '🍎', audio: '/audio/a.mp3' },
    { id: 2, letter: 'B', word: 'Ball', image: '⚽', audio: '/audio/b.mp3' },
    { id: 3, letter: 'C', word: 'Cat', image: '🐱', audio: '/audio/c.mp3' },
    { id: 4, letter: 'D', word: 'Dog', image: '🐶', audio: '/audio/d.mp3' },
    { id: 5, letter: 'E', word: 'Elephant', image: '🐘', audio: '/audio/e.mp3' },
    { id: 6, letter: 'F', word: 'Fish', image: '🐟', audio: '/audio/f.mp3' },
    { id: 7, letter: 'G', word: 'Grape', image: '🍇', audio: '/audio/g.mp3' },
    { id: 8, letter: 'H', word: 'House', image: '🏠', audio: '/audio/h.mp3' },
    { id: 9, letter: 'I', word: 'Ice cream', image: '🍦', audio: '/audio/i.mp3' },
    { id: 10, letter: 'J', word: 'Juice', image: '🧃', audio: '/audio/j.mp3' },
    { id: 11, letter: 'K', word: 'Kite', image: '🪁', audio: '/audio/k.mp3' },
    { id: 12, letter: 'L', word: 'Lion', image: '🦁', audio: '/audio/l.mp3' },
    { id: 13, letter: 'M', word: 'Moon', image: '🌙', audio: '/audio/m.mp3' },
    { id: 14, letter: 'N', word: 'Nest', image: '🪺', audio: '/audio/n.mp3' },
    { id: 15, letter: 'O', word: 'Orange', image: '🍊', audio: '/audio/o.mp3' },
    { id: 16, letter: 'P', word: 'Panda', image: '🐼', audio: '/audio/p.mp3' },
    { id: 17, letter: 'Q', word: 'Queen', image: '👸', audio: '/audio/q.mp3' },
    { id: 18, letter: 'R', word: 'Rainbow', image: '🌈', audio: '/audio/r.mp3' },
    { id: 19, letter: 'S', word: 'Sun', image: '☀️', audio: '/audio/s.mp3' },
    { id: 20, letter: 'T', word: 'Tiger', image: '🐯', audio: '/audio/t.mp3' },
    { id: 21, letter: 'U', word: 'Umbrella', image: '☂️', audio: '/audio/u.mp3' },
    { id: 22, letter: 'V', word: 'Violin', image: '🎻', audio: '/audio/v.mp3' },
    { id: 23, letter: 'W', word: 'Watermelon', image: '🍉', audio: '/audio/w.mp3' },
    { id: 24, letter: 'X', word: 'X-ray', image: '🩻', audio: '/audio/x-ray.mp3' },
    { id: 25, letter: 'Y', word: 'Yo-yo', image: '🪀', audio: '/audio/y.mp3' },
    { id: 26, letter: 'Z', word: 'Zebra', image: '🦓', audio: '/audio/z.mp3' }
  ])

  // 学习进度（从localStorage加载）
  const progress = ref(JSON.parse(localStorage.getItem('learningProgress') || '{}'))

  // 打卡记录
  const checkins = ref(JSON.parse(localStorage.getItem('checkins') || '[]'))

  // 获取字母进度
  const getLetterProgress = (letterId) => {
    return progress.value[letterId] || { stage: 0, score: 0, completed: false }
  }

  // 更新字母进度
  const updateProgress = (letterId, stage, score) => {
    progress.value[letterId] = {
      stage,
      score,
      completed: stage >= 3,
      updatedAt: new Date().toISOString()
    }
    localStorage.setItem('learningProgress', JSON.stringify(progress.value))
  }

  // 打卡
  const checkin = () => {
    const today = new Date().toISOString().split('T')[0]
    if (!checkins.value.includes(today)) {
      checkins.value.push(today)
      localStorage.setItem('checkins', JSON.stringify(checkins.value))
    }
  }

  // 连续打卡天数
  const streakDays = computed(() => {
    if (checkins.value.length === 0) return 0
    const sorted = [...checkins.value].sort().reverse()
    let streak = 0
    const today = new Date()

    for (let i = 0; i < sorted.length; i++) {
      const checkDate = new Date(sorted[i])
      const diff = Math.floor((today - checkDate) / (1000 * 60 * 60 * 24))
      if (diff === streak) {
        streak++
      } else {
        break
      }
    }
    return streak
  })

  // 总星星数
  const totalStars = computed(() => {
    return Object.values(progress.value).reduce((sum, p) => sum + (p.score || 0), 0)
  })

  return {
    letters,
    progress,
    checkins,
    getLetterProgress,
    updateProgress,
    checkin,
    streakDays,
    totalStars
  }
})
