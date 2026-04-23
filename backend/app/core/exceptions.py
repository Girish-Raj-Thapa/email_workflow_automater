class AppError(Exception):
    """Base application exception."""
    pass


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""
    pass


class EmailNotFoundError(NotFoundError):
    """Raised when an email is not found."""
    pass


class ConflictError(AppError):
    """Raised when a resource conflicts with current state."""
    pass


class AIAnalysisAlreadyExistsError(ConflictError):
    """Raised when an email already has an AI analysis."""
    pass

class AIAnalysisError(AppError):
    """Raised when AI analysis fails."""
    pass