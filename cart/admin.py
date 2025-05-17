from django.contrib import admin
from django.utils import timezone
from .models import Order, OrderItem

# Register your models here.


@admin.action(description='Mark as ordered and delete from cart')
def mark_and_delete(modeladmin, request, queryset):
    queryset.update(ordered=True, ordered_date=timezone.now())
    queryset.delete()


class OrderedFilter(admin.SimpleListFilter):
    title = 'Ordered'
    parameter_name = 'ordered'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(ordered=True)
        if self.value() == 'No':
            return queryset.filter(ordered=False)
        return queryset


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'quantity', 'ordered', 'ordered_date')
    list_filter = (OrderedFilter,)


admin.site.register(OrderItem, OrderItemAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('ref_code', 'user', 'ordered', 'created_at',
                    'payment_status', 'get_order_items')

    def get_order_items(self, obj):
        return ", ".join([str(item) for item in obj.items.all()])
    get_order_items.short_description = 'Order Items'


admin.site.register(Order, OrderAdmin)
