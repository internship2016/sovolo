from django.utils.deprecation import MiddlewareMixin
from debug_toolbar.middleware import DebugToolbarMiddleware


class AtopdedTo110DebugMiddleware(MiddlewareMixin, DebugToolbarMiddleware):
    pass
