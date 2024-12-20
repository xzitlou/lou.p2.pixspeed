from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from accounts.models import CustomUser


class CustomUserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'email',
        'is_active',
        'is_staff',
        'is_confirm',
        'verification_code',
    )

    fieldsets = (
        (None, {
            'fields': ("full_name", 'email', 'password')
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_confirm',
            )
        }),
        ('API', {
            'fields': (
                "api_token",
                "image_credits",
                "free_image_credits",
                "next_free_credits_date",
            )
        }),
        ('Billing', {
            'fields': (

            )
        }),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'phone_number', 'email', 'password1', 'password2', 'is_staff')}
         ),
    )
    search_fields = (
        'email',
    )
    ordering = ('email',)
    filter_horizontal = ()
    list_filter = ()


admin.site.register(CustomUser, CustomUserAdmin)
