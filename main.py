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
        """Hook into LLM requests，生成 session key 并打印 req 属性"""
        # 生成 session key
        try:
            provider_id = await self.context.get_current_chat_provider_id(
                umo=event.unified_msg_origin
            )
            model_id = provider_id.split("/")[-1] if provider_id else "main"
        except Exception as e:
            logger.warning(f"[OpenClaw Session] 获取 provider 失败: {e}")
            model_id = "main"
        
        user_id = str(event.get_sender_id())
        group_id = str(event.get_group_id()) if event.get_group_id() else ""
        
        if group_id:
            session_id = group_id
        else:
            session_id = user_id
        
        session_key = f"agent:{model_id}:openai:{session_id}"
        logger.info(f"[OpenClaw Session] session_key: {session_key}")
        
        # 打印 req 的所有属性
        logger.info(f"[OpenClaw Session] === ProviderRequest 属性 ===")
        for attr in dir(req):
            if not attr.startswith('_'):
                try:
                    value = getattr(req, attr)
                    if not callable(value):
                        logger.info(f"[OpenClaw Session] {attr}: {value}")
                except Exception as e:
                    logger.info(f"[OpenClaw Session] {attr}: <获取失败: {e}>")
    
    async def terminate(self):
        """插件卸载时调用"""
        pass