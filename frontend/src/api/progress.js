import http from './http'

export const progressAPI = {
  // 获取学习进度
  getProgress() {
    return http.get('/api/progress/')
  },

  // 更新学习进度
  updateProgress(letterId, stage, score) {
    return http.post('/api/progress/update', {
      letter_id: letterId,
      stage,
      score
    })
  },

  // 打卡
  checkin() {
    return http.post('/api/progress/checkin')
  },

  // 获取打卡记录
  getCheckins() {
    return http.get('/api/progress/checkins')
  },

  // 获取统计信息
  getStats() {
    return http.get('/api/progress/stats')
  }
}
