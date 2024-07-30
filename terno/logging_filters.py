import logging
import platform


class LogFilter(logging.Filter):
    hostname = platform.node()

    def filter(self, record):
        record.hostname = LogFilter.hostname

        try:
            request = record.request
            record.clientip = request.META['REMOTE_ADDR']
            record.sessionid = request.session.session_key
            record.username = request.user.username
        except Exception:
            pass
        return True
