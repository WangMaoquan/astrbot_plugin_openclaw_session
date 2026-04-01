import asyncio
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import ProviderRequest
from astrbot.api import AstrBotConfig
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
        """Hook into LLM requests，设置固定的 session key"""
        # 获取当前 provider_id
        try:
            provider_id = await self.context.get_current_chat_provider_id(
                umo=event.unified_msg_origin
            )
        except Exception as e:
            logger.warning(f"[OpenClaw Session] 获取 provider 失败: {e}")
            provider_id = "openai"
        
        # 获取 user_id 和 group_id
        user_id = str(event.get_sender_id())
        group_id = str(event.get_group_id()) if event.get_group_id() else ""
        
        # 群聊用 group_id，私聊用 user_id
        if group_id:
            session_id = group_id
        else:
            session_id = user_id
        
        # 格式: agent:main:<provider_id>:<user_id/group_id>
        session_key = f"agent:main:{provider_id}:{session_id}"
        
        logger.info(f"[OpenClaw Session] 设置 session key: {session_key}")
        
        # 设置自定义请求头
        req.headers = req.headers or {}
        req.headers["x-openclaw-session-key"] = session_key
    
    async def terminate(self):
        """插件卸载时调用"""
        pass