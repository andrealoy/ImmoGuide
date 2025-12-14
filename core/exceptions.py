# core/exceptions.py

class SessionExpiredError(RuntimeError):
    """Raised when the browser session (cookies / headers) is no longer valid."""
    pass
