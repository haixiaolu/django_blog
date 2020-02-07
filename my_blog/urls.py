"""my_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import notifications.urls
from article.views import article_list

urlpatterns = [
    path('admin/', admin.site.urls),

    # 新增代码 配置app的url
    path('article/', include('article.urls', namespace='article')),

    # 用户管理
    path('userprofile/', include('userprofile.urls', namespace='userprofile')),

    # 密码重制
    path('password-reset/', include('password_reset.urls')),

    # 评论
    path('comment/', include('comment.urls', namespace='comment')),

    # 消息通知
    path('inbox/notifications/',
         include(notifications.urls, namespace='notifications')),

    # notice
    path('notice/', include('notice.urls', namespace='notice')),

    # allauth
    path('accounts/', include('allauth.urls')),

    # home
    path('', article_list, name='home'),


]

# 上传图像
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
