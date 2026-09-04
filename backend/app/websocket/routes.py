from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models import Driver, EmergencyProvider, UserRole
from app.websocket.manager import manager
router=APIRouter()
@router.websocket('/ws')
async def websocket_endpoint(websocket:WebSocket):
    token=websocket.query_params.get('token')
    try:
        payload=decode_access_token(token or ''); user_id=payload.get('user_id')
        if not isinstance(user_id,int): raise JWTError()
    except JWTError: await websocket.close(code=1008); return
    if not await manager.connect(user_id,websocket): return
    try:
        while True:
            message=await websocket.receive_json()
            if message.get('type')=='heartbeat' and manager.heartbeat_due(user_id):
                with SessionLocal() as db:
                    if payload.get('role') == UserRole.DRIVER.value:
                        driver = db.query(Driver).filter(Driver.user_id == user_id).first()
                        if driver: driver.last_seen = datetime.now(timezone.utc); db.commit()
                    elif payload.get('role') == UserRole.EMERGENCY_PROVIDER.value:
                        provider = db.query(EmergencyProvider).filter(EmergencyProvider.user_id == user_id).first()
                        if provider: provider.last_seen = datetime.now(timezone.utc); db.commit()
            elif message.get('type')!='heartbeat': await websocket.send_json({'type':'ERROR','message':'Unsupported message'})
    except (WebSocketDisconnect,Exception): manager.disconnect(user_id,websocket)
