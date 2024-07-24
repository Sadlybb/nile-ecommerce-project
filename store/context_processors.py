from django.db.models import Min, Max
from .models import Category, Vendor, Product, Cart, CartItem
from taggit.models import Tag


def default(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.prefetch_related('products').all()
    min_max_price = Product.objects.aggregate(
        Min("discount_price"), Max("discount_price"))
    tags = Tag.objects.all()

    context = {
        'categories': categories,
        'vendors': vendors,
        'tags': tags,
        'min_max_price': min_max_price,
    }

    cart_total_amount = 0
    cart_data_context = {}

    if request.user.is_authenticated:
        user_cart, create = Cart.objects.get_or_create(user=request.user)

        if create:
            cart_data_context = {}
            cart_total_amount = 0
        else:
            user_cart_items = CartItem.objects.filter(
                cart=user_cart).prefetch_related('product__images')
            for item in user_cart_items:
                product_id = str(item.product.id)
                cart_data_context[product_id] = {
                    'title': item.product.title,
                    'quantity': item.quantity,
                    'price': str(item.product.discount_price),
                    'image': f"/media/{item.product.images.first().image}" if item.product.images.exists() else "",
                }

    else:
        if 'cart_data_obj' in request.session:
            cart_data_context = request.session['cart_data_obj']
        else:
            cart_data_context = {}

    for product_id, item in cart_data_context.items():
        item['subtotal'] = int(item['quantity']) * float(item['price'])
        cart_total_amount += float(item['subtotal'])

    context['cart_data'] = cart_data_context
    context['totalcartitems'] = len(cart_data_context)
    context['cart_total_amount'] = cart_total_amount

    return context
