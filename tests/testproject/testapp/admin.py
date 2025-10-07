from django.contrib import admin

from dalf.admin import (
    DALFChoicesField,
    DALFModelAdmin,
    DALFRelatedField,
    DALFRelatedFieldAjax,
    DALFRelatedOnlyField,
)

from .models import (
    Category,
    CategoryRenamed,
    Item,
    Order,
    Post,
    Product,
    Supplier,
    Tag,
)


@admin.register(Post)
class PostAdmin(DALFModelAdmin):
    list_display = ('title',)
    list_filter = (
        ('author', DALFRelatedField),
        ('audience', DALFChoicesField),
        ('category', DALFRelatedFieldAjax),
        ('category_renamed', DALFRelatedFieldAjax),
        ('tags', DALFRelatedOnlyField),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(CategoryRenamed)
class CategoryRenamedAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ('name', 'supplier__name')
    ordering = ('name',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    search_fields = ('name', 'product__name')
    ordering = ('name',)


@admin.register(Order)
class OrderAdmin(DALFModelAdmin):
    list_display = ('reference',)
    list_filter = (('item__product__supplier', DALFRelatedFieldAjax),)
