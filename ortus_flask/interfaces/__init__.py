"""
Interfaces package.
Contains all abstract interfaces for Ortus integration.
"""

from .blog_model import BlogModelInterface
from .blog_repository import BlogRepositoryInterface
from .webhook_handler import WebhookHandlerInterface

__all__ = [
    'BlogModelInterface',
    'BlogRepositoryInterface', 
    'WebhookHandlerInterface'
]