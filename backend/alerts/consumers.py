import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from core.db import alerts_col, users_col
from bson.objectid import ObjectId
import jwt
from django.conf import settings
import asyncio

class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.alert_id = self.scope['url_route']['kwargs']['alert_id']
        self.room_group_name = f'location_{self.alert_id}'
        
        # Verify JWT Token present in query params
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        if not token:
            await self.close(code=4001)
            return
            
        try:
            # Requires access token validation
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            self.user_id = decoded.get('user_id')
        except jwt.ExpiredSignatureError:
            await self.close(code=4002)
            return
        except jwt.InvalidTokenError:
            await self.close(code=4003)
            return

        # Check if alert exists and is not resolved
        alert = alerts_col.find_one({"_id": ObjectId(self.alert_id)})
        if not alert or alert.get('status') == 'resolved':
            await self.close(code=4004)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Auto close the connection after 30 minutes (1800 seconds)
        asyncio.create_task(self.auto_close())

    async def auto_close(self):
        await asyncio.sleep(1800)
        await self.close(code=4005)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # We only accept messages from the victim broadcasting their location
        text_data_json = json.loads(text_data)
        lat = text_data_json.get('lat')
        lng = text_data_json.get('lng')

        if lat and lng:
            # Could update DB here, but to avoid huge throughput we only broadcast
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_message',
                    'lat': lat,
                    'lng': lng,
                    'user_id': self.user_id
                }
            )

    async def location_message(self, event):
        lat = event['lat']
        lng = event['lng']
        user_id = event['user_id']

        await self.send(text_data=json.dumps({
            'lat': lat,
            'lng': lng,
            'user_id': user_id
        }))
