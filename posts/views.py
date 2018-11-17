from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template

import sendgrid
import os
from sendgrid.helpers.mail import *
from django.http import *

from django.core.urlresolvers import reverse
from django.urls import reverse


from urllib.parse import quote_plus
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, ContactForm
from django.utils import timezone
from comments.models import Comment
from comments.forms import CommentForm


# Create your views here.
from .models import Post


def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = PostForm(request.POST or None, request.FILES or None)  #Request files or none
    if form.is_valid():
        instance = form.save(commit = False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
    }
    return render(request, "post_form.html",context)

def article(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(instance.content)
    initial_data = {
            "content_type": instance.get_content_type,
            "object_id": instance.id
    }
    form = CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid() and request.user.is_authenticated():
        c_type = form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        obj_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get('parent_id'))
        except:
            parent_id = None

        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count()== 1:
                parent_obj = parent_qs.first()
        new_comment, created = Comment.objects.get_or_create(
                                    user = request.user,
                                    content_type = content_type,
                                    object_id = obj_id,
                                    content = content_data,
                                    parent = parent_obj
                                    )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())
    comments = instance.comments #Comment.objects.filter_by_instance(instance) with the qs of the commentsManager
    context = {
        "title":instance.title,
        "instance": instance,
        "share_string": share_string,
        "comments":comments,
        "comment_form":form,
    }
    return render(request, "article.html",context)

def bloglist(request):
    today = timezone.now().date()
    queryset_list = Post.objects.active() #.order_by("-timestamp")
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()
    query = request.GET.get("q") #name of the input for the query search
    if query: #if search exists
        queryset_list= queryset_list.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)|
                Q(post_tagone__icontains=query)|
                Q(post_tagtwo__icontains=query)
                ).distinct()
    paginator = Paginator(queryset_list,4)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    context = {
            "object_list": queryset,
            "title":"List",
            "page_request_var":page_request_var,
            "today":today,
        }
    return render(request, "blog.html",context)

def home(request):
    today = timezone.now().date()
    queryset_list = Post.objects.active() #.order_by("-timestamp")
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()
    query = request.GET.get("q") #name of the input for the query search
    if query: #if search exists
        queryset_list= queryset_list.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
                ).distinct()
    paginator = Paginator(queryset_list,2)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    context = {
            "object_list": queryset,
            "title":"List",
            "page_request_var":page_request_var,
            "today":today,
        }
    if request.method == "POST":
        sendmail(request) #Here I call the function sendmail in order to have two views in the same url
        return redirect('posts:success')
    return render(request, "home.html", context)

def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug = slug)
    form = PostForm(request.POST or None, request.FILES or None, instance = instance) #It uses the create method, just adds the instance to update the article
    if form.is_valid():
        instance = form.save(commit = False)
        instance.save()
        messages.success(request, "Item Saved")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "title":instance.title,
        "instance": instance,
        "form": form,
    }
    return render(request, "post_form.html",context)

def post_delete(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug = slug)
    instance.delete()
    messages.success(request, "Successfully Deleted")
    return redirect("posts:home")
    
def sendmail(request):
    emailform = ContactForm(request.POST or None)
    if emailform.is_valid():
        name = emailform.cleaned_data.get("name")
        email = emailform.cleaned_data.get("email")
        message = emailform.cleaned_data.get("message")

        subject = "Blog contact form from: "+name
        from_email = settings.EMAIL_HOST_USER
        to_email = [from_email, "spacetimetraveler.blog@gmail.com"]
        contact_message = "%s: %s via %s"%(
                name,
                email,
                message)
        some_html_message = email + """
        <h2>A message from the blog!</h2>
        """+message 

        send_mail(subject,
                  message,
                  from_email,
                  to_email,
                  html_message = some_html_message,
                  fail_silently= True)

    context = {
        "emailform":emailform,
    }
    return render(request, "home.html", context)

def success_message(request):
    return render(request, "success_message.html")

    
    



