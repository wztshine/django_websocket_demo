from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from app01 import consumers


websocket_urlPatterns = [
    re_path(r"", consumers.ChatConsumer.as_asgi()),
]