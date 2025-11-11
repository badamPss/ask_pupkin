from django.shortcuts import render
from django.http import HttpRequest
from .utils import paginate
def make_questions(n = 50):
    data=[] 
    for i in range(1, n + 1):
        data.append({'id':i,'title':f'How to build a moon park ? #{i}','text':"Guys, i have trouble with a moon park. Can't find th black-jack...",'answers_count':(i*3)%7,'tags':['black-jack','bender'] if i%2 else ['python','django'],'likes':(i%10)+1})
    return data

QUESTIONS = make_questions()
def index(request:HttpRequest):
    page = paginate(QUESTIONS, request, per_page=10)
    return render(request,'index.html',{'page':page})

def hot(request:HttpRequest):
    qs = sorted(QUESTIONS, key=lambda q:q['likes'], reverse=True)
    page = paginate(qs, request, per_page=10)
    return render(request,'index.html',{'page':page,'hot':True})

def tag(request:HttpRequest, slug:str):
    filtered = [q for q in QUESTIONS if slug in q['tags']]
    page = paginate(filtered, request, per_page=10)
    return render(request,'tag.html',{'page':page,'tag':slug})

def question(request:HttpRequest, qid:int):
    q = next((x for x in QUESTIONS if x['id']==qid), {'id':qid,'title':f'Question #{qid}','text':'Not found','tags':['bender']})
    answers=[{'text':'First of all I would like to thank you ... Russia is huge ...','correct':True,'likes':5},
             {'text':'Another answer sample text ...','correct':False,'likes':3}]
    return render(request,'question.html',{'question':q,'answers':answers})

def ask(request:HttpRequest): return render(request,'ask.html')

def login_view(request:HttpRequest): return render(request,'login.html')

def signup_view(request:HttpRequest): return render(request,'signup.html')

def settings_view(request:HttpRequest): return render(request,'settings.html')
