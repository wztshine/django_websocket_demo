from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from app01 import consumers


websocket_urlPatterns = [
    # 实现 ws://127.0.0.1:8000/room/群号
    re_path(r"room/(?P<group_id>\w+)", consumers.ChatConsumer.as_asgi()),
]