from django.urls import path


from . import views

app_name = 'store'

urlpatterns = [
    #####   HomePage  ######
    path('', views.homepage, name='homepage'),

    #####   Products  ######
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>', views.product_detail, name='product_detail'),


    #####   Categories  ######
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>', views.category_product_list,
         name='category_product_list'),

    #####   Vendors  ######
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/<int:pk>', views.vendor_detail, name='vendor_detail'),

    #####   Tags  ######
    path('products/tag/<slug:tag_slug>/', views.tag_product_list, name='tags'),

    #####   Add Review  ######
    path('ajax-add-review/<pk>/', views.ajax_add_review, name='ajax_add_review'),

    #####   Search Product  ######
    path('search/', views.search_view, name='search'),

    #####   About Page  ######
    path('about/', views.about_us, name='about'),

    #####   Filter Product  ######
    path('filter-products/', views.filter_product, name='filter-product'),


    #####   Carts  ######
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.cart_view, name='cart'),
    path('delete-from-cart/', views.delete_item_from_cart, name='delete-cart-item'),
    path('update-cart/', views.update_cart, name='update-cart-item'),


    path('checkout/', views.checkout, name='checkout'),


    path('customer-dashboard/', views.customer_dashboard,
         name="customer-dashboard"),

    path('customer-dashboard/order/<int:id>',
         views.order_detail, name="order-detail"),

    path('place-order/', views.place_order, name="place-order"),
    path('zarinpal-verify/', views.zarinpal_verify, name='zarinpal-verify'),


    path('set-default-address', views.set_default_address,
         name="set-default-address"),

    path("delete-address/", views.delete_address, name="delete-address"),

    path("wishlist/", views.wishlist_view, name="wishlist"),
    path('add-to-wishlist/', views.add_to_wishlist, name="add-to-wishlist"),
    path('delete-from-wishlist/', views.delete_from_wishlist,
         name="delete-from-wishlist"),
    path('subscribe-email/', views.subscribe_email, name="subscribe-email")

]
