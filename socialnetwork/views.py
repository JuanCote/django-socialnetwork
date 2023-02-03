import json

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from .forms import Login, Register, PostForm, Post
from .models import Post, Friends


def index(request):
    if request.user.is_authenticated:
        return redirect('home_page')

    hidden = True
    form_login = Login()
    form_register = Register()

    if request.method == 'POST' and 'Login' in request.POST:
        form_login = Login(request.POST)
        if form_login.is_valid():
            user_from_db = User.objects.filter(email=form_login.cleaned_data['email'])
            if user_from_db:
                username = user_from_db[0].username
                user = authenticate(username=username, password=form_login.cleaned_data['password'])
                if user is not None:
                    login(request, user)
                    return redirect('home_page')
                else:
                    form_login.add_error(None, 'Invalid password')
            else:
                form_login.add_error(None, 'Invalid email')
    elif request.method == 'POST' and 'Register' in request.POST:
        form_register = Register(request.POST)
        if form_register.is_valid():
            form_register.save()
            messages.success(request, 'Success registration')
            data = {'form_login': Login(), 'form_register': form_register, 'hidden': True, messages: messages}
            return render(request, 'index.html', context=data)
        else:
            hidden = False
    data = {'form_login': form_login, 'form_register': form_register, 'hidden': hidden}
    return render(request, 'index.html', context=data)


@login_required(login_url='index')
def home_page(request):
    user = request.user
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = Post(content=form.cleaned_data['content'], image=form.cleaned_data['image'], user=user)
            post.save()
            return redirect('home_page')
        else:
            print('not valid')
    else:
        posts = Post.objects.order_by('-created_at')
        data = {'form': form, 'posts': posts, 'user': user}
        return render(request, 'news.html', context=data)


@login_required(login_url='index')
def logout(request):
    django_logout(request)
    return redirect('index')


@login_required(login_url='index')
def friends_all(request):
    users = User.objects.select_related('profile').exclude(username=request.user)
    subscriptions_id = Friends.objects.filter(user1=request.user).values_list('user2', flat=True)
    subscriptions = User.objects.filter(username__in=subscriptions_id)
    data = {'users': users, 'current_user': request.user, 'subscriptions': subscriptions, 'page': 0}
    return render(request, 'friends_all.html', context=data)


@login_required(login_url='index')
def friends_subscriptions(request):
    subscriptions_id = Friends.objects.filter(user1=request.user).values_list('user2', flat=True)
    subscriptions = User.objects.filter(username__in=subscriptions_id)
    data = {'subscriptions': subscriptions, 'current_user': request.user, 'page': 2}
    return render(request, 'friends_subscriptions.html', context=data)


@login_required(login_url='index')
def friends_subscribers(request):
    subscribers_id = Friends.objects.filter(user2=request.user).values_list('user1', flat=True)
    subscriptions_id = Friends.objects.filter(user1=request.user).values_list('user2', flat=True)
    subscribers = User.objects.filter(username__in=subscribers_id)
    subscriptions = User.objects.filter(username__in=subscriptions_id)
    data = {'subscribers': subscribers, 'subscriptions': subscriptions, 'current_user': request.user, 'page': 1}
    return render(request, 'friends_subscribers.html', context=data)


def subscribe(request):
    data = json.loads(request.body)
    users = User.objects.filter(username__in=(data['user1'], data['user2']))
    if int(users[0].username) == data['user1']:
        print('shot')
        user1, user2 = users[0], users[1]
    else:
        user1, user2 = users[1], users[0]
    subscribe = Friends.objects.filter(user1=user1, user2=user2)
    if subscribe.exists():
        subscribe.delete()
    else:
        subscribe = Friends.objects.create(user1=user1, user2=user2)
        subscribe.save()
    return JsonResponse({'Nikita': 'viktor'})