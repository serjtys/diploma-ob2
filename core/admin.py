from django.contrib import admin
from .models import Post, Subscription

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('title', 'content')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
