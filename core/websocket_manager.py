from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
from core.custom_logging import logger


class ConnectionManager:
    def __init__(self) -> None:
        # Menyimpan koneksi berdasarkan user_id: { "user_id": [WebSocket, ...] }
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.log = logger.bind(service="websocket_manager")

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Menerima koneksi baru dan mendaftarkannya ke user_id tertentu."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        self.log.info("ws_connected", user_id=user_id)

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Menghapus koneksi yang terputus."""
        try:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            self.log.info("ws_disconnected", user_id=user_id)
        except ValueError:
            pass

    async def send_personal_message(self, message: dict, user_id: str) -> None:
        """Mengirim JSON payload ke semua tab/device milik user_id."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    self.disconnect(connection, user_id)


manager = ConnectionManager()
