from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('categories/', views.CategoriesView.as_view()),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>/', views.SingleItemView.as_view()),
    path('menu-items/item-of-the-day/', views.item_of_the_day),
    path('menu-items/item-of-the-day/set/', views.set_item_of_the_day),
    path('categories/<int:pk>/', views.SingleCategoryView.as_view()),
    path('secret/', views.secret_view),
    path('api-token-auth/', obtain_auth_token), #for token generation  ->  Only accepts HTTP Post requests
    path('manager/', views.manager_view),
    path('throttle-check/', views.throttle_check_view),
    path('throttle-check-auth/', views.throttle_check_view),
    path('me/', views.me),
    path('groups/manager/users', views.manager_users),
    path('groups/manager/users/<int:user_id>/', views.manager_user_detail),
    path('groups/delivery-crew/users', views.delivery_crew_users),
    path('groups/delivery-crew/users/<int:user_id>/', views.delivery_crew_user_detail),
    path('ratings/', views.RatingsView.as_view()),
    path('cart/menu-items/', views.CartItemsView.as_view()),
    path('cart/menu-items/<int:pk>/', views.CartItemDetailView.as_view()),
    path('orders/', views.OrdersView.as_view()),
    path('orders/<int:pk>/', views.OrderDetailView.as_view()),
]