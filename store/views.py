import requests
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q, Count, Avg, F, Sum
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.conf import settings

from taggit.models import Tag

from . models import Address, Vendor, Category, Product, Review, Cart, CartItem, Customer, Order, OrderItem, Shipment, Wishlist
from . forms import ReviewForm, AddressForm


if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'


ZP_API_REQUEST = \
    f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"

ZP_API_VERIFY = \
    f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"

ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"


# --------------------------------------------------------------------------About-----------------------------------------------------------------
def about_us(request):
    return render(request, 'store/about_us.html')


# --------------------------------------------------------------------------Home Page view-----------------------------------------------------------------


def homepage(request):
    popular_products = Product.objects.prefetch_related("images") \
        .select_related('category') \
        .select_related("vendor") \
        .filter(is_active=True, publish_status="P", is_featured=True) \
        .annotate(
            orders_count=Count('orders')
    ) \
        .order_by("-orders_count")

    context = {
        "products": popular_products,
    }
    return render(request, 'store/homepage.html', context=context)

# --------------------------------------------------------------------------Categories-----------------------------------------------------------------


def category_list(request):
    categories = Category.objects \
        .annotate(
            published_product_count=Count('products', filter=Q(products__is_active=True,
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
        .filter(is_active=True, publish_status="P", category=selected_category) \
        .annotate(
            orders_count=Count('orders')
    ) \
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
        .filter(is_active=True, publish_status="P") \
        .annotate(
            orders_count=Count('orders')) \
        .order_by("-orders_count")

    context = {
        "products": all_products,
    }
    return render(request, 'store/product_list.html', context=context)


def product_detail(request, pk):
    product = Product.objects \
        .prefetch_related('images') \
        .prefetch_related('reviews') \
        .select_related('vendor') \
        .select_related('vendor__user') \
        .prefetch_related('vendor__user__addresses') \
        .get(pk=pk)

    related_products = Product.objects \
        .prefetch_related('images') \
        .filter(category=product.category)[:5]

    #  Reviews-----------

    # Query for reviews with related user and product data
    reviews = Review.objects.select_related('user', 'product') \
        .filter(product=product).order_by('-id')

    try:
        # Aggregate all rating data in a single query
        review_aggregates = reviews.aggregate(
            avg_rating=Avg('rating'),
            count=Count('rating'),
            count_1star=Count('rating', filter=Q(rating=1)),
            count_2star=Count('rating', filter=Q(rating=2)),
            count_3star=Count('rating', filter=Q(rating=3)),
            count_4star=Count('rating', filter=Q(rating=4)),
            count_5star=Count('rating', filter=Q(rating=5)),
        )

        # Calculate average percentage
        review_rating_detail = {
            'avg_rating': review_aggregates['avg_rating'],
            'avg_percent': (review_aggregates['avg_rating'] / 5 * 100) if review_aggregates['avg_rating'] else 0,
        }

        # Calculate star percentages
        for i in range(1, 6):
            review_rating_detail[f"{i}star_percent"] = \
                ((review_aggregates[f"count_{i}star"] / review_aggregates['count'] * 100)
                 if review_aggregates['count'] else 0)
    except TypeError:
        # Handle the case where there are no reviews
        review_rating_detail = {
            'avg_rating': 0,
            'avg_percent': 0,
            '1star_percent': 0,
            '2star_percent': 0,
            '3star_percent': 0,
            '4star_percent': 0,
            '5star_percent': 0,
        }

# Now review_rating_detail contains all the required aggregated data

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
        .select_related('user') \
        .prefetch_related('user__addresses') \
        .annotate(published_product_count=Count('products', filter=Q(products__publish_status='P'))) \
        .all()

    context = {
        'vendors': vendors
    }

    return render(request, 'store/vendor_list.html', context=context)


def vendor_detail(request, pk):
    vendor = Vendor.objects.select_related('user') \
        .prefetch_related('user__addresses') \
        .get(pk=pk)

    products_in_vendor = Product.objects.prefetch_related("images") \
        .select_related('category') \
        .select_related("vendor") \
        .all() \
        .annotate(orders_count=Count('orders')) \
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
            .prefetch_related('images') \
            .select_related('category', 'vendor') \
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

    products = Product.objects \
        .prefetch_related('images') \
        .select_related('vendor', 'category') \
        .filter(title__icontains=query)

    context = {
        'products': products,
        'query': query,
    }

    return render(request, 'store/search.html', context=context)


# --------------------------------------------------------------------------Filters-----------------------------------------------------------------
def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")
    products = Product.objects \
        .filter(is_active=True, publish_status="P") \
        .order_by("-id").distinct()

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
    user = request.user
    product_id = str(request.GET['id'])
    quantity = int(request.GET['quantity'])

    if user.is_authenticated:
        product = Product.objects.get(id=product_id)
        user_cart = Cart.objects.get(user=user)
        user_cart_items = CartItem.objects.filter(cart=user_cart)

        if user_cart_items.filter(product=product).exists():
            pass
        else:
            CartItem.objects.create(
                cart=user_cart, product=product, quantity=quantity)

        cart_items = {}
        user_cart_items = CartItem.objects.filter(cart=user_cart)
        for item in user_cart_items:
            cart_items[str(item.product.id)] = {
                'title': str(item.product.title),
                'quantity': int(item.quantity),
                'price': float(item.product.discount_price),
                'image': f"/media/{item.product.images.first().image}" if item.product.images.exists() else "",
            }

    else:
        cart_product = {}

        cart_product = {
            product_id: {
                'title': request.GET['title'],
                'quantity': quantity,
                'price': request.GET['price'],
                'image': request.GET['image'],
            }
        }

        if 'cart_data_obj' in request.session:
            cart_data = request.session['cart_data_obj']

            if product_id in cart_data:
                cart_data[product_id]['quantity'] = cart_product[product_id]['quantity']

            else:
                cart_data.update(cart_product)

            request.session['cart_data_obj'] = cart_data

        else:
            request.session['cart_data_obj'] = cart_product

        cart_items = request.session['cart_data_obj']

    cart_items_list = [
        {
            'id': product_id,
            'title': item['title'],
            'quantity': item['quantity'],
            'price': item['price'],
            'image': item['image']
        }
        for product_id, item in cart_items.items()
    ]

    cart_total_amount = 0
    for product_id, item in cart_items.items():
        item['subtotal'] = int(item['quantity']) * float(item['price'])
        cart_total_amount += float(item['subtotal'])

    total_cart_items = len(cart_items)
    context = {
        "data": cart_items,
        "totalcartitems": total_cart_items,
        "cartitems": cart_items_list,
        "cart_total_amount": round(cart_total_amount, 2),
    }

    return JsonResponse(context)


def cart_view(request):
    user = request.user
    cart_total_amount = 0
    cart_items = {}

    if user.is_authenticated:
        user_cart = Cart.objects.get(user=user)
        user_cart_items = CartItem.objects.filter(cart=user_cart)

        for item in user_cart_items:
            cart_items[str(item.product.id)] = {
                'title': str(item.product.title),
                'quantity': int(item.quantity),
                'price': float(item.product.discount_price),
                'image': f"/media/{item.product.images.first().image}" if item.product.images.exists() else "",
            }

    elif 'cart_data_obj' in request.session:
        cart_items = request.session['cart_data_obj']
    else:
        messages.warning(request, 'You have no item in cart.')
        return redirect('store:homepage')

    for product_id, item in cart_items.items():
        item['subtotal'] = int(item['quantity']) * float(item['price'])
        cart_total_amount += item['subtotal']

    context = {
        'cart_data': cart_items,
        'totalcartitems': len(cart_items),
        'cart_total_amount': cart_total_amount
    }

    return render(request, "store/cart.html", context=context)


def delete_item_from_cart(request):
    product_id = str(request.GET.get('id'))
    user = request.user
    cart_items = {}
    cart_total_amount = 0

    if user.is_authenticated:
        user_cart = Cart.objects.get(user=user)
        product = Product.objects.get(id=product_id)
        user_cart_items = CartItem.objects.filter(cart=user_cart)
        cart_item = user_cart_items.get(product=product)
        cart_item.delete()
        for item in user_cart_items:
            cart_items[str(item.product.id)] = {
                'title': str(item.product.title),
                'quantity': int(item.quantity),
                'price': float(item.product.discount_price),
                'image': f"/media/{item.product.images.first().image}" if item.product.images.exists() else "",
            }

    elif 'cart_data_obj' in request.session:
        cart_items = request.session['cart_data_obj']

        if product_id in cart_items:
            del cart_items[product_id]
            request.session['cart_data_obj'] = cart_items

    data = render_to_string("store/async/cart_list.html", context=cart_items)
    for product_id, item in cart_items.items():
        item['subtotal'] = int(item['quantity']) * float(item['price'])
        cart_total_amount += item['subtotal']

    context = {
        "data": data,
        "totalcartitems": len(cart_items),
        "cart_total_amount": round(cart_total_amount, 2),
    }

    return JsonResponse(context)


def update_cart(request):

    product_id = str(request.GET['id'])
    product_quantity = int(request.GET['quantity'])
    user = request.user
    cart_items = {}
    cart_total_amount = 0

    if user.is_authenticated:
        user_cart = Cart.objects.get(user=user)
        user_cart_items = CartItem.objects.filter(cart=user_cart)
        product = Product.objects.get(id=product_id)
        cart_item = user_cart_items.get(product=product)
        cart_item.quantity = product_quantity
        cart_item.save()
        for item in user_cart_items:
            cart_items[str(item.product.id)] = {
                'title': str(item.product.title),
                'quantity': int(item.quantity),
                'price': float(item.product.discount_price),
                'image': f"/media/{item.product.images.first().image}" if item.product.images.exists() else "",
            }

    elif 'cart_data_obj' in request.session:
        cart_items = request.session['cart_data_obj']

        if product_id in cart_items:
            cart_items[product_id]['quantity'] = product_quantity
            request.session['cart_data_obj'] = cart_items

    data = render_to_string("store/async/cart_list.html", context=cart_items)
    for product_id, item in cart_items.items():
        item['subtotal'] = int(item['quantity']) * float(item['price'])
        cart_total_amount += item['subtotal']

    context = {
        "data": data,
        "totalcartitems": len(cart_items),
        "cart_total_amount": round(cart_total_amount, 2),
    }

    return JsonResponse(context)


@receiver(user_logged_in)
def transfer_cart(sender, request, user, **kwargs):
    user_has_cart = Cart.objects.filter(user=user).exists()

    if user_has_cart:
        pass

    else:

        session_cart = request.session.get('cart_data_obj', {})
        if session_cart:
            user_cart = Cart.objects.create(user=user)
            for product_id, item in session_cart.items():
                product = Product.objects.get(id=product_id)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=user_cart, product=product)
                cart_item.quantity = item['quantity']
                cart_item.save()


def checkout(request):
    user = request.user
    address_form = AddressForm
    if request.method == "GET":

        if user.is_authenticated:
            cart = Cart.objects.get(user=user)
            user_cart_items = CartItem.objects.filter(cart=cart)
            if len(user_cart_items) == 0:
                messages.info(
                    request, "You have no item in your cart, continue shopping.")
                return redirect('store:homepage')
            else:
                cart_items = {}
                for item in user_cart_items:
                    cart_items[str(item.product.id)] = {
                        'title': str(item.product.title),
                        'quantity': int(item.quantity),
                        'price': float(item.product.discount_price),
                        'image': f"/media/{item.product.images.first().image}" if item.product.images.exists() else "",
                    }
                cart_total_amount = 0
                for product_id, item in cart_items.items():
                    item['subtotal'] = int(
                        item['quantity']) * float(item['price'])
                    cart_total_amount += item['subtotal']

                default_address = Address.objects \
                    .filter(user=user, is_default=True) \
                    .first()
                user_addresses = Address.objects.filter(user=user)
                customer = Customer.objects.get(user=user)
                context = {
                    'cart_data': cart_items,
                    'totalcartitems': len(cart_items),
                    'cart_total_amount': round(cart_total_amount, 2),
                    'addresses': user_addresses,
                    'address_form': address_form,
                    'customer': customer,

                }

                return render(request, 'store/checkout.html', context=context)
        else:
            messages.warning(
                request, "You must login to proceed to Checkout page.")
            return redirect("userauth:login")
    elif request.method == "POST":
        address_form = AddressForm(request.POST or None)
        if address_form.is_valid():
            Address.objects.filter(user=request.user).update(is_default=False)
            new_address = address_form.save(commit=False)
            new_address.user = request.user
            new_address.is_default = True
            new_address.save()
            messages.success(request, 'Address added.')
            return redirect("store:checkout")


def place_order(request):
    user = request.user

    if user.is_authenticated:
        user_cart = Cart.objects.filter(user=user).first()
        user_cart_items = CartItem.objects.filter(cart=user_cart)

        customer = Customer.objects.get(user=user)

        new_order = Order.objects.create(customer=customer)

        order_total_price = 0
        for item in user_cart_items:
            OrderItem.objects.create(
                order=new_order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.discount_price
            )
            order_total_price += item.quantity * item.product.discount_price

        user_address = Address.objects.filter(
            user=user, is_default=True).first()

        if user_address:
            Shipment.objects.create(
                order=new_order,
                address=user_address,
            )
        else:
            messages.warning(request, "Please select the address.")
            return redirect('store:checkout')

    else:
        messages.warning(
            request, "You must login to place order.")
        return redirect("userauth:login")

    zarinpal_request_data = {
        "MerchantID": settings.MERCHANT,
        "Amount": str(order_total_price),
        "Description": f"ORDER_NO_{new_order.id}",
        "Phone": str(customer.phone_number),
        "CallbackURL": f'http://127.0.0.1:8000/zarinpal-verify/?order_total_price={order_total_price}&order_id={new_order.id}',
    }

    req_data = json.dumps(zarinpal_request_data)
    # set content length by data
    req_headers = {'content-type': 'application/json',
                   'content-length': str(len(req_data))}
    try:
        resp = requests.post(
            ZP_API_REQUEST, data=req_data, headers=req_headers, timeout=10)

        if resp.status_code == 200:
            resp = resp.json()

            if resp['Status'] == 100:

                authority = resp['Authority']
                print(f"authority: {authority}")
                return redirect(ZP_API_STARTPAY+authority)
            else:
                return render(request, 'store/payment_failed.html')
        return resp

    except requests.exceptions.Timeout:
        return JsonResponse({'status': False, 'code': 'timeout'})
    except requests.exceptions.ConnectionError:
        return JsonResponse({'status': False, 'code': 'connection error'})


def zarinpal_verify(request):
    authority = request.GET.get('Authority')
    order_total_price = request.GET.get('order_total_price')
    order_id = request.GET.get('order_id')
    req_data = {
        "MerchantID": settings.MERCHANT,
        "Amount": order_total_price,
        "Authority": authority,
    }
    req_data = json.dumps(req_data)
    # set content length by data
    req_headers = {'content-type': 'application/json',
                   'content-length': str(len(req_data))}
    resp = requests.post(ZP_API_VERIFY, data=req_data, headers=req_headers)

    if resp.status_code == 200:
        resp = resp.json()
        order = Order.objects.get(id=order_id)
        if resp['Status'] == 100:

            order.payment_status = "C"
            order.save()
            order_items = OrderItem.objects \
                .filter(order=order) \
                .annotate(
                    subtotal=(F("quantity") * F("unit_price")),
                )

            user_cart = Cart.objects.filter(user=request.user).first()
            user_cart_items = CartItem.objects.filter(cart=user_cart)
            user_cart_items.delete()
            context = {
                "order": order,
                "order_items": order_items,
                "order_total_price": order_total_price
            }

            return render(request, 'store/payment_successful.html', context=context)
        else:
            order.payment_status = "F"
            order.save()
            return render(request, 'store/payment_failed.html')
    return resp


def order_detail(request, id):
    order = Order.objects.get(id=id)

    order_items = OrderItem.objects \
        .filter(order=order) \
        .annotate(
            subtotal=(F("quantity") * F("unit_price")),
        )

    context = {
        "order": order,
        "order_items": order_items,
    }

    return render(request, 'store/order_detail.html', context=context)


def customer_dashboard(request):
    customer = Customer.objects.get(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    address_form = AddressForm
    customer_orders = Order.objects \
        .filter(customer=customer) \
        .annotate(
            items_count=Count('items'),
            total_price=Sum(F("items__quantity") * F("items__unit_price")),
        ) \
        .order_by('-id')
    if request.method == 'POST':
        address_form = AddressForm(request.POST or None)
        if address_form.is_valid():
            Address.objects.filter(user=request.user).update(is_default=False)
            new_address = address_form.save(commit=False)
            new_address.user = request.user
            new_address.is_default = True
            new_address.save()
            messages.success(request, 'Address added.')
            return redirect("store:customer-dashboard")

    context = {
        'orders': customer_orders,
        'addresses': addresses,
        'address_form': address_form,

    }
    return render(request, 'store/customer_dashboard.html', context=context)


def set_default_address(request):
    user = request.user
    address_id = request.GET['id']

    Address.objects.filter(user=user).update(is_default=False)
    Address.objects.filter(id=address_id).update(is_default=True)

    return JsonResponse({'boolean': True})


def delete_address(request):
    address_id = request.GET["id"]

    Address.objects.get(id=address_id).delete()

    return JsonResponse({"boolean": True})


def wishlist_view(request):
    user = request.user
    wishlist = Wishlist.objects.filter(user=user)

    context = {
        'wishlist': wishlist,
    }

    return render(request, 'store/wishlist.html', context=context)


def add_to_wishlist(request):
    product_id = request.GET.get('product_id')
    user = request.user
    product = Product.objects.get(id=product_id)

    product_in_wishlist = Wishlist.objects.filter(
        product=product, user=user).exists()

    if product_in_wishlist:
        pass
    else:
        Wishlist.objects.create(
            product=product,
            user=user,
        )

    wishlist_count = Wishlist.objects.filter(user=user).count()

    context = {
        "bool": True,
        "wishlist_count": wishlist_count,

    }

    return JsonResponse(context)


def delete_from_wishlist(request):
    product_id = request.GET.get('product_id')
    user = request.user
    product = Product.objects.get(id=product_id)

    Wishlist.objects.filter(product=product, user=user).delete()

    wishlist_count = Wishlist.objects.filter(user=user).count()

    context = {
        "bool": True,
        "wishlist_count": wishlist_count,
    }

    return JsonResponse(context)
