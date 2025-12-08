import http from './http'

export const speechAPI = {
  // 评估语音
  evaluate(letter, audioBlob) {
    const formData = new FormData()
    formData.append('letter', letter)
    formData.append('audio', audioBlob)

    return http.post('/api/speech/evaluate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}
