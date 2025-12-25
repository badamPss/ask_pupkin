from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count, Q
from django.core.cache import cache
from .models import Question, Tag, Answer, Profile, QuestionLike, AnswerLike
from .utils import paginate
from .forms import LoginForm, SignUpForm, ProfileEditForm, AskQuestionForm, AnswerForm
from .centrifugo import publish_to_centrifugo

def index(request: HttpRequest):
    qs = Question.objects.new().select_related("author", "author__profile").prefetch_related("tags")
    page = paginate(qs, request, per_page=10)
    
    questions_data = []
    for q in page.object_list:
        user_liked = None
        if request.user.is_authenticated:
            try:
                like = QuestionLike.objects.get(question=q, user=request.user)
                user_liked = like.value
            except QuestionLike.DoesNotExist:
                pass
        
        rating = QuestionLike.objects.filter(question=q).aggregate(total=Sum('value'))['total'] or 0
        questions_data.append({
            'question': q,
            'user_liked': user_liked,
            'rating': rating
        })
    
    return render(request, 'index.html', {
        'page': page,
        'questions_data': questions_data
    })

def hot(request: HttpRequest):
    qs = Question.objects.hot().select_related("author", "author__profile").prefetch_related("tags")
    page = paginate(qs, request, per_page=10)
    
    questions_data = []
    for q in page.object_list:
        user_liked = None
        if request.user.is_authenticated:
            try:
                like = QuestionLike.objects.get(question=q, user=request.user)
                user_liked = like.value
            except QuestionLike.DoesNotExist:
                pass
        
        rating = QuestionLike.objects.filter(question=q).aggregate(total=Sum('value'))['total'] or 0
        questions_data.append({
            'question': q,
            'user_liked': user_liked,
            'rating': rating
        })
    
    return render(request, 'index.html', {
        'page': page,
        'questions_data': questions_data
    })

def tag(request: HttpRequest, slug: str):
    tag_obj = get_object_or_404(Tag, slug=slug)
    qs = Question.objects.tagged(slug).select_related("author", "author__profile").prefetch_related("tags")
    page = paginate(qs, request, per_page=10)
    
    questions_data = []
    for q in page.object_list:
        user_liked = None
        if request.user.is_authenticated:
            try:
                like = QuestionLike.objects.get(question=q, user=request.user)
                user_liked = like.value
            except QuestionLike.DoesNotExist:
                pass
        
        rating = QuestionLike.objects.filter(question=q).aggregate(total=Sum('value'))['total'] or 0
        questions_data.append({
            'question': q,
            'user_liked': user_liked,
            'rating': rating
        })
    
    return render(request, 'tag.html', {
        'page': page,
        'tag_obj': tag_obj,
        'questions_data': questions_data
    })

def question(request: HttpRequest, qid: int):
    q = get_object_or_404(Question.objects.select_related("author", "author__profile").prefetch_related("tags"), pk=qid)
    answers = q.answers.select_related("author", "author__profile").all()
    
    user_liked_question = None
    if request.user.is_authenticated:
        try:
            like = QuestionLike.objects.get(question=q, user=request.user)
            user_liked_question = like.value
        except QuestionLike.DoesNotExist:
            pass
    
    question_rating = QuestionLike.objects.filter(question=q).aggregate(total=Sum('value'))['total'] or 0
    
    answers_data = []
    for answer in answers:
        user_liked = None
        if request.user.is_authenticated:
            try:
                like = AnswerLike.objects.get(answer=answer, user=request.user)
                user_liked = like.value
            except AnswerLike.DoesNotExist:
                pass
        
        answer_rating = AnswerLike.objects.filter(answer=answer).aggregate(total=Sum('value'))['total'] or 0
        answers_data.append({
            'answer': answer,
            'user_liked': user_liked,
            'rating': answer_rating
        })
    
    is_question_author = request.user.is_authenticated and q.author == request.user
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = q
            answer.author = request.user
            answer.save()
            
            channel = f"public:question_{qid}"
            answer_data = {
                'id': answer.pk,
                'text': answer.text,
                'author': {
                    'id': answer.author.pk,
                    'username': answer.author.username,
                    'nickname': getattr(answer.author.profile, 'nickname', None) or answer.author.username,
                    'avatar': answer.author.profile.avatar.url if hasattr(answer.author, 'profile') and answer.author.profile.avatar else None
                },
                'created_at': answer.created_at.isoformat(),
                'is_correct': answer.is_correct,
                'rating': 0
            }
            publish_to_centrifugo(channel, answer_data)
            
            return redirect(f"{reverse('question', kwargs={'qid': qid})}#answer-{answer.pk}")
    else:
        form = AnswerForm()
    
    from django.conf import settings
    return render(request, 'question.html', {
        'question': q,
        'answers_data': answers_data,
        'form': form,
        'user_liked_question': user_liked_question,
        'question_rating': question_rating,
        'is_question_author': is_question_author,
        'CENTRIFUGO_WS_URL': settings.CENTRIFUGO_WS_URL
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
            if user is not None:
                login(request, user)
                next_url = request.GET.get('continue', '/')
                return redirect(next_url)
            else:
                form.add_error(None, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def signup_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

def logout_view(request: HttpRequest):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def profile_edit_view(request: HttpRequest):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('settings')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'settings.html', {'form': form})

@require_http_methods(["POST"])
@login_required
def question_like(request: HttpRequest, qid: int):
    question = get_object_or_404(Question, pk=qid)
    action = request.POST.get('action')
    
    if action not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    value = 1 if action == 'like' else -1
    
    like, created = QuestionLike.objects.get_or_create(
        question=question,
        user=request.user,
        defaults={'value': value}
    )
    
    if not created:
        if like.value == value:
            like.delete()
            value = 0
        else:
            like.value = value
            like.save()
    
    rating = QuestionLike.objects.filter(question=question).aggregate(total=Sum('value'))['total'] or 0
    
    return JsonResponse({
        'rating': rating,
        'user_liked': value if value != 0 else None
    })

@require_http_methods(["POST"])
@login_required
def answer_like(request: HttpRequest, aid: int):
    answer = get_object_or_404(Answer, pk=aid)
    action = request.POST.get('action')
    
    if action not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    value = 1 if action == 'like' else -1
    
    like, created = AnswerLike.objects.get_or_create(
        answer=answer,
        user=request.user,
        defaults={'value': value}
    )
    
    if not created:
        if like.value == value:
            like.delete()
            value = 0
        else:
            like.value = value
            like.save()
    
    rating = AnswerLike.objects.filter(answer=answer).aggregate(total=Sum('value'))['total'] or 0
    
    return JsonResponse({
        'rating': rating,
        'user_liked': value if value != 0 else None
    })

@require_http_methods(["POST"])
@login_required
def mark_correct_answer(request: HttpRequest, qid: int, aid: int):
    question = get_object_or_404(Question, pk=qid)
    
    if question.author != request.user:
        return JsonResponse({'error': 'Only question author can mark correct answer'}, status=403)
    
    answer = get_object_or_404(Answer, pk=aid, question=question)
    answer.is_correct = not answer.is_correct
    answer.save()
    
    return JsonResponse({
        'is_correct': answer.is_correct
    })

def search(request: HttpRequest):
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('index')
    
    questions = Question.objects.filter(
        Q(title__icontains=query) | Q(text__icontains=query)
    ).select_related("author", "author__profile").prefetch_related("tags")
    
    page = paginate(questions, request, per_page=10)
    
    questions_data = []
    for q in page.object_list:
        user_liked = None
        if request.user.is_authenticated:
            try:
                like = QuestionLike.objects.get(question=q, user=request.user)
                user_liked = like.value
            except QuestionLike.DoesNotExist:
                pass
        
        rating = QuestionLike.objects.filter(question=q).aggregate(total=Sum('value'))['total'] or 0
        questions_data.append({
            'question': q,
            'user_liked': user_liked,
            'rating': rating
        })
    
    return render(request, 'index.html', {
        'page': page,
        'questions_data': questions_data,
        'search_query': query
    })

def search_suggestions(request: HttpRequest):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    questions = Question.objects.filter(
        Q(title__icontains=query) | Q(text__icontains=query)
    )[:5]
    
    results = [{
        'title': q.title,
        'url': q.get_absolute_url()
    } for q in questions]
    
    return JsonResponse({'results': results})
