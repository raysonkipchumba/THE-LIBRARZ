from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    chat,
    home,
    login_view,
    logout_view,
    paper_create,
    paper_detail,
    paper_list,
    project_create,
    project_detail,
    project_list,
    registered_users,
    search,
    signup_view,
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='myApp/password_reset.html',
        email_template_name='myApp/password_reset_email.html',
        success_url='password_reset_done',
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='myApp/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='myApp/password_reset_confirm.html',
        success_url='password_reset_complete',
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='myApp/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('logout/', logout_view, name='logout'),
    path('users/', registered_users, name='users'),
    path('chat/', chat, name='chat'),
    path('chat/<int:user_id>/', chat, name='chat_with'),
    path('projects/', project_list, name='project_list'),
    path('projects/new/', project_create, name='project_create'),
    path('projects/<int:pk>/', project_detail, name='project_detail'),
    path('library/', paper_list, name='paper_list'),
    path('library/upload/', paper_create, name='paper_create'),
    path('papers/<int:pk>/', paper_detail, name='paper_detail'),
    path('search/', search, name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
