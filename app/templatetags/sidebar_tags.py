from django import template
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum
from app.models import Tag, User, Question, Answer, QuestionLike, AnswerLike

register = template.Library()

@register.inclusion_tag('includes/popular_tags.html')
def popular_tags():
    tags = cache.get('popular_tags')
    if tags is None:
        three_months_ago = timezone.now() - timedelta(days=90)
        tags = Tag.objects.filter(
            questions__created_at__gte=three_months_ago
        ).annotate(
            questions_count=Count('questions')
        ).order_by('-questions_count')[:10]
        cache.set('popular_tags', list(tags), 3600)
    else:
        tags = list(tags)
    return {'tags': tags}

@register.inclusion_tag('includes/best_members.html')
def best_members():
    members = cache.get('best_members')
    if members is None:
        week_ago = timezone.now() - timedelta(days=7)
        
        question_scores = Question.objects.filter(
            created_at__gte=week_ago
        ).values('author').annotate(
            total_likes=Sum('question_likes__value')
        ).filter(total_likes__isnull=False)
        
        answer_scores = Answer.objects.filter(
            created_at__gte=week_ago
        ).values('author').annotate(
            total_likes=Sum('answer_likes__value')
        ).filter(total_likes__isnull=False)
        
        user_scores = {}
        for item in question_scores:
            user_id = item['author']
            user_scores[user_id] = user_scores.get(user_id, 0) + (item['total_likes'] or 0)
        
        for item in answer_scores:
            user_id = item['author']
            user_scores[user_id] = user_scores.get(user_id, 0) + (item['total_likes'] or 0)
        
        sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        user_ids = [uid for uid, _ in sorted_users]
        members = User.objects.filter(id__in=user_ids).select_related('profile')
        cache.set('best_members', list(members), 3600)
    else:
        members = list(members)
    return {'members': members}
