from django.http import JsonResponse
from user.models import User, UserReviewList
from django.apps import apps
from django.db.models import Q

def get_unreview_list(request, unreview_kind, *args, **kwargs):
    """Get Unreview List.
    ログインしているユーザーの未レビューの最新５件を返す。
    デフォルトで未レビュー一覧ページへのリンクがある。
    """
    pass
