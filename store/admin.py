from typing import Any
from django.contrib import admin
from django.urls import reverse
from django.db.models import Count, Sum, F
from django.utils.html import format_html, urlencode
from . models import Vendor, Customer, Address, Category, Product, ProductImage, Order, OrderItem, Cart, CartItem, Review, Shipment

#########################      Inlines      #########################
#########################      Inlines      #########################
#########################      Inlines      #########################


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    readonly_fields = ['thumbnail']
    extra = 1

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" width="150" height="150" class="thumbnail">')
        return ''


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    extra = 0


class CartItemInline(admin.TabularInline):
    model = CartItem
#########################      Filters      #########################
#########################      Filters      #########################
#########################      Filters      #########################


#########################      Model Admins      #########################
#########################      Model Admins      #########################
#########################      Model Admins      #########################


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['category']
    prepopulated_fields = {
        'slug': ['title'],
    }

    list_display = ['title', 'category_title', 'regular_price',
                    'discount_price', 'inventory',
                    'publish_status', 'is_active', 'is_featured', 'rating']
    exclude = ['created_by']
    list_editable = ['regular_price', 'discount_price',
                     'inventory', 'publish_status', 'rating', 'is_active', 'is_featured']
    list_filter = ['category', 'publish_status']
    list_select_related = ['category']
    search_fields = ['title']
    list_per_page = 10

    inlines = [ProductImageInline]

    @admin.display(ordering='category')
    def category_title(self, product):
        return product.category.title

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        return super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image', 'products_count']
    exclude = ['created_by']
    search_fields = ['title']

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        return super().save_model(request, obj, form, change)

    def category_image(self, instance):
        return format_html(f"<img src='{instance.image.url}' width='50' height='50'/>")

    @admin.display(ordering='products_count')
    def products_count(self, category):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'category__id': str(category.id),
            })
        )
        return format_html('<a href="{}">{} Products</a>', url, category.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name',
                    'customer_image', 'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 10
    list_filter = ['membership']
    list_select_related = ['user']
    search_fields = ['user', 'first_name', 'last_name']

    def customer_image(self, instance):
        return format_html(f"<img src='{instance.image.url}' width='50' height='50'/>")

    @admin.display(ordering='user__first_name')
    def first_name(self, customer):
        return customer.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self, customer):
        return customer.user.last_name

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:core_order_changelist')
            + '?'
            + urlencode({
                'customer_id': str(customer.id),
            })
        )
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('orders')
        )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name',
                    'vendor_image', 'title', 'rating']
    list_per_page = 10
    list_filter = ['rating']
    list_select_related = ['user']
    search_fields = ['user', 'first_name', 'last_name', 'title']

    def vendor_image(self, instance):
        return format_html(f"<img src='{instance.image.url}' width='50' height='50'/>")

    @admin.display(ordering='user__first_name')
    def first_name(self, vendor):
        return vendor.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self, vendor):
        return vendor.user.last_name


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'country', 'city', 'postal_code', 'address_line1']
    list_per_page = 10
    list_filter = ['country', 'city']
    list_select_related = ['user']
    search_fields = ['country', 'city', 'address_line1']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'placed_at',
                    'total_price', 'payment_status']
    list_per_page = 10
    list_filter = ['placed_at', 'payment_status']
    list_select_related = ['customer']
    search_fields = ['customer']
    inlines = [OrderItemInline]

    @admin.display(ordering='total_price')
    def total_price(self, order):
        return order.total_price

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_price=Sum(F('items__quantity') *
                            F('items__unit_price'))
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity', 'unit_price', 'order']
    list_select_related = ['order']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    list_per_page = 10
    list_filter = ['created_at']
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity']


@admin.register(Review)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'posted_at', 'short_desc']
    list_per_page = 10

    def short_desc(self, review: Review):
        return review.description[:30]


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['order', 'address', 'status', 'updated_at']
