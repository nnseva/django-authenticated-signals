from django.utils.deprecation import MiddlewareMixin

from threading import local


class AuthenticatedSignalsMiddleware(MiddlewareMixin):
    thread_data = local()

    def process_request(self, request):
        if hasattr(self.thread_data, 'request'):
            raise Exception("Unknown race condition in authenticated signal middleware!")
        self.thread_data.request = request

    def process_response(self, request, response):
        del self.thread_data.request
        return response

    @classmethod
    def current_request(cls):
        return getattr(cls.thread_data, 'request', None)


def current_request():
    return AuthenticatedSignalsMiddleware.current_request()
