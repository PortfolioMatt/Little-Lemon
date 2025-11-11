from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from django_filters import rest_framework as filters
from .models import MenuItem, Category, Rating
from .serializers import MenuItemSerializer, SingleItemSerializer, RatingSerializer
from .serializers import CategorySerializer
from .permissions import IsManagerOrAdminOrReadOnly, IsManagerOrAdmin, IsCustomer
from .pagination import MenuItemsPagination
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .throttles import TenCallsPerMinuteUserThrottle
from django.contrib.auth.models import User, Group
from .models import CartItem, Order, OrderItem
from .serializers import CartItemSerializer, OrderReadSerializer, ManagerOrderUpdateSerializer, DeliveryCrewOrderUpdateSerializer

# Custom filter for MenuItem with range filters
class MenuItemFilterView(filters.FilterSet):
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')
    inventory_min = filters.NumberFilter(field_name='inventory', lookup_expr='gte')
    inventory_max = filters.NumberFilter(field_name='inventory', lookup_expr='lte')
    '''This does not filter; it's only to show an input in the browsable API so users can set the paginator page size via ?number_pages='''
    number_pages = filters.NumberFilter(method='noop', label='Items per page')
    
    def noop(self, queryset, name, value):
        return queryset
    
    class Meta:
        model = MenuItem
        fields = ['category']


# Custom filter for Order with range filters
class OrderFilterView(filters.FilterSet):
    total_min = filters.NumberFilter(field_name='total', lookup_expr='gte')
    total_max = filters.NumberFilter(field_name='total', lookup_expr='lte')
    date_min = filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    date_max = filters.DateTimeFilter(field_name='date', lookup_expr='lte')
    number_pages = filters.NumberFilter(method='noop', label='Items per page')
    
    def noop(self, queryset, name, value):
        return queryset
    
    class Meta:
        model = Order
        fields = ['status', 'user', 'delivery_crew']

# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuItemsPagination
    filterset_class = MenuItemFilterView  # Use custom filter
    ordering_fields = ['price', 'inventory', 'id']  # Allows ordering by price, inventory, or id
    search_fields = ['name']  # Allows text search in the name of the dish
    permission_classes = [IsManagerOrAdminOrReadOnly]
    
class SingleItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = SingleItemSerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]

@api_view(['GET'])
def item_of_the_day(request):
    """Public endpoint: returns the current item of the day or 404 if none set."""
    item = MenuItem.objects.filter(is_item_of_the_day=True).first()
    if not item:
        return Response({'detail': 'No item of the day set.'}, status=404)
    return Response(MenuItemSerializer(item).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManagerOrAdmin])
def set_item_of_the_day(request):
    """Manager/Admin endpoint: set a menu item as item of the day.

    Body: { "menu_item_id": <id> }
    - Clears previous item_of_the_day flags.
    - Marks the given item.
    """
    menu_item_id = request.data.get('menu_item_id')
    if not menu_item_id:
        return Response({'detail': 'menu_item_id is required'}, status=400)
    try:
        item = MenuItem.objects.get(pk=menu_item_id)
    except MenuItem.DoesNotExist:
        return Response({'detail': 'Menu item not found'}, status=404)
    # Clear previous
    MenuItem.objects.filter(is_item_of_the_day=True).update(is_item_of_the_day=False)
    item.is_item_of_the_day = True
    item.save(update_fields=['is_item_of_the_day'])
    return Response(MenuItemSerializer(item).data, status=200)
    
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]
    
class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]

@api_view()
@permission_classes([IsAuthenticated])
def secret_view(request):
    return Response({"message": "Some secret message for authenticated users only."})

#Like this I can protect API endpoints based on user groups
@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    if(request.user.groups.filter(name='Manager').exists()):
        return Response({"message": "Some manager message for authenticated users only."})
    return Response({"message": "You do not have permission to view this."}, status=403)

@api_view()
@throttle_classes([AnonRateThrottle]) #available only to anon classes
def throttle_check_view(request):
    return Response({"message": "successful throttle check for anon users"})

@api_view()
@throttle_classes([TenCallsPerMinuteUserThrottle]) #available only to authenticated users, the throttle class is created by me
def throttle_check_view(request):
    return Response({"message": "successful throttle check for authenticated users"})

@api_view()
@permission_classes([IsAuthenticated])
def me(request):
    return Response({
        "username": request.user.username,
        "email": request.user.email,
        "is_staff": request.user.is_staff,
        "is_superuser": request.user.is_superuser,
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsManagerOrAdmin])
def manager_users(request):
    """GET: list all managers; POST: add username to Manager group."""
    group, _ = Group.objects.get_or_create(name='Manager')
    if request.method == 'GET':
        users = group.user_set.all().values('id', 'username', 'email')
        return Response(list(users))
    # POST
    username = request.data.get('username')
    if not username:
        return Response({"detail": "username is required"}, status=400)
    user = get_object_or_404(User, username=username)
    group.user_set.add(user)
    return Response({"message": "Created", "user": {"id": user.id, "username": user.username}}, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsManagerOrAdmin])
def manager_user_detail(request, user_id: int):
    """DELETE: remove user from Manager group by user id."""
    group, _ = Group.objects.get_or_create(name='Manager')
    user = get_object_or_404(User, pk=user_id)
    group.user_set.remove(user)
    return Response({"message": "Success"}, status=200)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsManagerOrAdmin])
def delivery_crew_users(request):
    """GET: list all delivery crew; POST: add username to Delivery Crew group."""
    group, _ = Group.objects.get_or_create(name='Delivery Crew')
    if request.method == 'GET':
        users = group.user_set.all().values('id', 'username', 'email')
        return Response(list(users))
    # POST
    username = request.data.get('username')
    if not username:
        return Response({"detail": "username is required"}, status=400)
    user = get_object_or_404(User, username=username)
    group.user_set.add(user)
    return Response({"message": "Created", "user": {"id": user.id, "username": user.username}}, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsManagerOrAdmin])
def delivery_crew_user_detail(request, user_id: int):
    """DELETE: remove user from Delivery Crew group by user id."""
    group, _ = Group.objects.get_or_create(name='Delivery Crew')
    user = get_object_or_404(User, pk=user_id)
    group.user_set.remove(user)
    return Response({"message": "Success"}, status=200)

class RatingsView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated()]


class CartItemsView(generics.ListCreateAPIView):
    """Authenticated users manage their own cart items.

    - GET: list current user's cart items
    - POST: add an item {menu_item_id, quantity}
    - DELETE: remove ALL items from the current user's cart
    """
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('menu_item')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def delete(self, request, *args, **kwargs):
        """Clear the entire cart for the authenticated customer.

        Returns 200 with a summary of how many items were removed.
        """
        qs = self.get_queryset()
        deleted = qs.count()
        qs.delete()
        return Response({"message": "Cart cleared", "deleted_items": deleted}, status=200)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update quantity, or delete a cart item of the current user."""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('menu_item')


def _is_manager(user):
    return user.is_superuser or user.groups.filter(name='Manager').exists()


def _is_delivery(user):
    return user.groups.filter(name='DeliveryCrew').exists()


class OrdersView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderReadSerializer
    pagination_class = MenuItemsPagination
    filterset_class = OrderFilterView
    ordering_fields = ['total', 'date', 'status']
    search_fields = ['user__username', 'delivery_crew__username']

    def get_queryset(self):
        user = self.request.user
        if _is_manager(user):
            return Order.objects.all().prefetch_related('items__menu_item', 'user', 'delivery_crew')
        if _is_delivery(user):
            return Order.objects.filter(delivery_crew=user).prefetch_related('items__menu_item', 'user', 'delivery_crew')
        # customer
        return Order.objects.filter(user=user).prefetch_related('items__menu_item', 'user', 'delivery_crew')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by('-date'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Only customers can create orders from their cart
        user = request.user
        if _is_manager(user) or _is_delivery(user):
            return Response({"detail": "Only customers can create orders."}, status=403)
        cart_items = CartItem.objects.filter(user=user).select_related('menu_item')
        if not cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=400)
        # Create order
        order = Order.objects.create(user=user, status=0, total=0)
        order_items = []
        total = 0
        for ci in cart_items:
            oi = OrderItem(order=order, menu_item=ci.menu_item, quantity=ci.quantity, unit_price=ci.unit_price)
            order_items.append(oi)
            total += ci.unit_price * ci.quantity
        OrderItem.objects.bulk_create(order_items)
        order.total = total
        order.save()
        # Clear cart
        cart_items.delete()
        return Response(OrderReadSerializer(order).data, status=201)


class OrderDetailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderReadSerializer

    def get_object(self, pk):
        return get_object_or_404(Order.objects.prefetch_related('items__menu_item', 'user', 'delivery_crew'), pk=pk)

    def get(self, request, pk: int):
        order = self.get_object(pk)
        user = request.user
        if _is_manager(user) or (_is_delivery(user) and order.delivery_crew_id == user.id) or (order.user_id == user.id):
            return Response(OrderReadSerializer(order).data)
        return Response({"detail": "Not found."}, status=404)

    def patch(self, request, pk: int):
        order = self.get_object(pk)
        user = request.user
        if _is_manager(user):
            serializer = ManagerOrderUpdateSerializer(order, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(OrderReadSerializer(order).data)
        if _is_delivery(user):
            if order.delivery_crew_id != user.id:
                return Response({"detail": "This order is not assigned to you."}, status=403)
            serializer = DeliveryCrewOrderUpdateSerializer(order, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(OrderReadSerializer(order).data)
        return Response({"detail": "Forbidden"}, status=403)

    def put(self, request, pk: int):
        # Treat PUT like manager full update of allowed fields
        return self.patch(request, pk)

    def delete(self, request, pk: int):
        order = self.get_object(pk)
        if not _is_manager(request.user):
            return Response({"detail": "Forbidden"}, status=403)
        order.delete()
        return Response(status=204)