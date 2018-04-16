from werobot import WeRoBot

myrobot = WeRoBot(token='hwmobilebus')
myrobot.config["APP_ID"] = "wxd6ac78fadc53c8d5"
myrobot.config["APP_SECRET"] = "f831286ea21d818221c5df4f5247c98f"

client = myrobot.client

#@myrobot.text
#def articles(message):
#    return [
#        [
#            "title",
#            "description",
#            "img",
#            "url"
#        ],
#        [
#            "进入Mobilebus",
#            "Mobilebus",
#            "https://secure.gravatar.com/avatar/0024710771815ef9b74881ab21ba4173?s=420",
#            "http://mbus.honeywell.com.cn"
#        ]
#    ]
from werobot.replies import ArticlesReply, Article


@myrobot.handler
def reply(message):
    reply = ArticlesReply(content="HoneywellMobilebus",message=message)
    article = Article(
        title="Mobilebus",
        description="点击进入Honeywell移动班车系统",
        img="https://secure.gravatar.com/avatar/0024710771815ef9b74881ab21ba4173?s=420",
        url="http://mbus.honeywell.com.cn"
    )
    reply.add_article(article)
    return reply


'''
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
'''