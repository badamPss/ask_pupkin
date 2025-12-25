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
]
