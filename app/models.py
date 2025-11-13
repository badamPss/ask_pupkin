from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    nickname = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return self.nickname or self.user.username

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class QuestionQuerySet(models.QuerySet):
    def with_counts(self):
        return self.annotate(answers_count=Count("answers"), likes_count=Count("question_likes"))

    def new(self):
        return self.with_counts().order_by("-created_at", "-id")

    def hot(self):
        return self.with_counts().order_by("-likes_count", "-created_at")

    def tagged(self, slug):
        return self.with_counts().filter(tags__slug=slug).order_by("-created_at")

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, related_name="questions", blank=True)

    objects = QuestionQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("question", kwargs={"qid": self.pk})

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-is_correct", "-created_at", "-id"]

    def __str__(self):
        return f"Answer #{self.pk} to Q#{self.question_id}"

class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question_likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="question_likes")
    value = models.SmallIntegerField(default=1)

    class Meta:
        unique_together = ("question", "user")

class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="answer_likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answer_likes")
    value = models.SmallIntegerField(default=1)

    class Meta:
        unique_together = ("answer", "user")
