from django.db.models.query import QuerySet
from django.forms.fields import EmailField
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from .forms import CommentForm
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm
from django.views.generic import ListView
from taggit.models import Tag
from blog import models
from django.db.models import Count


def post_list(request,tag_slug = None ):
    posts = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = posts.filter(tags__in=[tag])


    return render(request, 'blog/post/list.html', context={
        "posts": posts,
        "tag": tag,
       
    })






def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
    status='published',
    publish__year=year,
    publish__month=month,
    publish__day=day)

    comments = post.comments.filter(active=True)

    comment_form = CommentForm()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_form.save()




    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    return render(request, 'blog/post/detail.html', context={
        "comment_form": comment_form,
        "comments": comments,
        "post": post,
        "similar_posts": similar_posts})






def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status = 'published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}" 
            message = f"Read {post.title} at {post_url}\n\n" f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'ngechamike26@gmail.com',
            [cd['to']])
            sent = True

    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', context= {"form": form,
                                                              "post": post,
                                                              "sent": sent})





