from django.db import models
from django_countries.fields import CountryField

from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager

from userauth.models import User


RATING_CHOICES = (
    (1, '★☆☆☆☆'),
    (2, '★★☆☆☆'),
    (3, '★★★☆☆'),
    (4, '★★★★☆'),
    (5, '★★★★★'),
)


def user_directory_path(instance, filename):
    return 'images/users/id_{0}/{1}'.format(instance.user.id, filename)


class Vendor(models.Model):
    title = models.CharField(max_length=255)
    short_description = models.CharField(
        max_length=150, null=True, blank=True, default='-')
    full_description = RichTextUploadingField(blank=True, default='-')
    phone_number = models.CharField(max_length=30, default="+989123456789")
    image = models.ImageField(
        upload_to=user_directory_path, default="/images/users/person.png", null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    chat_response_time = models.CharField(max_length=100, default="1 Day")
    shipping_time = models.CharField(max_length=100, default="1 Day")
    allowed_return_days = models.CharField(max_length=100, default="7 Day")
    warranty_period = models.CharField(max_length=100, default="7 Day")
    join_date = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='vendor')

    def __str__(self):
        return self.title

    def get_rating_percent(self):
        return float((self.rating) / 5 * 100)

    def get_address(self):
        if hasattr(self.user, 'addresses'):
            # If addresses are prefetched, use them directly
            return self.user.addresses.all()[0] if self.user.addresses.exists() else None
        else:
            # Fallback to querying if addresses are not prefetched
            return self.user.addresses.first()

    class Meta:
        verbose_name_plural = "Vendors"


class Customer(models.Model):
    MEMBERSHIP_STATUS_BRONZE = "B"
    MEMBERSHIP_STATUS_SILVER = "S"
    MEMBERSHIP_STATUS_GOLD = "G"

    MEMBERSHIP_STATUS_CHOICES = {
        MEMBERSHIP_STATUS_BRONZE: "Bronze",
        MEMBERSHIP_STATUS_SILVER: "Silver",
        MEMBERSHIP_STATUS_GOLD: "Gold",
    }

    phone_number = models.CharField(max_length=30, default="+989123456789")
    birth_date = models.DateField(null=True, blank=True)
    image = models.ImageField(
        upload_to=user_directory_path, default="/images/users/person.png", null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_STATUS_CHOICES, default="B")

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='customer')

    def __str__(self):
        return f"{self.user.first_name} - {self.user.last_name}"

    class Meta:
        verbose_name_plural = "Customers"


class Address(models.Model):
    address_line = models.TextField()
    postal_code = models.CharField(max_length=10)
    country = CountryField(blank_label="(select country)")
    city = models.CharField(max_length=50)
    assigned_phone_number = models.CharField(max_length=30)
    is_default = models.BooleanField(default=False)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses")

    def __str__(self):
        return f"{self.country} - {self.city} - {self.address_line[:20]}"

    class Meta:
        verbose_name_plural = "Addresses"


class Category(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(
        upload_to='store/images/category', default="store/images/category.png")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_categories")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):

    PUBLISH_STATUS_PUBLISHED = "P"
    PUBLISH_STATUS_REVIEW = "R"
    PUBLISH_STATUS_DRAFT = "D"

    PUBLISH_STATUS_CHOICES = [
        (PUBLISH_STATUS_PUBLISHED, "Published"),
        (PUBLISH_STATUS_REVIEW, "Pending Review"),
        (PUBLISH_STATUS_DRAFT, "Draft"),
    ]

    title = models.CharField(max_length=255)
    short_description = models.CharField(
        max_length=150, null=True, blank=True, default='-')
    full_description = RichTextUploadingField(blank=True, default='-')
    specifications = RichTextUploadingField(blank=True, default='-')
    slug = models.SlugField()
    sku = models.CharField(max_length=100)
    regular_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=2.99)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=1.99)
    inventory = models.IntegerField()
    publish_status = models.CharField(
        max_length=1, choices=PUBLISH_STATUS_CHOICES, default="D")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(choices=RATING_CHOICES, default=3)

    tags = TaggableManager(blank=True)

    vendor = models.ForeignKey(
        Vendor, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_products')

    def __str__(self):
        return self.title

    def get_rating_percent(self):
        return float(self.rating / 5) * 100

    def get_discount_percent(self):
        return int((self.regular_price - self.discount_price) / self.regular_price * 100)

    class Meta:
        verbose_name_plural = "Products"


class ProductImage(models.Model):
    image = models.ImageField(
        upload_to="store/images/product", default="store/images/product.png")

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images")

    class Meta:
        verbose_name_plural = "Product Images"


class Order(models.Model):
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETE = "C"
    PAYMENT_STATUS_FAILED = "F"

    PAYMENT_STATUS_CHOICES = {
        PAYMENT_STATUS_PENDING: "Pending",
        PAYMENT_STATUS_COMPLETE: "Complete",
        PAYMENT_STATUS_FAILED: "Failed",
    }

    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default="P")
    placed_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="orders")

    def __str__(self) -> str:
        return f"{self.customer} - {self.last_update} - {self.payment_status}"

    class Meta:
        verbose_name_plural = "Orders"


class OrderItem(models.Model):
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orders")\


    def __str__(self):
        return f"{self.order.id} - {self.product} - {self.quantity} - {self.unit_price}"

    class Meta:
        verbose_name_plural = "Order Items"


class Cart(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for User {self.user.username if self.user else 'Anonymous'}"

    class Meta:
        verbose_name_plural = "Carts"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in Cart {self.cart.id}"

    class Meta:
        verbose_name_plural = "Cart Items"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, default="Review Title")
    description = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES, default=1)

    def get_rating_percent(self):
        return float((self.rating)/5*100)


class Shipment(models.Model):

    SHIPMENT_STATUS_PENDING = "P"
    SHIPMENT_STATUS_SHIPPED = "S"
    SHIPMENT_STATUS_DELIVERD = "D"

    SHIPMENT_STATUS_CHOICES = {
        SHIPMENT_STATUS_PENDING: "Proccessing",
        SHIPMENT_STATUS_SHIPPED: "Shipped",
        SHIPMENT_STATUS_DELIVERD: "Delivered",
    }

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="shipments")
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="shipments")
    status = models.CharField(
        max_length=1, choices=SHIPMENT_STATUS_CHOICES, default="P")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Shipments"


class Wishlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='wishlists')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product}"

    class Meta:
        verbose_name_plural = 'Wishlists'


class EmailSubscription(models.Model):
    email = models.EmailField(unique=True)
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Email Subscription'
        verbose_name_plural = 'Email Subscriptions'
