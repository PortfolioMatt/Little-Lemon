from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#RECORDAR ---> EL ORDEN IMPORTA  
class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title
    
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    is_item_of_the_day = models.BooleanField(default=False, help_text="Marks this menu item as the item of the day (only one should be True)")

class Rating(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField()  # Assuming score is an integer value
    comment = models.TextField(blank=True, null=True)  # Optional comment field
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # To track which user gave the rating

class CartItem(models.Model):
    """Represents a MenuItem in a user's cart.

    We don't create a separate Cart model; the cart is the collection of a user's CartItem rows.
    unit_price snapshots the price at the moment of adding; total is derived.
    Unique constraint prevents duplicate rows for same user/menu_item.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='in_carts')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menu_item')

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} for {self.user.username}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = (
        (0, 'Out for delivery'),
        (1, 'Delivered'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order', 'menu_item')

    @property
    def total_price(self):
        return self.unit_price * self.quantity