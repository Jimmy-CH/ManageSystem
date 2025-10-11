
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination


class FrontendCompatiblePagination(PageNumberPagination):
    """
    适配前端 Pagination 组件（使用 limit 参数）
    """
    page_size = 20  # 默认每页数量，对应前端默认 limit: 20
    page_query_param = 'page'  # 页码参数名（默认就是 page，可不写）
    page_size_query_param = 'limit'  # 关键！前端传的是 limit，不是 page_size
    max_page_size = 100  # 最大每页数量，防止前端传超大值


class WellMatchedPaginator(Paginator):
    # 作用是 【参数中的page > page总数】 时，不会报错，而是使用最后一页
    def validate_number(self, number):
        try:
            if int(number) > self.num_pages:
                return self.num_pages
        except:
            pass

        return super().validate_number(number)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"  # 获取参数中传入的页码
    page_size_query_param = (
        "limit"  # 获取url参数中每页显示的数据条数，Defaults to `None`, meaning pagination is disabled.
    )
    django_paginator_class = WellMatchedPaginator
    max_page_size = 100
