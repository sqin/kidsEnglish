"""
阿里云语音评测API集成

使用前需要：
1. 注册阿里云账户
2. 开通智能语音交互服务
3. 获取AccessKey、Secret和AppKey
4. 配置到.env文件中

文档：https://help.aliyun.com/document_detail/84435.html

当前实现使用HTTP API直接调用，确保与最新SDK版本兼容
"""

import json
import base64
import time
import hmac
import hashlib
import asyncio
from typing import Optional
from urllib.parse import urlencode
from datetime import datetime

import httpx
from app.config import get_settings


class AliyunSpeechEvaluator:
    """阿里云语音评测客户端（使用HTTP API）"""

    def __init__(self):
        self.settings = get_settings()
        self.access_key_id = self.settings.aliyun_access_key_id
        self.access_key_secret = self.settings.aliyun_access_key_secret
        self.app_key = self.settings.aliyun_app_key

        if not all([self.access_key_id, self.access_key_secret, self.app_key]):
            raise ValueError("阿里云配置不完整，请在.env文件中配置ALIYUN_ACCESS_KEY_ID等")

    def _generate_signature(self, method: str, url: str, params: dict, body: str = "") -> str:
        """生成阿里云API签名（简化版）"""
        # 对URL进行编码
        import urllib.parse

        # 移除签名相关参数
        params_to_sign = {k: v for k, v in params.items() if k != 'signature'}

        # 按照阿里云规范对参数进行排序和编码
        sorted_params = sorted(params_to_sign.items())
        query_string = urllib.parse.quote_plus("&".join([f"{k}={v}" for k, v in sorted_params]))

        # 构造待签名字符串
        string_to_sign = f"{method}&%2F&{query_string}"

        # 使用HMAC-SHA1算法计算签名
        signature = hmac.new(
            (self.access_key_secret + "&").encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()

        return base64.b64encode(signature).decode('utf-8')

    def _get_token(self) -> str:
        """获取访问令牌"""
        # 使用SDK获取token
        import nls.token

        token = nls.token.getToken(
            akid=self.access_key_id,
            aksecret=self.access_key_secret
        )
        return token

    async def _call_evaluation_api(self, audio_data: bytes, letter: str) -> dict:
        """
        调用阿里云语音评测HTTP API
        """
        # 获取访问令牌
        token = self._get_token()

        # 准备请求URL和参数
        url = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr"

        # 检测音频格式（通过文件头）
        audio_format = "wav"  # 默认
        if len(audio_data) >= 4:
            if audio_data[:4] == b'RIFF' or (len(audio_data) > 8 and audio_data[8:12] == b'WAVE'):
                audio_format = "wav"
            elif audio_data[:4] == b'\x1aE\xdf\xa3':
                audio_format = "webm"
                # #region agent log
                import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:92','message':'检测到webm格式','data':{'audioSize':len(audio_data),'detectedFormat':audio_format},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run2','hypothesisId':'D'})+'\n')
                # #endregion
            elif audio_data[:3] == b'ID3' or (len(audio_data) >= 2 and audio_data[:2] == b'\xff\xfb'):
                audio_format = "mp3"
        
        # 阿里云语音识别/评测API参数
        params = {
            "appkey": self.app_key,
            "timestamp": str(int(time.time() * 1000)),
            "sign_type": "HMAC-SHA1",
            "sign_version": "1.0",
            "v": "2.0",
            "aformat": audio_format,  # 使用检测到的格式
            "sample_rate": 16000,
            "text": letter.upper(),  # 评测文本
            "token": token,  # 添加token参数
        }

        # 生成签名
        params["signature"] = self._generate_signature("POST", "/stream/v1/asr", params)

        # 准备音频数据
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        # 构建请求体 - 根据实际格式调整
        payload = {
            "audio": audio_base64,
            "aformat": audio_format,  # 使用检测到的格式
            "sample_rate": 16000,
            "text": letter.upper()
        }
        # #region agent log
        import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:117','message':'设置API请求payload','data':{'aformat':audio_format,'audioBase64Length':len(audio_base64)},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run2','hypothesisId':'D'})+'\n')
        # #endregion

        # 发送请求
        headers = {
            "Content-Type": "application/json"
        }

        # #region agent log
        import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:118','message':'准备发送阿里云API请求','data':{'url':url,'audioBase64Length':len(audio_base64),'paramsKeys':list(params.keys()),'payloadKeys':list(payload.keys()),'letter':letter},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'D'})+'\n')
        # #endregion
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, params=params, json=payload, headers=headers)
            # #region agent log
            import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:119','message':'收到阿里云API响应','data':{'statusCode':response.status_code,'responseTextLength':len(response.text),'hasJson':bool(response.text)},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'D'})+'\n')
            # #endregion

            if response.status_code != 200:
                # #region agent log
                import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:121','message':'API返回非200状态码','data':{'statusCode':response.status_code,'responseText':response.text[:500]},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'D'})+'\n')
                # #endregion
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")

            result = response.json()
            # #region agent log
            import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:125','message':'解析API响应JSON','data':{'resultKeys':list(result.keys()) if isinstance(result,dict) else 'not_dict','resultStr':str(result)[:500]},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'D'})+'\n')
            # #endregion
            return result

    async def evaluate(self, audio_data: bytes, letter: str) -> dict:
        """
        评估语音

        Args:
            audio_data: 音频数据 (WAV/PCM格式)
            letter: 目标字母

        Returns:
            评估结果字典
        """
        # #region agent log
        import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:127','message':'evaluate开始，准备调用阿里云API','data':{'audioSize':len(audio_data),'letter':letter},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'C'})+'\n')
        # #endregion
        # 如果没有音频数据或字母，返回错误
        if not audio_data or not letter:
            raise ValueError("音频数据和字母不能为空")

        try:
            # 调用阿里云API
            result = await self._call_evaluation_api(audio_data, letter)
            # #region agent log
            import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:144','message':'阿里云API调用返回','data':{'resultKeys':list(result.keys()) if isinstance(result,dict) else 'not_dict','status':result.get('status') if isinstance(result,dict) else None,'hasResult':bool(result.get('result')) if isinstance(result,dict) else False,'hasScore':bool(result.get('score')) if isinstance(result,dict) else False},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'D'})+'\n')
            # #endregion

            # 解析API响应
            status = result.get('status', 200)
            # #region agent log
            import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:147','message':'检查API响应状态','data':{'status':status,'expectedStatus':20000000},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'D'})+'\n')
            # #endregion
            if status != 20000000:
                error_msg = result.get('message', '未知错误')
                # #region agent log
                import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:149','message':'API返回错误状态','data':{'status':status,'errorMsg':error_msg},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'D'})+'\n')
                # #endregion
                print(f"阿里云评测API错误: {error_msg}")
                raise Exception(f"API错误: {error_msg}")

            # 提取评测结果
            eval_result = result.get('result') or result.get('score')
            # #region agent log
            import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:154','message':'提取评测结果','data':{'hasResult':bool(result.get('result')),'hasScore':bool(result.get('score')),'evalResultType':type(eval_result).__name__ if eval_result else None,'evalResultKeys':list(eval_result.keys()) if isinstance(eval_result,dict) else None},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'E'})+'\n')
            # #endregion

            if eval_result:
                if isinstance(eval_result, dict):
                    score = eval_result.get('overall') or eval_result.get('pronunciation_score') or eval_result.get('score', 0)
                    # #region agent log
                    import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:158','message':'从字典提取分数','data':{'score':score,'overall':eval_result.get('overall'),'pronunciation_score':eval_result.get('pronunciation_score'),'score_key':eval_result.get('score')},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'E'})+'\n')
                    # #endregion
                elif isinstance(eval_result, (int, float)):
                    score = eval_result
                    # #region agent log
                    import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:160','message':'eval_result是数值类型','data':{'score':score},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'E'})+'\n')
                    # #endregion
                else:
                    score = 0
                    # #region agent log
                    import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:162','message':'eval_result类型不匹配，设为0','data':{'evalResultType':type(eval_result).__name__},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'E'})+'\n')
                    # #endregion
            else:
                score = 0
                # #region agent log
                import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:164','message':'eval_result为空，设为0','data':{},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'E'})+'\n')
                # #endregion

            # 确保分数在合理范围内
            if score > 100:
                score = min(score, 100)

            # 转换为星星评分
            if score >= 85:
                stars = 3
                feedback = f"太棒了！你的 {letter} 发音非常标准！"
            elif score >= 70:
                stars = 2
                feedback = f"很好！{letter} 发音不错，继续加油！"
            else:
                stars = 1
                feedback = f"不错的开始！再练习一下 {letter} 的发音吧！"
            # #region agent log
            import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:177','message':'评分转换完成','data':{'originalScore':score if 'score' in locals() else None,'stars':stars,'feedback':feedback},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'E'})+'\n')
            # #endregion

            return {
                "score": stars,
                "accuracy": round(score, 1) if isinstance(score, (int, float)) else 0,
                "feedback": feedback,
                "audio_length": len(audio_data),
                "details": result
            }

        except Exception as e:
            # #region agent log
            import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'aliyun_speech.py:189','message':'evaluate异常','data':{'errorType':type(e).__name__,'errorMessage':str(e)},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'D'})+'\n')
            # #endregion
            print(f"阿里云语音评估异常: {e}")
            raise  # 重新抛出异常，不使用模拟评估

    async def _mock_evaluate(self, audio_data: bytes, letter: str) -> dict:
        """
        本地模拟评估（开发阶段使用）
        """
        # 简单的模拟逻辑
        import random

        # 模拟音频长度
        audio_length = len(audio_data) if audio_data else 0

        # 如果音频太短或太长，降低分数
        if audio_length < 1000:  # 小于1KB
            base_score = 60
        elif audio_length > 50000:  # 大于50KB
            base_score = 70
        else:
            base_score = random.uniform(75, 95)

        # 添加一些随机性
        score = base_score + random.uniform(-10, 10)
        score = max(50, min(100, score))

        # 转换为星星评分
        if score >= 85:
            stars = 3
            feedback = f"太棒了！你的 {letter} 发音非常标准！"
        elif score >= 70:
            stars = 2
            feedback = f"很好！{letter} 发音不错，继续加油！"
        else:
            stars = 1
            feedback = f"不错的开始！再练习一下 {letter} 的发音吧！"

        return {
            "score": stars,
            "accuracy": round(score, 1),
            "feedback": feedback,
            "audio_length": audio_length
        }


# 全局实例
_speech_evaluator = None


def get_speech_evaluator() -> Optional[AliyunSpeechEvaluator]:
    """获取语音评估器实例"""
    global _speech_evaluator
    if _speech_evaluator is None:
        _speech_evaluator = AliyunSpeechEvaluator()
    return _speech_evaluator


async def evaluate_speech(audio_data: bytes, letter: str) -> dict:
    """
    评估语音的主函数

    使用阿里云API进行语音评测
    """
    evaluator = get_speech_evaluator()

    if not evaluator:
        raise ValueError("阿里云语音评测服务未正确配置，请检查.env文件中的ALIYUN_*配置")

    return await evaluator.evaluate(audio_data, letter)
