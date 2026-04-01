import asyncio
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import ProviderRequest
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.api import logger


@register(
    "astrbot_plugin_openclaw_session",
    "OpenClaw Session",
    "OpenClaw Session 管理 - 为每个用户/群生成固定 session key",
    "v1.0.0"
)
class OpenClawSession(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
    
    @filter.on_llm_request()
    async def on_llm_request_handler(self, event: AstrMessageEvent, req: ProviderRequest):
        """Hook into LLM requests，设置 session key"""
        # 获取当前 provider_id
        try:
            provider_id = await self.context.get_current_chat_provider_id(
                umo=event.unified_msg_origin
            )
            # 只取最后一段，比如 "Openclaw/openclaw/main" -> "main"
            model_id = provider_id.split("/")[-1] if provider_id else "main"
        except Exception as e:
            logger.warning(f"[OpenClaw Session] 获取 provider 失败: {e}")
            model_id = "main"
        
        # 获取 user_id 和 group_id
        user_id = str(event.get_sender_id())
        group_id = str(event.get_group_id()) if event.get_group_id() else ""
        
        # 群聊用 group_id，私聊用 user_id
        if group_id:
            session_id = group_id
        else:
            session_id = user_id
        
        # 拼接 session key: agent:<model>:openai:<user_id/group_id>
        session_key = f"agent:{model_id}:openai:{session_id}"
        
        logger.info(f"[OpenClaw Session] 设置 session key: {session_key}")
        
        # 设置 x-openclaw-session-key header
        req.headers = req.headers or {}
        req.headers["x-openclaw-session-key"] = session_key
    
    async def terminate(self):
        """插件卸载时调用"""
        pass