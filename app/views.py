from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Question, Tag, Answer, Profile
from .utils import paginate
from .forms import LoginForm, SignUpForm, ProfileEditForm, AskQuestionForm, AnswerForm

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
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = q
            answer.author = request.user
            answer.save()
            return redirect(f"{reverse('question', kwargs={'qid': qid})}#answer-{answer.pk}")
    else:
        form = AnswerForm()
    
    return render(request, 'question.html', {
        'question': q,
        'answers': answers,
        'form': form
    })

@login_required
def ask(request: HttpRequest):
    if request.method == 'POST':
        form = AskQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question = form.save()
            return redirect(question.get_absolute_url())
    else:
        form = AskQuestionForm()
    
    return render(request, 'ask.html', {'form': form})

def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get('continue', None)
                if next_url:
                    if next_url.startswith('/') and not next_url.startswith('//'):
                        return redirect(next_url)
                return redirect('index')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def signup_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

def logout_view(request: HttpRequest):
    if request.method == 'POST':
        logout(request)
        referer = request.META.get('HTTP_REFERER')
        if referer:
            from urllib.parse import urlparse
            parsed = urlparse(referer)
            path = parsed.path
            protected_paths = ['/settings/', '/profile/edit/', '/ask/']
            if path not in protected_paths and path != '/logout/':
                return redirect(path)
        return redirect('index')
    return redirect('index')

@login_required
def profile_edit_view(request: HttpRequest):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен.')
            return redirect('profile_edit')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    
    return render(request, 'settings.html', {'form': form})
