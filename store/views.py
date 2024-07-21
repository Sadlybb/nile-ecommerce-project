from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q, Count, Avg
from django.template.loader import render_to_string
from django.contrib import messages

from taggit.models import Tag

from . models import Vendor, Category, Product, Review
from . forms import ReviewForm

# --------------------------------------------------------------------------Home Page view-----------------------------------------------------------------


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

# --------------------------------------------------------------------------Categories-----------------------------------------------------------------


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
    selected_category = Category.objects.get(pk=pk)
    products_in_category = Product.objects.prefetch_related("images") \
        .select_related('category') \
        .select_related("vendor") \
        .all() \
        .annotate(
            orders_count=Count('orders')
    ) \
        .filter(publish_status="P", category=selected_category) \
        .order_by("-orders_count")

    context = {
        "selected_category": selected_category,
        "products": products_in_category,
    }
    return render(request, 'store/category_product_list.html', context=context)


# --------------------------------------------------------------------------Products-----------------------------------------------------------------
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


# --------------------------------------------------------------------------Vendors-----------------------------------------------------------------
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


# --------------------------------------------------------------------------Tag-----------------------------------------------------------------

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


# --------------------------------------------------------------------------Review-----------------------------------------------------------------
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


# --------------------------------------------------------------------------Search-----------------------------------------------------------------
def search_view(request):
    query = request.GET.get("query")

    products = Product.objects.filter(title__icontains=query)

    context = {
        'products': products,
        'query': query,
    }

    return render(request, 'store/search.html', context=context)


# --------------------------------------------------------------------------Filters-----------------------------------------------------------------
def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")
    products = Product.objects.filter(
        publish_status="P").order_by("-id").distinct()

    min_price = request.GET['min_price']
    max_price = request.GET['max_price']

    products = products.filter(discount_price__gte=min_price)
    products = products.filter(discount_price__lte=max_price)

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct()

    context = {
        'products': products
    }

    data = render_to_string("store/async/product_list.html", context=context)

    return JsonResponse({'data': data})


# --------------------------------------------------------------------------Cart-----------------------------------------------------------------
def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'quantity': request.GET['quantity'],
        'price': request.GET['price'],
        'image': request.GET['image'],
    }

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            print(cart_product[str(request.GET['id'])])
            cart_data[str(request.GET['id'])]['quantity'] = int(
                cart_product[str(request.GET['id'])]['quantity'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data

        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data

    else:
        request.session['cart_data_obj'] = cart_product

    return JsonResponse({"data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})


def cart_view(request):
    cart_total_amount = 0

    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            item['subtotal'] = int(item['quantity']) * float(item['price'])
            cart_total_amount += item['subtotal']

        context = {
            'cart_data': request.session['cart_data_obj'],
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount
        }

        return render(request, "store/cart.html", context=context)

    else:
        messages.warning(request, 'You have no item in cart.')
        return redirect('store:homepage')


def delete_item_from_cart(request):

    product_id = str(request.GET['id'])

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

            cart_total_amount = 0
            for product_id, item in request.session['cart_data_obj'].items():
                item['subtotal'] = int(item['quantity']) * float(item['price'])
                cart_total_amount += item['subtotal']
    context = {
        'cart_data': request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount
    }
    data = render_to_string("store/async/cart_list.html", context=context)

    return JsonResponse({"data": data, 'totalcartitems': len(request.session['cart_data_obj'])})


def update_cart(request):

    product_id = str(request.GET['id'])
    product_quantity = request.GET['quantity']

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['quantity'] = product_quantity
            request.session['cart_data_obj'] = cart_data

            cart_total_amount = 0
            for product_id, item in request.session['cart_data_obj'].items():
                item['subtotal'] = int(item['quantity']) * float(item['price'])
                cart_total_amount += item['subtotal']
    context = {
        'cart_data': request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount
    }
    data = render_to_string("store/async/cart_list.html", context=context)

    return JsonResponse({"data": data, 'totalcartitems': len(request.session['cart_data_obj'])})


# --------------------------------------------------------------------------About-----------------------------------------------------------------
def about_us(request):
    return render(request, 'store/about_us.html')
