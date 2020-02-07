from django.contrib import admin

#  导入ArticlePost
from .models import ArticlePost

from .models import ArticleColumn

# 注册ArticlePost到Admin中
admin.site.register(ArticlePost)

# 注册文章栏目
admin.site.register(ArticleColumn)
# Register your models here.
