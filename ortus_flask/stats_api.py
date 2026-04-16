"""
Stats API Blueprint.
Handles likes and views for blog posts.
"""

import logging
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

def create_stats_api_blueprint():
    """
    Create stats API blueprint for likes and views.
    
    Returns:
        Flask Blueprint
    """
    
    stats_bp = Blueprint("ortus_stats_api", __name__, url_prefix="/api/blogs")
    
    @stats_bp.route("/<slug>/view", methods=["POST"])
    def increment_view(slug):
        try:
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            blog = BlogModel.query.filter_by(slug=slug).first()
            if not blog:
                return jsonify({"error": "Blog not found"}), 404
            
            # Increment views
            if hasattr(blog, 'views'):
                try:
                    current_views = int(blog.views or 0)
                    blog.views = str(current_views + 1)
                except (ValueError, TypeError):
                    blog.views = "1"
                    
                db.session.commit()
                return jsonify({"views": blog.views}), 200
            
            return jsonify({"error": "Stats not supported for this model"}), 400
            
        except Exception as e:
            logger.error(f"Error incrementing view: {e}")
            return jsonify({"error": str(e)}), 500
            
    @stats_bp.route("/<slug>/like", methods=["POST"])
    def toggle_like(slug):
        try:
            data = request.get_json() or {}
            browser_id = data.get("browser_id") or request.headers.get("X-Browser-Id")
            
            if not browser_id:
                return jsonify({"error": "Browser ID required"}), 400
                
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            blog = BlogModel.query.filter_by(slug=slug).first()
            if not blog:
                return jsonify({"error": "Blog not found"}), 404
            
            # Find Like model dynamically
            import sys
            LikeModel = None
            module = sys.modules.get(BlogModel.__module__, None)
            if module and hasattr(module, 'Like'):
                LikeModel = module.Like
            
            if not LikeModel:
                return jsonify({"error": "Likes not supported for this model"}), 400
                
            # Toggle like
            existing_like = LikeModel.query.filter_by(blog_id=blog.id, browser_id=browser_id).first()
            
            if existing_like:
                db.session.delete(existing_like)
                liked = False
            else:
                new_like = LikeModel(blog_id=blog.id, browser_id=browser_id)
                db.session.add(new_like)
                liked = True
                
            db.session.commit()
            
            # Get total likes
            total_likes = LikeModel.query.filter_by(blog_id=blog.id).count()
            
            return jsonify({
                "liked": liked,
                "likes": total_likes
            }), 200
            
        except Exception as e:
            logger.error(f"Error toggling like: {e}")
            return jsonify({"error": str(e)}), 500
            
    @stats_bp.route("/<slug>/stats", methods=["GET"])
    def get_stats(slug):
        try:
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            blog = BlogModel.query.filter_by(slug=slug).first()
            if not blog:
                return jsonify({"error": "Blog not found"}), 404
                
            stats = {
                "views": getattr(blog, 'views', '0')
            }
            
            # Try to get likes
            try:
                import sys
                module = sys.modules.get(BlogModel.__module__, None)
                if module and hasattr(module, 'Like'):
                    LikeModel = module.Like
                    stats["likes"] = LikeModel.query.filter_by(blog_id=blog.id).count()
                else:
                    stats["likes"] = 0
            except Exception:
                stats["likes"] = 0
                
            return jsonify(stats), 200
            
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return jsonify({"error": str(e)}), 500
            
    return stats_bp
