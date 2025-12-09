from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import SpeechEvalResponse
from app.routers.auth import get_current_user
from app.config import get_settings
from app.services.aliyun_speech import evaluate_speech as evaluate_speech_service

router = APIRouter(prefix="/speech", tags=["语音评分"])

settings = get_settings()


@router.post("/evaluate", response_model=SpeechEvalResponse)
async def evaluate_speech(
    letter: str = Form(...),
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    _db: AsyncSession = Depends(get_db)
):
    """
    评估用户语音发音

    参数:
    - letter: 目标字母 (A-Z)
    - audio: 音频文件

    返回:
    - score: 1-3星评分
    - accuracy: 准确度百分比
    - feedback: 反馈文字
    """
    # 验证字母
    if len(letter) != 1 or not letter.isalpha():
        raise HTTPException(status_code=400, detail="请提供单个字母")

    letter = letter.upper()

    # 读取音频数据
    audio_content = await audio.read()

    # 验证音频大小 (最大5MB)
    if len(audio_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="音频文件过大")

    # 使用语音评分服务（阿里云API或本地模拟）
    result = await evaluate_speech_service(audio_content, letter)

    return SpeechEvalResponse(
        score=result["score"],
        accuracy=result["accuracy"],
        feedback=result["feedback"]
    )


# ============ 阿里云语音评测API集成示例 ============
#
# async def aliyun_speech_evaluation(letter: str, audio_data: bytes) -> SpeechEvalResponse:
#     """
#     阿里云智能语音交互 - 语音评测
#     文档: https://help.aliyun.com/document_detail/84435.html
#     """
#     import nls  # pip install aliyun-python-sdk-core aliyun-python-sdk-nls
#
#     class SpeechEvaluator:
#         def __init__(self):
#             self.result = None
#
#         def on_result(self, message, *args):
#             self.result = json.loads(message)
#
#     evaluator = SpeechEvaluator()
#
#     # 创建评测实例
#     sr = nls.NlsSpeechEvaluator(
#         url="wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1",
#         akid=settings.aliyun_access_key_id,
#         aksecret=settings.aliyun_access_key_secret,
#         appkey=settings.aliyun_app_key,
#         on_result_changed=evaluator.on_result
#     )
#
#     # 设置评测文本和参数
#     sr.set_text(letter)
#     sr.set_ref_text(letter)
#
#     # 发送音频并获取结果
#     sr.start(audio_data)
#
#     # 解析结果
#     if evaluator.result:
#         overall_score = evaluator.result.get('overall_score', 0)
#         # 转换为1-3星
#         if overall_score >= 80:
#             score = 3
#         elif overall_score >= 60:
#             score = 2
#         else:
#             score = 1
#         return SpeechEvalResponse(
#             score=score,
#             accuracy=overall_score,
#             feedback=f"评测完成，得分: {overall_score}"
#         )
#
#     return SpeechEvalResponse(score=1, accuracy=0, feedback="评测失败")
