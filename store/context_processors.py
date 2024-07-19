
from django.db.models import Min, Max

from .models import Category, Vendor, Product
from taggit.models import Tag


def default(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.prefetch_related('products').all()
    min_max_price = Product.objects.aggregate(
        Min("discount_price"), Max("discount_price"))
    tags = Tag.objects.all()
    return {
        'categories': categories,
        'vendors': vendors,
        'tags': tags,
        'min_max_price': min_max_price,
    }
