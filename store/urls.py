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


    path('search/', views.search_view, name='search'),


    path('about/', views.about_us, name='about'),

    path('filter-products/', views.filter_product, name='filter-product'),


]
