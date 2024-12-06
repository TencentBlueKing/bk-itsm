from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Context(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True)

    def __str__(self):
        return self.key

    class Meta:
        db_table = "meta_context"


@receiver(post_save, sender=Context)
def update_cache(sender, instance, **kwargs):
    cache_key = f"meta_context_{instance.key}"
    cache.set(cache_key, instance.value, 30)


class ContextService:
    @staticmethod
    def get_context_value(key):
        cache_key = f"meta_context_{key}"
        context_value = cache.get(cache_key)
        if not context_value:
            try:
                context_value = Context.objects.get(key=key).value
            except Context.DoesNotExist:
                context_value = ""
            cache.set(cache_key, context_value, 30)
        return context_value

    @staticmethod
    def get_context_value_list(key):
        context_value = ContextService.get_context_value(key)
        context_value = (
            [item.strip() for item in context_value.split(",")] if context_value else []
        )
        return context_value
