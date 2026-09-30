from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ChatMessageForm,
    CustomLoginForm,
    RegistrationForm,
    ResearchNoteForm,
    ResearchPaperForm,
    ResearchProjectForm,
)
from .models import ChatMessage, ResearchNote, ResearchPaper, ResearchProject, UserProfile


def touch_user_activity(request):
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.last_seen = timezone.now()
        profile.save(update_fields=['last_seen'])


def home(request):
    touch_user_activity(request)
    projects = ResearchProject.objects.all().order_by('-updated_at')[:5]
    papers = ResearchPaper.objects.select_related('project').order_by('-updated_at')[:5]
    notes = ResearchNote.objects.select_related('paper').order_by('-created_at')[:5]

    user_role = None
    if request.user.is_authenticated:
        user_role = getattr(request.user.profile, 'role', None)

    context = {
        'project_count': ResearchProject.objects.count(),
        'paper_count': ResearchPaper.objects.count(),
        'note_count': ResearchNote.objects.count(),
        'registered_users': User.objects.count(),
        'projects': projects,
        'papers': papers,
        'notes': notes,
        'user_role': user_role,
    }
    return render(request, 'myApp/home.html', context)


@login_required
def registered_users(request):
    touch_user_activity(request)
    users = User.objects.select_related('profile').order_by('-date_joined')
    role_counts = {
        'student': UserProfile.objects.filter(role='student').count(),
        'professor': UserProfile.objects.filter(role='professor').count(),
        'lab': UserProfile.objects.filter(role='lab').count(),
    }

    return render(request, 'myApp/users.html', {
        'users': users,
        'user_count': users.count(),
        'role_counts': role_counts,
    })


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('home')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'myApp/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = CustomLoginForm()

    return render(request, 'myApp/login.html', {'form': form})


def project_list(request):
    touch_user_activity(request)
    projects = ResearchProject.objects.annotate(paper_count=Count('papers')).all()
    return render(request, 'myApp/project_list.html', {'projects': projects})


def project_create(request):
    if request.method == 'POST':
        form = ResearchProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return redirect(project.get_absolute_url())
    else:
        form = ResearchProjectForm()

    return render(request, 'myApp/project_form.html', {'form': form, 'title': 'Create research project'})


def project_detail(request, pk):
    touch_user_activity(request)
    project = get_object_or_404(ResearchProject.objects.prefetch_related('papers'), pk=pk)
    return render(request, 'myApp/project_detail.html', {'project': project})


def paper_list(request):
    touch_user_activity(request)
    query = request.GET.get('q', '')
    papers = ResearchPaper.objects.select_related('project')

    if query:
        papers = papers.filter(
            Q(title__icontains=query) |
            Q(authors__icontains=query) |
            Q(keywords__icontains=query) |
            Q(abstract__icontains=query)
        )

    return render(request, 'myApp/paper_list.html', {'papers': papers, 'query': query})


def paper_create(request):
    if request.method == 'POST':
        form = ResearchPaperForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save()
            return redirect(paper.get_absolute_url())
    else:
        form = ResearchPaperForm()

    return render(request, 'myApp/paper_form.html', {'form': form, 'title': 'Add paper to library'})


def paper_detail(request, pk):
    touch_user_activity(request)
    paper = get_object_or_404(ResearchPaper.objects.select_related('project'), pk=pk)
    notes = paper.notes.all()

    if request.method == 'POST':
        form = ResearchNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.paper = paper
            note.save()
            return redirect('paper_detail', pk=paper.pk)
    else:
        form = ResearchNoteForm()

    return render(request, 'myApp/paper_detail.html', {'paper': paper, 'notes': notes, 'form': form})


@login_required
def chat(request, user_id=None):
    touch_user_activity(request)
    users = User.objects.exclude(id=request.user.id).select_related('profile').order_by('username')
    selected_user = None

    if user_id:
        selected_user = get_object_or_404(users, pk=user_id)
    elif users.exists():
        selected_user = users.first()

    messages = ChatMessage.objects.none()
    if selected_user:
        messages = ChatMessage.objects.filter(
            Q(sender=request.user, receiver=selected_user) |
            Q(sender=selected_user, receiver=request.user)
        ).order_by('created_at')

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if selected_user and form.is_valid():
            ChatMessage.objects.create(
                sender=request.user,
                receiver=selected_user,
                content=form.cleaned_data['content'],
            )
            return redirect('chat_with', user_id=selected_user.pk)
    else:
        form = ChatMessageForm()

    return render(request, 'myApp/chat.html', {
        'users': users,
        'selected_user': selected_user,
        'messages': messages,
        'form': form,
    })


def search(request):
    return paper_list(request)
