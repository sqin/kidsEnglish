import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.models import User, Recording
from app.schemas.schemas import SpeechEvalResponse, RecordingResponse
from app.routers.auth import get_current_user
from app.config import get_settings
from app.services.aliyun_speech import evaluate_speech as evaluate_speech_service

router = APIRouter(prefix="/speech", tags=["语音评分"])

settings = get_settings()

# 确保上传目录存在
UPLOAD_DIR = Path("uploads/audio")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
    # #region agent log
    import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'speech.py:49','message':'后端接收音频数据','data':{'audioSize':len(audio_content),'filename':audio.filename,'contentType':audio.content_type,'letter':letter,'audioStartBytes':audio_content[:20].hex() if len(audio_content)>=20 else audio_content.hex()},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run2','hypothesisId':'C'})+'\n')
    # #endregion

    # 验证音频大小 (最大5MB)
    if len(audio_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="音频文件过大")

    # 使用语音评分服务（阿里云API或本地模拟）
    result = await evaluate_speech_service(audio_content, letter)
    # #region agent log
    import json; open('/Users/linshengqin/Documents/Code/kidsEnglish/.cursor/debug.log','a').write(json.dumps({'location':'speech.py:56','message':'evaluate_speech_service返回结果','data':{'resultKeys':list(result.keys()) if isinstance(result,dict) else 'not_dict','score':result.get('score') if isinstance(result,dict) else None},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'E'})+'\n')
    # #endregion

    return SpeechEvalResponse(
        score=result["score"],
        accuracy=result["accuracy"],
        feedback=result["feedback"]
    )


@router.post("/save", response_model=RecordingResponse)
async def save_recording(
    letter: str = Form(...),
    audio: UploadFile = File(...),
    score: int = Form(0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    保存用户录音

    参数:
    - letter: 目标字母 (A-Z)
    - audio: 音频文件
    - score: 评分 (0-3)

    返回:
    - 录音记录信息
    """
    # 验证字母
    if len(letter) != 1 or not letter.isalpha():
        raise HTTPException(status_code=400, detail="请提供单个字母")

    letter = letter.upper()

    # 验证评分
    if score < 0 or score > 3:
        raise HTTPException(status_code=400, detail="评分必须在0-3之间")

    # 读取音频数据
    audio_content = await audio.read()

    # 验证音频大小 (最大5MB)
    if len(audio_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="音频文件过大")

    # 生成文件名：用户ID_字母_时间戳.扩展名
    file_ext = audio.filename.split('.')[-1] if '.' in audio.filename else 'webm'
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{current_user.id}_{letter}_{timestamp}.{file_ext}"
    file_path = UPLOAD_DIR / filename

    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(audio_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")

    # 获取字母ID
    letter_id = ord(letter) - ord('A') + 1

    # 生成文件URL（相对路径，前端需要配置正确的baseURL）
    file_url = f"/api/speech/audio/{filename}"

    # 保存到数据库
    recording = Recording(
        user_id=current_user.id,
        letter_id=letter_id,
        letter=letter,
        file_path=str(file_path),
        file_url=file_url,
        score=score
    )
    db.add(recording)
    await db.commit()
    await db.refresh(recording)

    return RecordingResponse(
        id=recording.id,
        letter_id=recording.letter_id,
        letter=recording.letter,
        file_url=recording.file_url,
        score=recording.score,
        created_at=recording.created_at
    )


@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """
    获取音频文件
    """
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    # 根据文件扩展名确定媒体类型
    ext = filename.split('.')[-1].lower()
    media_types = {
        'webm': 'audio/webm',
        'mp3': 'audio/mpeg',
        'mp4': 'audio/mp4',
        'wav': 'audio/wav',
        'ogg': 'audio/ogg'
    }
    media_type = media_types.get(ext, 'audio/webm')

    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(file_path),
        media_type=media_type
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
