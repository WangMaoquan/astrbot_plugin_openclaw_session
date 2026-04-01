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
        # 存储每个 provider 的原始 custom_headers，用于请求后恢复
        self._original_custom_headers = {}
    
    @filter.on_llm_request()
    async def on_llm_request_handler(self, event: AstrMessageEvent, req: ProviderRequest):
        """LLM 请求前触发：为每个 provider 添加 session-key header"""
        
        # 获取 AstrBot 配置
        config = self._get_context_config();
        provider_sources = config.get("provider_sources", [])
        
        # logger.info(f"[OpenClaw Session] provider_sources: {provider_sources}")

        # 生成 session key：根据 user_id 或 group_id 区分会话
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
        
        # 私聊用 user_id，群聊用 group_id
        if group_id:
            session_id = group_id
        else:
            session_id = user_id
        
        session_key = f"agent:{model_id}:openai:{session_id}"
        logger.info(f"[OpenClaw Session] session_key: {session_key}")

        # 保存原始 custom_headers 并添加 session-key
        # 这样 OpenClaw 可以根据 session-key 识别不同用户/群的会话
        self._original_custom_headers = {}
        for ps in provider_sources:
            ps_id = ps.get('id', '')
            self._original_custom_headers[ps_id] = ps.get('custom_headers', {}).copy()
            ps['custom_headers']['x-openclaw-session-key'] = session_key
        
        # logger.info(f"[OpenClaw Session] 原始 custom_headers: {self._original_custom_headers}")
        # logger.info(f"[OpenClaw Session] update provider_sources: {provider_sources}")
        
    @filter.on_llm_response()
    async def on_llm_response_handler(self, event: AstrMessageEvent, resp):
        """LLM 响应后触发：恢复原始 custom_headers，避免影响下次请求"""
        
        # 恢复原始 custom_headers
        config = self._get_context_config()
        provider_sources = config.get("provider_sources", [])
        
        # logger.info(f"[OpenClaw Session] 恢复前 provider_sources: {provider_sources}")
        # logger.info(f"[OpenClaw Session] 恢复时 original: {self._original_custom_headers}")
        
        for ps in provider_sources:
            ps_id = ps.get('id', '')
            if ps_id in self._original_custom_headers:
                ps['custom_headers'] = self._original_custom_headers[ps_id].copy()
        
        # logger.info(f"[OpenClaw Session] 恢复后 provider_sources: {provider_sources}")
    
    async def terminate(self):
        """插件卸载时调用"""
        pass