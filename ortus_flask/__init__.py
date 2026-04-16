"""
Ortus Flask Integration

Modular Ortus CMS integration for Flask applications.

Usage:
    from ortus_flask import init_ortus
    
    app.config['ORTUS_WEBHOOK_SECRET'] = 'your_secret'
    app.config['ORTUS_API_KEY'] = 'your_api_key'
    init_ortus(app, db, BlogModel)

For custom implementations, use interfaces:
    from ortus_flask.interfaces import BlogModelInterface, BlogRepositoryInterface
    from ortus_flask.implementations import SQLAlchemyBlogRepository, DefaultWebhookHandler
"""
import os
import logging
from importlib.metadata import version, PackageNotFoundError

logger = logging.getLogger(__name__)

try:
    __version__ = version("ortus-flask")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"



# Import submodules
from . import interfaces
from . import implementations

# Import main functions
from .webhook import create_ortus_webhook as create_webhook_blueprint
from .blogs_api import create_blogs_api_blueprint, create_compat_blueprint
from .images_api import create_image_api_blueprint
from .health_api import create_health_api_blueprint
from .stats_api import create_stats_api_blueprint
from .models import create_blog_models


def init_ortus(app, db, BlogModel):
    """
    Initialize complete Ortus integration with default implementations.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy instance
        BlogModel: SQLAlchemy model class for blogs
    
    Returns:
        Tuple of (webhook_bp, blogs_api_bp)
    """
    
    # Store config with defaults
    app.config.setdefault('ORTUS_WEBHOOK_SECRET', os.getenv('ORTUS_WEBHOOK_SECRET', ''))
    app.config.setdefault('ORTUS_API_KEY', os.getenv('ORTUS_API_KEY', ''))
    app.config['ORTUS_BLOG_MODEL'] = BlogModel
    app.config['ORTUS_DB'] = db
    
    # Set upload folder for images
    app.config.setdefault('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'uploads'))
    
    # Create and register blueprints
    webhook_bp = create_webhook_blueprint(app, db, BlogModel)
    app.register_blueprint(webhook_bp)
    
    blogs_api_bp = create_blogs_api_blueprint()
    app.register_blueprint(blogs_api_bp)
    
    # Register backwards-compatible endpoints
    compat_bp = create_compat_blueprint()
    app.register_blueprint(compat_bp)
    
    # Register image upload endpoints
    images_bp = create_image_api_blueprint()
    app.register_blueprint(images_bp)
    
    # Register health check endpoints
    health_bp = create_health_api_blueprint()
    app.register_blueprint(health_bp)
    
    # Register stats endpoints (likes/views)
    stats_bp = create_stats_api_blueprint()
    app.register_blueprint(stats_bp)
    
    logger.info("Ortus integration initialized")
    
    return webhook_bp, blogs_api_bp


# Convenience imports for common use cases
__all__ = [
    'init_ortus',
    'create_blog_models',
    'create_webhook_blueprint',
    'create_blogs_api_blueprint',
    'create_stats_api_blueprint',
    'interfaces',
    'implementations',
    'BlogModelInterface',
    'BlogRepositoryInterface',
    'WebhookHandlerInterface',
    'SQLAlchemyBlogRepository',
    'DefaultWebhookHandler'
]

# Import interfaces and implementations for convenience
from .interfaces import BlogModelInterface, BlogRepositoryInterface, WebhookHandlerInterface
from .implementations import SQLAlchemyBlogRepository, DefaultWebhookHandler