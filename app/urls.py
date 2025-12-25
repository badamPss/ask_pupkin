from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<slug:slug>/', views.tag, name='tag'),
    path('question/<int:qid>/', views.question, name='question'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('ask/', views.ask, name='ask'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('settings/', views.profile_edit_view, name='settings'),
    path('ajax/question/<int:qid>/like/', views.question_like, name='question_like'),
    path('ajax/answer/<int:aid>/like/', views.answer_like, name='answer_like'),
    path('ajax/question/<int:qid>/answer/<int:aid>/correct/', views.mark_correct_answer, name='mark_correct_answer'),
    path('search/', views.search, name='search'),
    path('ajax/search/suggestions/', views.search_suggestions, name='search_suggestions'),
]
