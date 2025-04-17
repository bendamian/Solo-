from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile

# Unregister the default Group model (optional)
admin.site.unregister(Group)

# Define inline admin descriptor for Profile model


class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ('name', 'phone_number', 'email', 'profile_bio',
              'facebook_link', 'profile_image')
    readonly_fields = ('date_modified',)
    extra = 0  # Don't show extra empty forms
    can_delete = False  # Prevent accidental deletion

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Define a new User admin


class CustomUserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_active', 'is_staff')
    search_fields = ('username', 'email',
                     'profile__phone_number', 'profile__name')
    list_filter = ('is_active', 'is_staff')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
