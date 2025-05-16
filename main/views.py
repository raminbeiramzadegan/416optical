from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count
from .models import Appointment, Contact, BlogPost, Category, Newsletter, Author
from django.template.loader import render_to_string
from django.http import JsonResponse

def home(request):
    return render(request, 'main/home.html')

def about_us(request):
    return render(request, 'main/about-us.html')

def services(request):
    return render(request, 'main/services.html')

def contact(request):
    if request.method == 'POST':
        try:
            contact = Contact(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                subject=request.POST.get('subject'),
                message=request.POST.get('message')
            )
            contact.save()
            return render(request, 'main/contact.html', {
                'success_message': 'Your message has been sent successfully!'
            })
        except Exception as e:
            return render(request, 'main/contact.html', {
                'error_message': f'Error sending message: {str(e)}',
                'form_data': request.POST
            })
    return render(request, 'main/contact.html')

def book_appointment(request):
    if request.method == 'POST':
        try:
            appointment = Appointment(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                service=request.POST.get('service'),
                date=request.POST.get('date'),
                message=request.POST.get('message', '')
            )
            appointment.save()
            return render(request, 'main/home.html', {
                'success_message': 'Your appointment has been booked successfully!',
                'scroll_to': 'booking'
            })
        except Exception as e:
            return render(request, 'main/home.html', {
                'error_message': f'Error booking appointment: {str(e)}',
                'scroll_to': 'booking'
            })
    else:
        return render(request, 'main/home.html')

def blog_list(request):
    featured_post = BlogPost.objects.filter(is_featured=True).first()
    
    # Get page number from request
    page = int(request.GET.get('page', 1))
    posts_per_page = 3
    offset = (page - 1) * posts_per_page
    
    search_query = request.GET.get('q')
    category_slug = request.GET.get('category')
    
    if search_query:
        posts = BlogPost.objects.filter(title__icontains=search_query) | BlogPost.objects.filter(content__icontains=search_query)
        featured_post = None
    elif category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = BlogPost.objects.filter(category=category)
    else:
        posts = BlogPost.objects.filter(is_featured=False)
    
    # Get total count for pagination
    total_posts = posts.count()
    
    posts = posts[offset:offset + posts_per_page]
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        
        html = render_to_string('main/includes/blog_cards.html', {'posts': posts})
        
        return JsonResponse({
            'html': html,
            'has_more': (offset + posts_per_page) < total_posts
        })
    
    categories = Category.objects.annotate(post_count=Count('blogpost'))
    
    context = {
        'featured_post': featured_post,
        'posts': posts,
        'categories': categories,
        'has_more': (offset + posts_per_page) < total_posts,
        'next_page': page + 1,
    }
    return render(request, 'main/blogs_list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    recent_posts = BlogPost.objects.exclude(id=post.id)[:3]
    categories = Category.objects.annotate(post_count=Count('blogpost'))
    
    context = {
        'post': post,
        'recent_posts': recent_posts,
        'categories': categories,
    }
    return render(request, 'main/blog_detail.html', context)

def blog_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = BlogPost.objects.filter(category=category)
    categories = Category.objects.annotate(post_count=Count('blogpost'))
    
    context = {
        'category': category,
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'main/blogs_list.html', context)

def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            Newsletter.objects.create(email=email)
            return redirect(request.META.get('HTTP_REFERER', 'main:blog_list') + '?success=subscribed')
        except Exception as e:
            return redirect(request.META.get('HTTP_REFERER', 'main:blog_list') + '?error=subscription')
    return redirect('main:blog_list')