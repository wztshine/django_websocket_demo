# Django webSocket

源代码：https://github.com/wztshine/django_websocket_demo

源码有三个分支，分别对应：简单的聊天室，channel layer，聊天室

**参考自：**

https://www.cnblogs.com/wupeiqi/articles/9593858.html

https://www.bilibili.com/video/BV1aM4y137Qu?p=10&spm_id_from=pageDriver

## 配置

- 安装第三方库

```shell
pip install channels~=3.0.5
pip install django
```

> channels 4.x 之后版本都不带 daphne 服务器了，因此要么使用 3.x 版本，要么指定 `pip install -U channels["daphne"]`

- 创建项目

命令行输入：

```shell
django-admin startproject ws_channel  # ws_channel 是项目名，会在当前路径下出现这样一个文件夹
```

- 进入项目文件夹，修改 `ws_channel/settings.py`

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',  # 这里修改了：添加 channels 模块
]

# ws_channel 是当前 settings.py 文件所在的文件夹，即 python 的包名；asgi 是包下的 asgi.py 模块，它支持异步和 websockt
ASGI_APPLICATION = "ws_channel.asgi.application"
```

> Django 3.0 以上版本，创建项目时会自动生成一个 asgi.py 文件， 和 settings.py 同级目录。

- 修改 `ws_channel/asgi.py`（如果你用的django不是3.0以上版本，自己手动创建这个文件）

```python
"""
ASGI config for ws_channel project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from . import routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ws_channel.settings')

# application = get_asgi_application()
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # 自动处理 http 请求
    'websocket': URLRouter(routing.websocket_urlPatterns),  # 使用自定义的路由系统，来处理 websocket 连接
})
```

- 创建编写 `ws_channel/routing.py` (settings.py 同级目录下)

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from app01 import consumers


websocket_urlPatterns = [
    re_path(r"", consumers.ChatConsumer.as_asgi()),  # 匹配路由
]
```

- 新建一个 app01 的应用，并在应用下编写 consumers.py

1. 在你当前的**工程目录**下，运行cmd命令：

```python
django-admin startapp app01  # 创建一个叫 app01 的应用
```

2. 编写 `app01/consumers.py`

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer


class ChatConsumer(WebsocketConsumer):

    def websocket_connect(self, message):
        """这个函数是用来建立连接的。当客户端发起连接时，服务端会自动触发这个函数"""
        print('开始握手')
        self.accept()  # 接受连接

    def websocket_receive(self, message):
        """客户端发来消息时，服务端自动调用这个方法接受消息"""
        print('接收到消息', message)
        self.send(text_data='收到了')  # send 方法可以发送消息

    def websocket_disconnect(self, message):
        """
        服务端主动调用 self.close() 时，或者客户端调用 close() 方法来关闭连接时，服务端都会自动运行这个方法，关闭连接
        :param message:
        :return:
        """
        print('客户端断开连接了')
        raise StopConsumer()

```

## 简单的聊天室

在上面的前提下，在 `ws_channel/settings.py` 中注册 app01

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app01.apps.App01Config',  # 注册 app01 
    'channels',
]
```

在 `ws_channel/urls.py` 中添加路由：

```python
from django.contrib import admin
from django.urls import path

from app01 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),  # 新路由
]
```

在 `app01/views.py` 中编写视图：

```python
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'index.html')
```

在 app01 目录下新建**文件夹**：`templates` ，并编写 `index.html`:

`app01/templates/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<style>
    .message{
        width: 100%;
        height: 300px;
        border: 1px solid #dddddd;
    }
</style>
<body>
    <div class="message" id="message"></div>

    <div>
        <input type="text" id="txt">
        <!-- 添加了 onclick 事件 -->
        <input type="button" value="send" onclick="sendMessage()">
        <input type="button" value="close" onclick="ws_close()">
    </div>



    <script>
        // 创建 WebSocket 对象, 尝试握手连接
        socket = new WebSocket("ws://127.0.0.1:8000")

        // onopen 函数会在 websocket 和服务端建立连接成功后，自动调用执行
        socket.onopen = function (event){
            let tag = document.createElement("div")
            tag.innerText = '[连接成功]'
            document.getElementById('message').append(tag)
        }

        // onmessage 会在 websocket 接收到服务端的消息后，自动调用执行
        socket.onmessage = function (event){
            let tag = document.createElement("div")
            tag.innerText = event.data
            document.getElementById('message').append(tag)
        }

        // onclose 会在服务端主动发起断开时，自动调用执行
        socket.onclose = function (event){
            let tag = document.createElement("div")
            tag.innerText = '[服务端断开]'
            document.getElementById('message').append(tag)

        }

        function ws_close(){
            socket.close()  // 客户端主动关闭 websocket 连接
        }
		
        // 点击按钮触发
        function sendMessage(){
            let content = document.getElementById('txt').value
            socket.send(content)  // 客户端向后端发消息
        }

    </script>
</body>
</html>
```

修改 `app01/consumers.py`:

```python
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
            # 触发异常，就不会执行 websocket_disconnect() 方法了；如果不触发下面的异常，服务端主动调用 close() 后还会继续执行 websocket_disconnect()
            raise StopConsumer()

    def websocket_disconnect(self, message):
        """
        服务端主动调用 self.close() 时，或者客户端调用 close() 方法来关闭连接时，服务端自动运行这个方法，来关闭连接
        :param message:
        :return:
        """
        print('客户端断开连接了')
        raise StopConsumer()
```

在项目目录下，命令行执行：

```shell
python manage.py runserver
```

打开浏览器，同时开两个窗口，都访问：`http://127.0.0.1:8000/index` 

你在任意一个窗口发送消息，另一个窗口同样能接收到



## channel layer

上面的 consumers.py 代码中，我们用 `clients = []` 来自定义了一个列表，来存放所有的客户端连接。

下面我们基于 channels 提供的 channel layer 来实现。

- settings.py 添加一个配置：

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",  # 使用内存来存储客户端连接
    }
}
```

- 可选项：还可以使用基于 redis 的 BACKEND，示例：

```python
# 首先安装 pip3 install channels-redis

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [('10.211.55.25', 6379)]
        },
    },
}


CHANNEL_LAYERS = {
    'default': {
    'BACKEND': 'channels_redis.core.RedisChannelLayer',
    'CONFIG': {"hosts": ["redis://10.211.55.25:6379/1"],},
    },
}
 

CHANNEL_LAYERS = {
    'default': {
    'BACKEND': 'channels_redis.core.RedisChannelLayer',
    'CONFIG': {"hosts": [('10.211.55.25', 6379)],},},
}
 

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://:password@10.211.55.25:6379/0"],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    },
}
```

- 修改 consumers.py 

```python
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

```

通过上面的代码，我们可以将客户端连接放在某个群组中，实现群发功能。

## 聊天室

修改 routing.py 文件：

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from app01 import consumers


websocket_urlPatterns = [
    # 通过 ws://127.0.0.1:8000/room/?num=群号 进入某个聊天室
    re_path(r"room/(?P<group_id>\w+)", consumers.ChatConsumer.as_asgi()),
]
```

修改 consumers.py 文件，使用 `group_id = self.scope["url_route"]["kwargs"].get("group_id")` 来获取群号：

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):

    def websocket_connect(self, message):
        self.accept()

        # 获取聊天室组名, self.scope['url_route'] 是固定写法。因为上文路由里面使用了分组，所以这里使用 ['kwargs'].get("分组名") 来匹配路由
        group_id = self.scope["url_route"]["kwargs"].get("group_id")

        async_to_sync(self.channel_layer.group_add)(group_id, self.channel_name)

    def websocket_receive(self, message):
        group_id = self.scope["url_route"]["kwargs"].get("group_id")
        async_to_sync(self.channel_layer.group_send)(group_id, {"type": "all_send", "message": message})

    def all_send(self, event):
        text = event['message']['text']
        self.send(text)

    def websocket_disconnect(self, message):
        group_id = self.scope["url_route"]["kwargs"].get("group_id")
        async_to_sync(self.channel_layer.group_discard)(group_id, self.channel_name)

        raise StopConsumer()

```

修改 app01/templates/index.html 中 `<script>` 标签中，url 也要修改：

```html
        // 创建 WebSocket 对象, 尝试握手连接
        socket = new WebSocket("ws://127.0.0.1:8000/room/{{ group_id }}")
```

> `{{ group_id }}` 是 django 模板渲染的标签。

修改 app01/views.py:

```python
from django.shortcuts import render


# Create your views here.

def index(request):
    group_id = request.GET.get("num")  # 通过 url 获取用户传递的聊天室的 id
    return render(request, 'index.html', {"group_id": group_id})  # 将聊天室 id 渲染给模板，会传递给模板的 socket = new WebSocket("ws://127.0.0.1:8000/room/{{ group_id }}") 处
```

浏览器开两个窗口访问：`http://127.0.0.1:8000/index/?num=111` 来进入聊天室 `111`， 这两个窗口之间的消息是互通的，别的聊天室不能看到这个聊天室的内容。



## 局域网部署

想要局域网内互相访问，需要进行如下设置：

settings.py

```python
ALLOWEN_HOSTS = ["*"]  # 允许所有主机连接
```

app01/templates/index.html

```html
socket = new WebSocket("ws://填写你主机的IP:8000")
```

运行服务：

```shell
python manage.py runserver 你主机的IP:8000
```

并且设置你主机的防火墙：入站规则和出站规则允许 8000 端口的 TCP 连接。

