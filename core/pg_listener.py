import asyncio
import json
import asyncpg
import os
from core.websocket_manager import manager
from core.custom_logging import logger

log = logger.bind(service="pg_listener")

async def listen_to_task_updates():
    """Listens for PostgreSQL NOTIFY events and forwards them to WebSocket clients."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        log.error("DATABASE_URL_not_set")
        return

    while True:
        try:
            conn = await asyncpg.connect(database_url)
            log.info("connected_to_pg_listen")
            
            async def handle_notification(connection, pid, channel, payload):
                data = json.loads(payload)
                user_id = data.get("user_id")
                await manager.send_personal_message(data, user_id)
                log.info("notified_websocket", task_id=data.get("task_id"))

            await conn.add_listener("task_updates", handle_notification)
            
            # Keep the connection open
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            log.error("pg_listener_error", error=str(e))
            await asyncio.sleep(5) # Backoff
