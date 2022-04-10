#!/usr/bin/env python
# -*- coding:utf-8 -*-
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer

clients = []


class ChatConsumer(WebsocketConsumer):

    def websocket_connect(self, message):
        """这个函数是用来建立连接的。当客户端发起连接时，服务端会自动触发这个函数"""
        print("有人来了...")
        self.accept()  # 接受连接
        clients.append(self)  # 存储每个客户端连接

    def websocket_receive(self, message):
        """客户端发来消息时，服务端自动调用这个方法接受消息"""
        print('接收到消息', message)

        for client in clients:  # 遍历客户端，给每个客户端发送消息
            client.send(message['text'])  # send 方法可以发送消息

        if message['text'] == 'close':
            self.close()  # 可以关闭连接
            # 触发异常，不会继续执行 websocket_disconnect() 方法了；否则 close() 后还会继续执行 websocket_disconnect()
            raise StopConsumer()

    def websocket_disconnect(self, message):
        """
        服务端主动调用 self.close() 时，或者客户端调用 close() 方法来关闭连接时，服务端都会自动运行这个方法，来关闭连接
        :param message:
        :return:
        """
        print('客户端断开连接了')
        raise StopConsumer()
