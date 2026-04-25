import logging


logger = logging.getLogger("hello.server_errors")


class ServerErrorLoggingMiddleware:
    """Log server-side exceptions with request context before Django returns a 500."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            user_context = f"{user.get_username()} (id={user.pk})"
        else:
            user_context = "anonymous"

        logger.exception(
            "Unhandled server error: method=%s path=%s query=%s user=%s "
            "remote_addr=%s user_agent=%s referer=%s",
            request.method,
            request.get_full_path(),
            dict(request.GET.lists()),
            user_context,
            request.META.get("REMOTE_ADDR", "unknown"),
            request.META.get("HTTP_USER_AGENT", "unknown"),
            request.META.get("HTTP_REFERER", "none"),
        )
        return None
