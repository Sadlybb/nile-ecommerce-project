from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Count, Avg

from taggit.models import Tag

from . models import Vendor, Category, Product, Review
from . forms import ReviewForm


def homepage(request):
    popular_products = Product.objects.prefetch_related("images") \
        .select_related('category') \
        .select_related("vendor") \
        .all() \
        .annotate(
            orders_count=Count('orders')
    ) \
        .filter(publish_status="P", is_featured=True) \
        .order_by("-orders_count")

    context = {
        "products": popular_products,
    }
    return render(request, 'store/homepage.html', context=context)


def product_list(request):
    all_products = Product.objects.prefetch_related("images") \
        .select_related('category') \
        .select_related("vendor") \
        .all() \
        .annotate(
            orders_count=Count('orders')) \
        .filter(publish_status="P") \
        .order_by("-orders_count")

    context = {
        "products": all_products,
    }
    return render(request, 'store/product_list.html', context=context)


def category_list(request):
    categories = Category.objects \
        .prefetch_related('products') \
        .all() \
        .annotate(
            published_product_count=Count('products', filter=Q(
                products__publish_status='P'))
        )

    context = {
        "categories": categories
    }
    return render(request, 'store/category_list.html', context=context)


def category_product_list(request, pk):
    category = Category.objects.get(pk=pk)
    products_in_category = Product.objects.prefetch_related("images") \
        .select_related('category') \
        .select_related("vendor") \
        .all() \
        .annotate(
            orders_count=Count('orders')
    ) \
        .filter(publish_status="P", category=category) \
        .order_by("-orders_count")

    context = {
        "category": category,
        "products": products_in_category,
    }
    return render(request, 'store/category_product_list.html', context=context)


def product_detail(request, pk):
    product = Product.objects \
        .prefetch_related('images') \
        .prefetch_related('reviews') \
        .get(pk=pk)

    related_products = Product.objects \
        .prefetch_related('images') \
        .filter(category=product.category)


#  Reviews-----------
    reviews = Review.objects.select_related(
        'user').select_related('product').filter(product=product).order_by('-id')

    try:
        review_rating_detail = reviews.aggregate(
            avg_rating=Avg('rating'), count=Count('rating'))
        review_rating_detail['avg_percent'] = review_rating_detail['avg_rating'] / 5 * 100

        for i in range(1, 6):
            review_rating_detail[f"{i}star_percent"] = \
                reviews.filter(rating=i).aggregate(count=Count('rating'))['count'] \
                / review_rating_detail['count'] * 100
    except TypeError:
        review_rating_detail = {
            'avg_rating': 0,
            'avg_percent': 0,
            '1star_percent': 0,
            '2star_percent': 0,
            '3star_percent': 0,
            '4star_percent': 0,
            '5star_percent': 0,
        }

# Review Form ----------------------

    review_form = ReviewForm()

    context = {
        "product": product,
        "reviews": reviews,
        "related_products": related_products,
        'review_rating_detail': review_rating_detail,
        'review_form': review_form,

    }

    return render(request, "store/product_detail.html", context=context)


def vendor_list(request):

    vendors = Vendor.objects \
        .prefetch_related('products') \
        .prefetch_related('user__addresses') \
        .annotate(published_product_count=Count('products', filter=Q(products__publish_status='P'))) \
        .all()

    context = {
        'vendors': vendors
    }

    return render(request, 'store/vendor_list.html', context=context)


def vendor_detail(request, pk):
    vendor = Vendor.objects.get(pk=pk)
    products_in_vendor = Product.objects.prefetch_related("images") \
        .select_related('category') \
        .select_related("vendor") \
        .all() \
        .annotate(
            orders_count=Count('orders')
    ) \
        .filter(publish_status="P", vendor=vendor) \
        .order_by("-orders_count")

    context = {
        "vendor": vendor,
        "products": products_in_vendor,
    }
    return render(request, 'store/vendor_detail.html', context=context)


def tag_product_list(request, tag_slug=None):
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = Product.objects \
            .filter(publish_status="P") \
            .filter(tags__in=[tag]) \
            .order_by("-id")

    context = {
        'products': products,
        'tag': tag,
    }

    return render(request, 'store/tag_product_list.html', context=context)


def ajax_add_review(request, pk):
    product = Product.objects.get(pk=pk)
    user = request.user

    review = Review.objects.create(
        user=user,
        product=product,
        title=request.POST['title'],
        description=request.POST['description'],
        rating=request.POST['rating'],
    )

    context = {
        'user': user.username,
        'title': request.POST['title'],
        'description': request.POST['description'],
        'rating': request.POST['rating'],
    }

    avg_rating = Review.objects.filter(
        product=product).aggregate(rating=Avg('rating'))
    product.rating = int(avg_rating['rating'])
    product.save()
    return JsonResponse(
        {
            'bool': True,
            'context': context,
            'avg_rating': avg_rating,
        }
    )
