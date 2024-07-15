from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Count

from taggit.models import Tag

from . models import Vendor, Category, Product


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
    product = Product.objects.prefetch_related('images').get(pk=pk)
    categories = Category.objects.all()

    context = {
        "product": product,
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
