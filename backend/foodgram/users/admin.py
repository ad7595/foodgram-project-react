from django.contrib import admin
from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',)
    search_fields = ('username', 'role',)
    list_filter = ('username', 'email',)
    ordering = ('username',)
    empty_value_display = '-пусто-'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = (
        'author__username',
        'author__email',
        'user__username',
        'user__email',
    )
    list_filter = ('author__username', 'user__username',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
