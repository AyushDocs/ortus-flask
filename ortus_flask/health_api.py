"""
Health Check API Blueprint.
Provides endpoints for checking service health.
"""

import logging
from flask import Blueprint, jsonify, current_app

logger = logging.getLogger(__name__)


def create_health_api_blueprint():
    """
    Create health check API blueprint.
    
    Returns:
        Flask Blueprint
    """
    
    health_bp = Blueprint("ortus_health", __name__, url_prefix="/api")
    
    @health_bp.route("/health", methods=["GET"])
    def health_check():
        """Basic health check - returns OK if server is running"""
        return jsonify({
            "status": "ok",
            "service": "ortus-flask"
        }), 200
    
    @health_bp.route("/health/detailed", methods=["GET"])
    def health_detailed():
        """Detailed health check - verifies database connection"""
        try:
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            health = {
                "status": "ok",
                "service": "ortus-flask",
                "database": "unknown"
            }
            
            if db:
                try:
                    db.session.execute(db.text('SELECT 1'))
                    health["database"] = "connected"
                except Exception as e:
                    health["status"] = "degraded"
                    health["database"] = f"error: {str(e)}"
            
            if BlogModel:
                health["blog_model"] = BlogModel.__name__
            
            status_code = 200 if health["status"] == "ok" else 503
            return jsonify(health), status_code
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return jsonify({
                "status": "error",
                "error": str(e)
            }), 500
    
    return health_bp
