
from django.db.models import Min, Max

from .models import Category, Vendor, Product
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
    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            item['subtotal'] = int(item['quantity']) * float(item['price'])
            cart_total_amount += item['subtotal']

        context['cart_data'] = request.session['cart_data_obj']
        context['totalcartitems'] = len(request.session['cart_data_obj'])
        context['cart_total_amount'] = cart_total_amount

    return context
