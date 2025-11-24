
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator


class WellMatchedPaginator(Paginator):
    """
    自定义分页器：当请求页码大于总页数时，自动返回最后一页；
    当页码无效（如非整数、<=0）时，交由父类处理（通常会抛出 EmptyPage）。
    """

    def validate_number(self, number):
        """
        验证页码有效性。
        - 若 number > 总页数 → 返回最后一页
        - 若 number 无法转为整数 或 <=0 → 交由父类处理（会抛出异常）
        """
        try:
            # 先尝试转为整数（Django 原生也要求是 int 或可转为 int 的字符串）
            page_number = int(number)
        except (TypeError, ValueError):
            # 无法转换：交给父类处理（会 raise EmptyPage）
            return super().validate_number(number)

        # 如果页码超出范围，返回最后一页（至少为 1）
        if page_number > self.num_pages:
            return max(1, self.num_pages)  # 防止 num_pages 为 0 时返回 0（页码从 1 开始）

        # 否则走默认校验逻辑（处理 <=0 等情况）
        return super().validate_number(number)


class StandardResultsSetPagination(PageNumberPagination):
    """
    标准分页配置：
    - 默认每页 10 条
    - 页码参数：?page=2
    - 每页数量参数：?limit=20（最大不超过 100）
    - 超出总页数时自动返回最后一页
    """
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = 100
    django_paginator_class = WellMatchedPaginator
