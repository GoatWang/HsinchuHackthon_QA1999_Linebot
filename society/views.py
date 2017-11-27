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

    actions = []
    for num, row in relatedrows.iterrows():
        actions.append(PostbackTemplateAction(label="1. " + row['question'][:7] + "...", text=row['ans'][:200], data='buttonfeedback=1'))
    actions.append(PostbackTemplateAction(label="皆不是以上問題!", text=contactinfo[:300], data='buttonfeedback=1'))

    message = TemplateSendMessage(
        alt_text='請再傳送一次訊息!',
        template=ButtonsTemplate(
            text= feedbackstring[:159],
            action =actions,
            # actions = [
            #     PostbackTemplateAction(label="1. " + questions[0][:7] + "...", text=answers[0][:200], data='buttonfeedback=1'),
            #     PostbackTemplateAction(label="2. " + questions[1][:7] + "...", text=answers[1][:200], data='buttonfeedback=1'),
            #     PostbackTemplateAction(label="3. " + questions[2][:7] + "...", text=answers[2][:200], data='buttonfeedback=1'),
            #     PostbackTemplateAction(label="皆不是以上問題!", text=contactinfo[:300], data='buttonfeedback=1')
            # ]
        )
    )
    
    line_bot_api.reply_message(
        event.reply_token,
        message
    )








@csrf_exempt
def callback(request):
    print(request)

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
                    clf = Classifier(event.message.text)
                    cat = clf.predict_cat()
                    contactinfo = clf.getcontactinfo(cat)
                    relatedrows = clf.findsimilar()
                    feedbackstring = clf.getfeedbackinfo(cat, relatedrows)
                    print(len(feedbackstring))
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
    print(len(relatedrows))
    for i, row in relatedrows.iterrows():
        question = row['question']
        print(question)

    return HttpResponse(feedbackstring)

def index(request):
    return HttpResponse("Test")