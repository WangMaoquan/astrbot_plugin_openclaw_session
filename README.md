# astrbot_plugin_openclaw_session

OpenClaw Session 管理插件

## 功能

- 为每次 LLM 请求设置固定的 `x-openclaw-session-key`
- 自动获取当前 agent_id、user_id/group_id
- 群聊使用 group_id，私聊使用 user_id
- 实现每个用户/群独立的会话记忆

## session key 格式

```
agent:main:<agent_id>:<user_id/group_id>
```

例如：
- 私聊：`agent:main:main:123456`
- 群聊：`agent:main:main:987654321`

## 仓库

https://github.com/WangMaoquan/astrbot_plugin_openclaw_session