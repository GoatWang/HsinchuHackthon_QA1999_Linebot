from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser ##, WebhookHanlder
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from linebot.models import (
    MessageEvent, TextMessage,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate, ConfirmTemplate, CarouselTemplate,
    PostbackTemplateAction, MessageTemplateAction, URITemplateAction,
    CarouselColumn
)

from society.classifier import Classifier

# Create your views here.

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

# Define Receiver
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)



def _handle_text_msg(event):
    text = event.message.text

    if "A" in text:
        message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url='https://example.com/image.jpg',
                title='Menu',
                text='Please select',
                actions=[
                    PostbackTemplateAction(label='postback', text='postback text', data='action=buy&itemid=1'),
                    MessageTemplateAction(label='message', text=' '),
                    URITemplateAction(label='uri', uri='http://example.com/')
                ]
            )
        )
    
    
    
    
    elif "B" in text:
        message = TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text='Are you sure?',
                actions=[
                    PostbackTemplateAction(label='postback', text='postback text', data='action=buy&itemid=1'),
                    MessageTemplateAction(label='message', text='message text'
                    )
                ]
            )
        )




    else:    
        message = TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                olumns=[
                    CarouselColumn(
                        thumbnail_image_url='https://example.com/item1.jpg',
                        title='this is menu1',
                        text='description1',
                        actions=[
                            PostbackTemplateAction(label='postback1', text='postback text1',data='action=buy&itemid=1'),
                            MessageTemplateAction(label='message1', text='message text1'),
                            URITemplateAction(label='uri1', uri='http://example.com/1')
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://example.com/item2.jpg',
                        title='this is menu2',
                        text='description2',
                        actions=[
                            PostbackTemplateAction(label='postback2', text='postback text2', data='action=buy&itemid=2'),
                            MessageTemplateAction(label='message2', text='message text2'),
                            URITemplateAction(label='uri2', uri='http://example.com/2')
                        ]
                    )
                ]
            )
        )

    line_bot_api.reply_message(
        event.reply_token,
        message
    )











@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        
        # TODO: Handler when receiver Line Message
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    # clf = Classifier(event.message.text)
                    # cat = clf.predict_cat()
                    # relatedrows = clf.findsimilar()
                    # feedbackstring = clf.getfeedbackinfo(cat, relatedrows)
                    _handle_text_msg(event)

                    # line_bot_api.reply_message(
                    #     event.reply_token,
                    #     TextSendMessage(text=feedbackstring)
                    # )

        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@csrf_exempt
def webcallback(request, query):
    clf = Classifier(query)
    cat = clf.predict_cat()
    relatedrows = clf.findsimilar()
    feedbackstring = clf.getfeedbackinfo(cat, relatedrows)
    return HttpResponse(feedbackstring)

def index(request):
    return HttpResponse("Test")