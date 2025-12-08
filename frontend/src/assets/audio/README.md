# 音频资源说明

## 需要的音频文件

本目录需要存放26个字母的标准发音音频文件，格式为MP3或WAV。

### 文件命名规范

```
a.mp3  - 字母A的发音
b.mp3  - 字母B的发音
...
z.mp3  - 字母Z的发音
```

### 音频要求

- **格式**: MP3 或 WAV
- **音质**: 清晰、标准的美式英语发音
- **时长**: 1-2秒
- **音量**: 标准化音量
- **适合儿童**: 发音清晰、语速适中

## 获取方式

### 方式1: 使用TTS服务生成（推荐）

可以使用以下TTS服务生成：

```bash
# 使用espeak (Linux/macOS)
for letter in {a..z}; do
  espeak -s 120 -v en-us "$letter" -w "${letter}.wav"
done

# 使用Festival (Linux)
echo "a b c d e f g h i j k l m n o p q r s t u v w x y z" | \
  festival --tts --otype wav

# 使用Amazon Polly (需要AWS账户)
aws polly synthesize-speech \
  --text-type text \
  --text "A" \
  --voice-id Joey \
  --output-format mp3 \
  --sample-rate 22050 \
  a.mp3
```

### 方式2: 使用在线TTS

1. **Google Text-to-Speech**: https://cloud.google.com/text-to-speech
2. **Amazon Polly**: https://aws.amazon.com/polly/
3. **Microsoft Speech**: https://azure.microsoft.com/zh-cn/products/cognitive-services/speech-services/

### 方式3: 录音

使用Audacity等软件录制标准发音：
1. 录制26个字母的发音
2. 分割为单独文件
3. 导出为MP3格式

## 临时方案

目前应用使用浏览器的Web Speech API作为临时方案：
```javascript
const utterance = new SpeechSynthesisUtterance(letter)
utterance.lang = 'en-US'
utterance.rate = 0.7
speechSynthesis.speak(utterance)
```

这不需要额外的音频文件，但依赖用户的浏览器支持。

## 注意事项

- 确保音频文件在正确的目录中
- 文件名必须为小写字母（a.mp3, b.mp3, ...）
- 建议使用CDN或静态资源服务优化加载速度
