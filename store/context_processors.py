

from .models import Category, Vendor


def default(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.prefetch_related('products').all()

    return {
        'categories': categories,
        'vendors': vendors
    }
