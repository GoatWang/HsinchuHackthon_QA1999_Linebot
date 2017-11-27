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



def _handle_text_msg(event, relatedrows, contactinfo, feedbackstring):
    text = event.message.text
    questions = list(relatedrows['question'])
    answers = list(relatedrows['ans'])

    message = TemplateSendMessage(
        alt_text='請再傳送一次訊息!',
        template=ButtonsTemplate(
            title='您是否想問以下問題?',
            text= feedbackstring,
            # actions = [
            #     PostbackTemplateAction(label="1. " + questions[0][:5], text=answers[0][:200], data='buttonfeedback=True'),
            #     PostbackTemplateAction(label="2. " + questions[1][:5], text=answers[1][:200], data='buttonfeedback=True'),
            #     PostbackTemplateAction(label="3. " + questions[1][:5], text=answers[2][:200], data='buttonfeedback=True'),
            #     PostbackTemplateAction(label="皆不是以上問題!", text=contactinfo[:300], data='buttonfeedback=True')
            # ]
            actions=[
                PostbackTemplateAction(label="皆不是以上問題!", text=contactinfo[:300], data='buttonfeedback=True'),
                MessageTemplateAction(label='message', text='message text'),
                MessageTemplateAction(label='message', text='message text'),
                MessageTemplateAction(label='message', text='message text'),
                # PostbackTemplateAction(label='postback', text='postback text', data='action=buy&itemid=1'),
                # URITemplateAction(label='uri', uri='http://example.com/')
            ]
        )
    )
    
    
    
    
    # message = TemplateSendMessage(
    #     alt_text='Confirm template',
    #     template=ConfirmTemplate(
    #         text='Are you sure?',
    #         actions=[
    #             PostbackTemplateAction(label='postback', text='postback text', data='action=buy&itemid=1'),
    #             MessageTemplateAction(label='message', text='message text')
    #         ]
    #     )
    # )

    line_bot_api.reply_message(
        event.reply_token,
        message
    )











@csrf_exempt
def callback(request, buttonfeedback=False):
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
                    if not buttonfeedback:
                        clf = Classifier(event.message.text)
                        cat = clf.predict_cat()
                        contactinfo = clf.getcontactinfo(cat)
                        relatedrows = clf.findsimilar()
                        feedbackstring = clf.getfeedbackinfo(cat, relatedrows)
                        # line_bot_api.reply_message(
                        #     event.reply_token,
                        #     TextSendMessage(text=feedbackstring)
                        # )
                        
                        _handle_text_msg(event, relatedrows, contactinfo, feedbackstring)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@csrf_exempt
def webcallback(request, query):
    clf = Classifier(query)
    cat = clf.predict_cat()
    feedbackstring = clf.getcontactinfo(cat)
    relatedrows = clf.findsimilar()
    # feedbackstring = clf.getfeedbackinfo(cat, relatedrows)
    return HttpResponse(feedbackstring)

def index(request):
    return HttpResponse("Test")