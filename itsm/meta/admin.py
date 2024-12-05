from django.contrib import admin
from .models import Context

# Register your models here.
class ContextAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "value", "created_at", "updated_at")
    search_fields = ("key", "value")
    list_filter = ("key", )


admin.site.register(Context, ContextAdmin)
