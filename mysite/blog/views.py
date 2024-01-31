from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
# import form 
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
# Create your views here.
from django.views.decorators.http import require_POST
#class based views
class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

# functional way of creating views
# def post_list(request):
#     posts = Post.published.all()
#     paginator = Paginator(object_list=posts, per_page=3)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.publish.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404('No post found!')
    # return render(request, 'blog/post/detail.html', {'post':post})

    # model manager have support for this method which does 
    # the same thing as above code
    post = get_object_or_404(Post,
                             status = Post.Status.PUBLISHED,
                             slug = post,
                             publish__year = year,
                             publish__month = month,
                             publish__day = day
                             )
    # list of active comments for the post
    comments = post.comments.filter(active=True)
    # form for users to comment
    form  = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post, 
                                                     'comments': comments,
                                                      'form': form })


def post_share(request, post_id):
    post = get_object_or_404(Post, id = post_id, status = Post.Status.PUBLISHED)
    sent = False
    if request.method == "POST":
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #form fields passed validation
            cd = form.cleaned_data
            # send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you to read {post.title}"
            message = f"Read {post.title} at {post_url} \n\n{cd['name']} comments {cd['comments']}"
            send_mail(subject, message,'a@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id = post_id, status = Post.Status.PUBLISHED)
    comment = None

    #a comment that was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a comment obj without saving it to db
        comment = form.save(commit=False)
        # assign the post to the comment object
        comment.post = post
        # save the comment obj
        comment.save()
    return render(request, 'blog/post/comment.html', {
        'post': post, 
        'form': form, 
        'comment':comment
        })