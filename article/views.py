# 导入模块
import markdown
# 引入redirect  重定向模块
from django.shortcuts import render, redirect
from django.http import HttpResponse

# 引入刚才定义的ArticlePostForm
from .forms import ArticlePostForm

# 引入User模型
from django.contrib.auth.models import User

# 导入数据模型ArticlePost
from .models import ArticlePost

#
from django.contrib.auth.decorators import login_required

# 引入分页模块
from django.core.paginator import Paginator

# 引入Q对象
from django.db.models import Q

from comment.models import Comment

# 引入栏目Model
from .models import ArticleColumn

# 引入评论表单
from comment.forms import CommentForm

from django.views import View


# 视图函数
def article_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集
    article_list = ArticlePost.objects.all()

    # 用户搜索逻辑
    # 搜索查询集
    if search:
        # if order == 'total_views':
        # 用Q对象进行联合搜索
        article_list = article_list.filter(
            # 模型的title字段查询，icontains是不区分大小写的包含
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )  # .order_by('-total_views')

        # else:
        article_list = ArticlePost.objects.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        # 将search参数充值为空
        # 为什么需要search = ''语句？如果用户没有搜索操作，
        # 则search = request.GET.get('search')会使得search = None
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

        # 根据GET请求中查询条件
        # 返回不同排序的对象数组
        # 查询集排序
    if order == 'total_views':
        # 按热度排序
        article_list = article_list.all().order_by('-total_views')
        # order = 'total_views'
        # else:
        #     # 取出所有博客文章
        #     article_list = ArticlePost.objects.all()
        #     order = 'normal'

    # 每页显示1篇文章
    paginator = Paginator(article_list, 3)

    # 获取url中的页码
    page = request.GET.get('page')

    # 将导航对象相应的页码内容返回给articles
    articles = paginator.get_page(page)

    # 需要传递给模版（templates） 的对象
    context = {'articles': articles, 'order': order,
               'search': search, 'column': column,
               'tag': tag, }
    # render函数，载入模版， 并返回context对象
    return render(request, 'article/list.html', context)


# 文章详情

# # 国风·周南·关雎


# **关关雎鸠，在河之洲。窈窕淑女，君子好逑**

# **参差荇菜，左右流之。窈窕淑女，寤寐求**


# + 列表一
# + 列表二
# + 列表二-1
# + 列表二-2


# ...python...


def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)

    # 取出文章评论
    comments = Comment.objects.filter(article=id)

    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])

    # 将markdown语法渲染成html样式
    # this one doesn't work
    md = markdown.Markdown(
        extensions=[
            # 包含 缩写、表格等常用扩展
            'markdown.extensions.extra',
            # 语法高亮扩展
            'markdown.extensions.codehilite',
            # 目录扩展
            'markdown.extensions.toc',
        ])

    article.body = md.convert(article.body)

    # 为评论引入表单
    comment_form = CommentForm()

    # 需要传递给模版的对象
    context = {'article': article, 'toc': md.toc,
               'comments': comments, 'comment_form': comment_form, }
    # 载入模版，并返回context对象
    return render(request, 'article/detail.html', context)


# 写文章的视图
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        # request.FILES 保存图片
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中，id=1的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户， 并传入次用户的id
            new_article.author = User.objects.get(id=request.user.id)

            # 栏目显示下拉菜单
            if request.POST['column'] != 'none':
                # 保存文章栏目
                new_article.column = ArticleColumn.objects.get(
                    id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()

            # 保存 tags 的多对的关系
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("article:article_list")

        # 如果不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误， 请重新填写。")
    # 如果用户请求获取数据
    else:

        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 文章栏目
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = {'article_post_form': article_post_form, 'columns': columns}
        # 返回模版
        return render(request, 'article/create.html', context)


# 删文章
def article_delete(request, id):
    # 根据 id 获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    # 调用 .delete()方法删除文章
    article.delete()
    # 完成删除后返回文章列表
    return redirect("article:article_list")


# 安全删除文章
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


# 更新文章
# 提醒用户登录
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新title， body字段
    GET方法进入初始表单页面
    id：文章的id
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)

    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    # 判断用户是否为POST提交表单数据
    if request.method == "POST":

        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)

        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():

            # 保存新写入的title，body数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']

            # 文章栏目
            if request.POST['column'] != 'none':
                # 保存文章栏目
                article.column = ArticleColumn.objects.get(
                    id=request.POST['column'])
            else:
                article.column = None

            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

            article.tags.set(*request.POST.get('tag').split(','), clear=True)
            article.save()

            # 完成后返回到修改后的文章中，需传入文章的id值
            return redirect("article:article_detail", id=id)

        # 如果数据不合法， 返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()

        columns = ArticleColumn.objects.all()

        # 赋值上下文， 将article文章对象也传递进去，以便提取旧放入内容
        context = {'article': article,
                   'article_post_form': article_post_form,
                   'columns': columns,
                   'tags': ','.join([x for x in article.tags.names()]),
                   }
        # 将响应返回到模版中
        return render(request, 'article/update.html', context)


# 点赞数+1
class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')
