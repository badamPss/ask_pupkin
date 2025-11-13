from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest
from .models import Question, Tag
from .utils import paginate

def index(request: HttpRequest):
    qs = Question.objects.new().select_related("author").prefetch_related("tags")
    page = paginate(qs, request, per_page=10)
    return render(request, 'index.html', {'page': page})

def hot(request: HttpRequest):
    qs = Question.objects.hot().select_related("author").prefetch_related("tags")
    page = paginate(qs, request, per_page=10)
    return render(request, 'index.html', {'page': page, 'hot': True})

def tag(request: HttpRequest, slug: str):
    get_object_or_404(Tag, slug=slug)
    qs = Question.objects.tagged(slug).select_related("author").prefetch_related("tags")
    page = paginate(qs, request, per_page=10)
    return render(request, 'tag.html', {'page': page, 'tag': slug})

def question(request: HttpRequest, qid: int):
    q = get_object_or_404(Question.objects.select_related("author").prefetch_related("tags"), pk=qid)
    answers = q.answers.select_related("author").all()
    return render(request, 'question.html', {'question': q, 'answers': answers})

def ask(request: HttpRequest):
    return render(request, 'ask.html')

def login_view(request: HttpRequest):
    return render(request, 'login.html')

def signup_view(request: HttpRequest):
    return render(request, 'signup.html')

def settings_view(request: HttpRequest):
    return render(request, 'settings.html')
