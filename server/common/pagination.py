
from rest_framework.pagination import PageNumberPagination


class FrontendCompatiblePagination(PageNumberPagination):
    """
    适配前端 Pagination 组件（使用 limit 参数）
    """
    page_size = 20  # 默认每页数量，对应前端默认 limit: 20
    page_query_param = 'page'  # 页码参数名（默认就是 page，可不写）
    page_size_query_param = 'limit'  # ⭐ 关键！前端传的是 limit，不是 page_size
    max_page_size = 100  # 最大每页数量，防止前端传超大值

