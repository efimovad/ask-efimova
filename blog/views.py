from django.shortcuts import render
from django.utils import timezone
from .models import Post, Comment, Tag, UserProfile, MyUser
from django.shortcuts import render, get_object_or_404
from .forms import PostForm, CommentForm, TagForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth import login, get_user_model, logout
from django.http import HttpResponseRedirect
from .forms import UserCreationForm, UserLoginForm, UserForm, UserProfileForm
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator


def post_list(request):
    posts_list = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

    paginator = Paginator(posts_list, 3)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    tags = Tag.objects.all()
    users = MyUser.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts, 'tags': tags, 'users': users})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    posttags = post.tags.all()
    tags = Tag.objects.all()
    users = MyUser.objects.all()
    return render(request, 'blog/post_detail.html', {'post': post, 'tags': tags, 'posttags': posttags, 'users': users})


def posts_by_tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)

    posts_list = tag.post_set.all()
    paginator = Paginator(posts_list, 3)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    tags = Tag.objects.all()

    return render(request, 'blog/post_list.html', {'posts': posts, 'tags': tags})


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    tags = Tag.objects.all()
    users = MyUser.objects.all()
    return render(request, 'blog/post_edit.html', {'form': form, 'tags': tags, 'users': users})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    tags = Tag.objects.all()
    users = MyUser.objects.all()
    return render(request, 'blog/post_edit.html', {'form': form, 'tags': tags, 'users': users})


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    tags = Tag.objects.all()
    users = MyUser.objects.all()
    return render(request, 'blog/add_comment_to_post.html', {'form': form, 'tags': tags, 'users': users})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def profile_detail(request):
    user = request.user
    tags = Tag.objects.all()
    users = MyUser.objects.all()
    return render(request, 'blog/profile.html', {'user': user, 'tags': tags, 'users': users})


@login_required
def like_post(request):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    post.likes.add(request.user)
    return HttpResponseRedirect("/")

@login_required
def dislike_post(request):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    post.dislikes.add(request.user)
    return HttpResponseRedirect("/")


def login_view(request, *args, **kwargs):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        user_obj = form.cleaned_data.get('user_obj')
        login(request, user_obj)
        return HttpResponseRedirect("/")
    return render(request, "registration/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('/')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
@transaction.atomic
def update_profile(request):
    myuser = request.user
    profile = UserProfile.objects.get(user=myuser)
    picture = profile.picture

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=myuser)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            #messages.success(request, _('Your profile was successfully updated!'))
            return redirect('profile')
        #else:
            #messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=myuser)
        profile_form = UserProfileForm(instance=profile)

    tags = Tag.objects.all()
    users = MyUser.objects.all()
    return render(request, 'blog/profile.html', {
        'picture': picture,
        'user_form': user_form,
        'profile_form': profile_form,
        'tags': tags,
        'users': users
    })


@login_required
def upload_pic(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            m = ExampleModel.objects.get(pk=course_id)
            m.model_pic = form.cleaned_data['image']
            m.save()
            return HttpResponse('image upload success')
    return HttpResponseForbidden('allowed only via POST')


@login_required
def vote(request):
    if request.POST:
        form = VoteForm(request.user, request.POST)
        if form.is_valid():
            cdata = form.cleaned_data
            if cdata['obj_name'] == 'answer':
                try:
                    answer = Answer.objects.get(pk=cdata['obj_id'])
                except Answer.DoesNotExist:
                    return status_response(False, {'answer': 'Answer by this doesn\'t exist'})
                else:
                    form.save(answer)
            else:
                try:
                    question = Question.objects.get(pk=cdata['obj_id'])
                except Question.DoesNotExist:
                    return status_response(False, {'question': 'Question by this doesn\'t exist'})
                else:
                    form.save(question)

            return status_response(True, 'Vote successfully added')
        else:
            return status_response(False, form.errors)

