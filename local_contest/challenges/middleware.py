from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.decorators import login_required
from .utils import calculate_rank


class UpdateUserRankMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated:
            user = request.user
            user.rank = calculate_rank(user)[0]
            user.save()