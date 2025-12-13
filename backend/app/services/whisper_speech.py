"""
Whisper 语音识别评分服务

使用 faster-whisper 进行本地语音识别，基于置信度给出评分
"""

import io
import math
import tempfile
from typing import Optional, Dict, Tuple
from pathlib import Path

from faster_whisper import WhisperModel
from app.config import get_settings

# 字母到单词的映射（与前端 learning.js 保持一致）
LETTER_WORD_MAP = {
    'A': 'Apple',
    'B': 'Ball',
    'C': 'Cat',
    'D': 'Dog',
    'E': 'Elephant',
    'F': 'Fish',
    'G': 'Grape',
    'H': 'House',
    'I': 'Ice cream',
    'J': 'Juice',
    'K': 'Kite',
    'L': 'Lion',
    'M': 'Moon',
    'N': 'Nest',
    'O': 'Orange',
    'P': 'Panda',
    'Q': 'Queen',
    'R': 'Rainbow',
    'S': 'Sun',
    'T': 'Tiger',
    'U': 'Umbrella',
    'V': 'Violin',
    'W': 'Watermelon',
    'X': 'X-ray',
    'Y': 'Yo-yo',
    'Z': 'Zebra',
}


class WhisperSpeechEvaluator:
    """Whisper 语音识别评估器"""

    def __init__(self):
        self.settings = get_settings()
        self.model_size = self.settings.whisper_model_size
        self.device = self.settings.whisper_device
        self.language = self.settings.whisper_language
        
        # 延迟加载模型（首次使用时加载）
        self._model: Optional[WhisperModel] = None

    @property
    def model(self) -> WhisperModel:
        """获取 Whisper 模型实例（单例模式）"""
        if self._model is None:
            try:
                self._model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type="int8" if self.device == "cpu" else "float16"
                )
            except Exception as e:
                raise RuntimeError(f"加载 Whisper 模型失败: {str(e)}")
        return self._model

    def _normalize_text(self, text: str) -> str:
        """标准化文本：转小写、去除标点、去除空格"""
        import re
        # 转小写并去除标点符号
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        # 去除空格
        text = text.replace(' ', '')
        return text

    def _check_match(self, recognized_text: str, target_letter: str) -> Tuple[bool, float]:
        """
        检查识别结果是否匹配目标字母或单词
        
        Returns:
            (是否匹配, 最高置信度)
        """
        recognized_lower = recognized_text.lower().strip()
        target_letter_upper = target_letter.upper()
        target_letter_lower = target_letter.lower()
        
        # 获取目标单词
        target_word = LETTER_WORD_MAP.get(target_letter_upper, "")
        target_word_lower = target_word.lower() if target_word else ""
        
        # 标准化文本用于匹配
        recognized_normalized = self._normalize_text(recognized_text)
        target_letter_normalized = self._normalize_text(target_letter_lower)
        target_word_normalized = self._normalize_text(target_word_lower) if target_word else ""
        
        # 检查是否包含目标字母（精确匹配或包含）
        letter_match = (
            recognized_lower == target_letter_lower or
            recognized_normalized == target_letter_normalized or
            target_letter_lower in recognized_lower or
            target_letter_normalized in recognized_normalized
        )
        
        # 检查是否包含目标单词（精确匹配或包含）
        word_match = False
        if target_word:
            word_match = (
                recognized_lower == target_word_lower or
                recognized_normalized == target_word_normalized or
                target_word_lower in recognized_lower or
                target_word_normalized in recognized_normalized
            )
        
        # 特殊处理：Ice cream 可能识别为 icecream
        if target_letter_upper == 'I' and 'ice' in recognized_lower and 'cream' in recognized_lower:
            word_match = True
        
        # 特殊处理：X-ray 可能识别为 xray 或 x ray
        if target_letter_upper == 'X' and ('xray' in recognized_lower or 'x ray' in recognized_lower):
            word_match = True
        
        # 特殊处理：Yo-yo 可能识别为 yoyo 或 yo yo
        if target_letter_upper == 'Y' and ('yoyo' in recognized_lower or 'yo yo' in recognized_lower):
            word_match = True
        
        # 更宽松的匹配：检查单词的部分匹配和相似音
        if not letter_match and not word_match and target_word:
            # 检查识别结果中是否包含目标单词的前3个字符（如 "app" 匹配 "apple"）
            target_prefix = target_word_lower[:3]
            if len(target_prefix) >= 3:
                if target_prefix in recognized_lower:
                    word_match = True
                # 检查识别结果的前3个字符是否匹配目标单词的前3个字符
                if len(recognized_lower) >= 3 and recognized_lower[:3] == target_prefix:
                    word_match = True
                # 检查识别结果中是否包含目标单词的关键部分（如 "app" 在 "apple" 中）
                if target_prefix in recognized_normalized:
                    word_match = True
                # 检查识别结果中是否包含目标单词的关键音节（如 "ap" 匹配 "apple"）
                if len(target_prefix) >= 2 and target_prefix[:2] in recognized_lower:
                    word_match = True
        
        return letter_match or word_match, 1.0  # 返回匹配结果和置信度

    async def evaluate(self, audio_data: bytes, letter: str) -> Dict:
        """
        评估语音
        
        Args:
            audio_data: 音频数据 (支持多种格式)
            letter: 目标字母 (A-Z)
        
        Returns:
            评估结果字典，包含:
            - score: 星星数 (0-3)
            - accuracy: 准确度百分比 (0-100)
            - feedback: 反馈文字
            - audio_length: 音频长度
            - details: 详细信息
        """
        if not audio_data or not letter:
            raise ValueError("音频数据和字母不能为空")
        
        letter = letter.upper()
        if letter not in LETTER_WORD_MAP:
            raise ValueError(f"无效的字母: {letter}")
        
        try:
            # 将音频数据保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # 使用 Whisper 进行识别
                # 构建初始提示，帮助Whisper识别字母和单词
                target_word = LETTER_WORD_MAP.get(letter, "")
                initial_prompt = f"{letter}. {target_word}." if target_word else letter
                
                segments, info = self.model.transcribe(
                    tmp_path,
                    language=self.language,
                    beam_size=5,
                    vad_filter=False,  # 禁用VAD，避免过滤掉短音频
                    condition_on_previous_text=False,  # 不依赖前文，更适合单字母/单词识别
                    initial_prompt=initial_prompt,  # 提供初始提示，引导识别
                    temperature=0.0,  # 降低随机性，提高准确性
                )
                
                # 收集所有识别片段
                recognized_texts = []
                confidences = []
                
                for segment in segments:
                    text = segment.text.strip()
                    if text:
                        recognized_texts.append(text)
                        confidences.append(segment.avg_logprob)  # 使用平均对数概率作为置信度
                
                # 合并识别结果
                full_text = " ".join(recognized_texts).strip()
                
                # 计算平均置信度（将对数概率转换为置信度）
                if confidences:
                    # 对数概率通常在 -1 到 0 之间，转换为 0-1 的置信度
                    # 使用 exp 转换，然后归一化
                    avg_logprob = sum(confidences) / len(confidences)
                    # 将对数概率转换为置信度：exp(logprob) 然后归一化到 0-1
                    # 由于 logprob 通常是负数，我们使用 sigmoid 函数转换
                    # avg_logprob 通常在 -1 到 0 之间，我们将其映射到 0-1
                    confidence = 1 / (1 + math.exp(-avg_logprob * 2))  # 乘以2来调整范围
                else:
                    confidence = 0.0
                    full_text = ""
                
                # 检查是否匹配 - 对每个识别片段都进行检查
                matched = False
                for text in recognized_texts:
                    if text.strip():
                        segment_matched, _ = self._check_match(text.strip(), letter)
                        if segment_matched:
                            matched = True
                            break
                
                # 如果单个片段不匹配，再检查完整文本
                if not matched:
                    matched, _ = self._check_match(full_text, letter)
                
                # 根据匹配结果和置信度计算评分
                # 评分规则：
                # 1. 完全匹配 → 3星
                # 2. 不完全匹配（部分匹配） → 2星或1星
                # 3. 没识别到 → 1星（鼓励分）
                
                target_word = LETTER_WORD_MAP.get(letter, "")
                
                # 检查是否完全匹配
                is_exact_match = False
                if matched:
                    recognized_lower = full_text.lower().strip()
                    target_letter_lower = letter.lower()
                    target_word_lower = target_word.lower() if target_word else ""
                    
                    # 完全匹配：识别结果完全等于目标字母或单词（忽略大小写和标点）
                    recognized_clean = self._normalize_text(full_text)
                    target_letter_clean = self._normalize_text(target_letter_lower)
                    target_word_clean = self._normalize_text(target_word_lower) if target_word else ""
                    
                    is_exact_match = (
                        recognized_clean == target_letter_clean or
                        recognized_clean == target_word_clean or
                        recognized_lower == target_letter_lower or
                        recognized_lower == target_word_lower
                    )
                
                # 检查是否有部分匹配
                partial_match = False
                if not matched and target_word and full_text:
                    target_lower = target_word.lower()
                    recognized_lower = full_text.lower()
                    # 检查是否包含目标单词的前2-3个字符
                    if len(target_lower) >= 3:
                        prefix = target_lower[:2]  # 前2个字符
                        if prefix in recognized_lower:
                            partial_match = True
                    # 检查是否包含目标字母
                    if letter.lower() in recognized_lower:
                        partial_match = True
                
                # 根据匹配情况评分
                if is_exact_match:
                    # 完全匹配 → 3星
                    stars = 3
                    feedback = f"太棒了！你的 {letter} 发音非常标准！"
                elif matched or partial_match:
                    # 不完全匹配 → 根据置信度给2星或1星
                    if confidence >= 0.3:
                        stars = 2
                        feedback = f"很好！识别到了 {letter}，继续加油！"
                    else:
                        stars = 1
                        feedback = f"识别到了部分内容，再试试完整地说出 {letter} 或 {target_word} 吧！"
                else:
                    # 没识别到 → 1星（鼓励分）
                    stars = 1
                    if full_text:
                        feedback = f"识别到: \"{full_text}\"，但未识别到 {letter}，再试试吧！"
                    else:
                        feedback = f"未识别到语音，请大声读出字母 {letter}！"
                
                # 计算准确度百分比（基于置信度）
                accuracy = round(confidence * 100, 1) if matched else 0.0
                
                result = {
                    "score": stars,
                    "accuracy": accuracy,
                    "feedback": feedback,
                    "audio_length": len(audio_data),
                    "details": {
                        "recognized_text": full_text,
                        "confidence": round(confidence, 3),
                        "matched": matched,
                        "target_letter": letter,
                        "target_word": LETTER_WORD_MAP.get(letter, ""),
                    }
                }
                return result
            
            finally:
                # 清理临时文件
                try:
                    Path(tmp_path).unlink()
                except Exception:
                    pass
        
        except Exception as e:
            print(f"Whisper 语音评估异常: {e}")
            raise RuntimeError(f"语音识别失败: {str(e)}")


# 全局实例
_speech_evaluator: Optional[WhisperSpeechEvaluator] = None


def get_speech_evaluator() -> Optional[WhisperSpeechEvaluator]:
    """获取语音评估器实例"""
    global _speech_evaluator
    if _speech_evaluator is None:
        _speech_evaluator = WhisperSpeechEvaluator()
    return _speech_evaluator


async def evaluate_speech(audio_data: bytes, letter: str) -> Dict:
    """
    评估语音的主函数
    
    使用 Whisper 进行语音识别和评分
    """
    evaluator = get_speech_evaluator()
    
    if not evaluator:
        raise ValueError("Whisper 语音识别服务未正确初始化")
    
    return await evaluator.evaluate(audio_data, letter)

