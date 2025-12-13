import http from './http'

export const speechAPI = {
  // 评估语音
  evaluate(letter, audioBlob) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'speech.js:5',message:'构建FormData准备上传',data:{letter,blobSize:audioBlob.size,blobType:audioBlob.type},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    const formData = new FormData()
    formData.append('letter', letter)
    formData.append('audio', audioBlob)

    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/8cca928c-d5b9-43d9-97e1-7898a9124d5d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'speech.js:10',message:'发送POST请求到后端',data:{url:'/api/speech/evaluate',hasLetter:formData.has('letter'),hasAudio:formData.has('audio')},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    return http.post('/api/speech/evaluate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 保存录音
  saveRecording(letter, audioBlob, score = 0) {
    const formData = new FormData()
    formData.append('letter', letter)
    formData.append('audio', audioBlob)
    formData.append('score', score.toString())

    return http.post('/api/speech/save', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}
