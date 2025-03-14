from django.contrib import admin

from dalf.admin import (
    DALFChoicesField,
    DALFModelAdmin,
    DALFRelatedField,
    DALFRelatedFieldAjax,
    DALFRelatedOnlyField,
)

from .models import Category, CategoryRenamed, Post, Tag


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
