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
        """Hook into LLM requests，测试获取 provider_id"""
        # 获取当前 provider_id
        try:
            provider_id = await self.context.get_current_chat_provider_id(
                umo=event.unified_msg_origin
            )
            logger.info(f"[OpenClaw Session] 获取到的 provider_id: {provider_id}")
        except Exception as e:
            logger.warning(f"[OpenClaw Session] 获取 provider 失败: {e}")
        
        # TODO: 后续再添加 session key 设置逻辑
        # session_key = f"agent:main:{provider_id}:{session_id}"
        # req.headers = req.headers or {}
        # req.headers["x-openclaw-session-key"] = session_key
    
    async def terminate(self):
        """插件卸载时调用"""
        pass