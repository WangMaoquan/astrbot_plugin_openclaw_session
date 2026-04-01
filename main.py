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
        """Hook into LLM requests，生成并打印 session key"""
        # 获取当前 provider_id
        try:
            provider_id = await self.context.get_current_chat_provider_id(
                umo=event.unified_msg_origin
            )
            # 只取最后一段，比如 "Openclaw/openclaw/main" -> "main"
            agent_id = provider_id.split("/")[-1] if provider_id else "main"
        except Exception as e:
            logger.warning(f"[OpenClaw Session] 获取 provider 失败: {e}")
            agent_id = "main"
        
        # 获取 user_id 和 group_id
        user_id = str(event.get_sender_id())
        group_id = str(event.get_group_id()) if event.get_group_id() else ""
        
        # 群聊用 group_id，私聊用 user_id
        if group_id:
            session_id = group_id
        else:
            session_id = user_id
        
        # 拼接 session key
        session_key = f"agent:main:{agent_id}:{session_id}"
        
        logger.info(f"[OpenClaw Session] session_key: {session_key}")
        
        # TODO: 后续添加实际设置 session key 的逻辑
    
    async def terminate(self):
        """插件卸载时调用"""
        pass