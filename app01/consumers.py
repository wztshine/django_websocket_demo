#!/usr/bin/env python
# -*- coding:utf-8 -*-
from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):

    def websocket_connect(self, message):
        """这个函数是用来建立连接的。当客户端发起连接时，服务端会自动触发这个函数"""
        self.accept()
        # 自动将当前连接，添加到某个群组中。
        async_to_sync(self.channel_layer.group_add)("group_1", self.channel_name)

    def websocket_receive(self, message):
        """客户端发来消息时，服务端自动调用这个方法接受消息"""
        # 这样写只会单独给当前客户端发送消息
        self.send("你好")

        # 给 group_1 群组的所有人发送消息；会调用 "all_send" 方法来为每个人发送消息
        async_to_sync(self.channel_layer.group_send)("group_1", {"type": "all_send", "message": message})

    def all_send(self, event):
        text = event['message']['text']
        self.send(text)

    def websocket_disconnect(self, message):
        """
        服务端主动调用 self.close() 时，或者客户端调用 close() 方法来关闭连接时，服务端都会自动运行这个方法，来关闭连接
        :param message:
        :return:
        """
        # 将当前通道，从群组中删除。
        async_to_sync(self.channel_layer.group_discard)("group_1", self.channel_name)

        raise StopConsumer()
