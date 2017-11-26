from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser ##, WebhookHanlder
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


from society.classifier import Classifier
clf = Classifier()

# Create your views here.

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

# Define Receiver
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

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
                    cat = clf.predict_cat(event.message.text)
                    contactInfo = clf.GetContactInfo(cat)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=contactInfo)
                    )


        return HttpResponse()
    else:
        return HttpResponseBadRequest()


def index(request):
    return HttpResponse("Test")