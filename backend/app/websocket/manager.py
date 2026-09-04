from collections import defaultdict
import asyncio
from datetime import datetime, timezone
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self): self.connections=defaultdict(set); self.loops={}; self.heartbeats={}
    async def connect(self,user_id:int,websocket:WebSocket):
        if len(self.connections[user_id])>=3: await websocket.close(code=1008); return False
        await websocket.accept(); self.connections[user_id].add(websocket); self.loops[websocket] = asyncio.get_running_loop(); return True
    def disconnect(self,user_id:int,websocket:WebSocket): self.connections[user_id].discard(websocket); self.loops.pop(websocket, None)
    def heartbeat_due(self,user_id:int) -> bool:
        now = datetime.now(timezone.utc)
        previous = self.heartbeats.get(user_id)
        if previous and (now - previous).total_seconds() < 60:
            return False
        self.heartbeats[user_id] = now
        return True
    async def send_to_user(self,user_id:int,message:dict):
        for ws in list(self.connections[user_id]):
            try: await ws.send_json(message)
            except Exception: self.disconnect(user_id,ws)
    def send_to_user_sync(self,user_id:int,message:dict):
        for ws in list(self.connections[user_id]):
            loop=self.loops.get(ws)
            if loop and loop.is_running(): loop.call_soon_threadsafe(asyncio.create_task,self._send(ws,user_id,message))
    async def _send(self,websocket:WebSocket,user_id:int,message:dict):
        try: await websocket.send_json(message)
        except Exception: self.disconnect(user_id,websocket)
manager=ConnectionManager()
