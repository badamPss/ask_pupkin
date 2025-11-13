import random, string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from django.db import transaction

def rand_word(n=8):
    return ''.join(random.choices(string.ascii_lowercase, k=n))

class Command(BaseCommand):
    help = "Fill database with test data. Usage: python manage.py fill_db [ratio]"

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, nargs='?', default=10000,
                            help='Base ratio: users=ratio; questions=ratio*10; answers=ratio*100; tags=ratio; likes=ratio*200')

    @transaction.atomic
    def handle(self, *args, **opts):
        ratio = opts['ratio']
        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"Filling DB: users={num_users}, questions={num_questions}, answers={num_answers}, tags={num_tags}, likes={num_likes}"
        ))

        existing_users = User.objects.count()
        users_to_create = max(0, num_users - existing_users)
        users = [User(username=f"user_{rand_word(6)}_{i}", email=f"user_{i}@example.com")
                 for i in range(users_to_create)]
        if users:
            User.objects.bulk_create(users, batch_size=1000)
        users_qs = list(User.objects.all())

        need_profiles = set(u.id for u in users_qs) - set(Profile.objects.values_list("user_id", flat=True))
        if need_profiles:
            Profile.objects.bulk_create([Profile(user_id=uid, nickname=f"nick_{uid}") for uid in need_profiles],
                                        batch_size=1000)

        existing_tags = Tag.objects.count()
        tags_to_create = max(0, num_tags - existing_tags)
        # тут просто создаю какие то рандомные
        if tags_to_create:
            Tag.objects.bulk_create(
                [Tag(name=f"tag_{rand_word(5)}_{i}", slug=f"tag_{rand_word(5)}_{i}")
                 for i in range(tags_to_create)],
                batch_size=1000
            )
        # красивые теги для сайдбара добавил
        base_tag_slugs = ["python", "mysql", "django", "firefox", "technopark", "bender", "black-jack"]
        for slug in base_tag_slugs:
            Tag.objects.get_or_create(slug=slug, defaults={"name": slug})
        tags_qs = list(Tag.objects.all()) or [Tag.objects.create(name="general", slug="general")]

        existing_q = Question.objects.count()
        to_create_q = max(0, num_questions - existing_q)
        questions = []
        for i in range(to_create_q):
            u = random.choice(users_qs)
            questions.append(Question(author=u, title=f"How to build a moon park ? #{existing_q + i + 1}",
                                      text="Guys, i have trouble with a moon park. Can't find the black-jack..."))
        if questions:
            Question.objects.bulk_create(questions, batch_size=1000)
        questions_qs = list(Question.objects.all())

        through = Question.tags.through
        links = []

        visible_tags = [t for t in tags_qs if t.slug in ["python", "mysql", "django", "firefox", "technopark", "bender", "black-jack"]]
        src_tags = visible_tags or tags_qs
        for q in questions_qs:
            for t in random.sample(src_tags, min(len(src_tags), random.randint(1, 3))):
                links.append(through(question_id=q.id, tag_id=t.id))
        if links:
            through.objects.bulk_create(links, batch_size=5000)

        existing_a = Answer.objects.count()
        to_create_a = max(0, num_answers - existing_a)
        answers = []
        for i in range(to_create_a):
            q = random.choice(questions_qs)
            u = random.choice(users_qs)
            answers.append(Answer(question=q, author=u, text=f"Answer text {i} ...", is_correct=False))
        if answers:
            Answer.objects.bulk_create(answers, batch_size=2000)
        answers_qs = list(Answer.objects.all())

        q_target = num_likes // 2
        a_target = num_likes - q_target

        seen_q = set()
        q_rows = []
        for _ in range(q_target):
            q = random.choice(questions_qs)
            u = random.choice(users_qs)
            key = (q.id, u.id)
            if key in seen_q: continue
            seen_q.add(key)
            q_rows.append(QuestionLike(question_id=q.id, user_id=u.id, value=1))
        if q_rows:
            QuestionLike.objects.bulk_create(q_rows, batch_size=5000, ignore_conflicts=True)

        seen_a = set()
        a_rows = []
        for _ in range(a_target):
            a = random.choice(answers_qs)
            u = random.choice(users_qs)
            key = (a.id, u.id)
            if key in seen_a: continue
            seen_a.add(key)
            a_rows.append(AnswerLike(answer_id=a.id, user_id=u.id, value=1))
        if a_rows:
            AnswerLike.objects.bulk_create(a_rows, batch_size=5000, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("Done!"))
