from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum
from app.models import Tag, User, Question, Answer, QuestionLike, AnswerLike

class Command(BaseCommand):
    help = 'Update cache for popular tags and best members'

    def handle(self, *args, **options):
        three_months_ago = timezone.now() - timedelta(days=90)
        tags = Tag.objects.filter(
            questions__created_at__gte=three_months_ago
        ).annotate(
            questions_count=Count('questions')
        ).order_by('-questions_count')[:10]
        cache.set('popular_tags', list(tags), 3600)
        self.stdout.write(self.style.SUCCESS(f'Updated popular_tags cache: {len(tags)} tags'))
        
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
        self.stdout.write(self.style.SUCCESS(f'Updated best_members cache: {len(members)} members'))

