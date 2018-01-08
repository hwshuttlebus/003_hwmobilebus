from werobot import WeRoBot

'''
myrobot = WeRoBot(token='hwshuttlebus')
myrobot.config["APP_ID"] = "wxc13fbfc1f37dc954"
myrobot.config["APP_SECRET"] = "0eb22811085cf2930becaefb91264f3d"

client = myrobot.client

client.create_menu({
    "button":[
        {
            "type":"view",
            "name":"进入班车系统",
            "url":"http://44c6706d.ngrok.io"
        },
        {
            "name":"ebus",
            "sub_button":[
                {
                    "type":"view",
                    "name":"李冰路ebus",
                    "url":"https://www.baidu.com"
                },
                {
                    "type":"view",
                    "name":"环科路ebus",
                    "url":"https://c6f0b795.ngrok.io"
                }

            ]
        }
    ]
})

@myrobot.handler
def hello(message):
    return '欢迎使用Honeywell移动班车系统!'

'''