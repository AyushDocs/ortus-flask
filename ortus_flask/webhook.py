"""
Ortus webhook integration.
Provides endpoint to receive blogs from Ortus CMS.
"""

import os
import hmac
import hashlib
import logging
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

logger = logging.getLogger(__name__)


def verify_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook signature"""
    if not secret or not signature:
        return True
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


def _get_or_create_tags(db, tag_names, BlogModel):
    """Get or create tags and return list of Tag objects"""
    try:
        import sys
        module = sys.modules.get(BlogModel.__module__, None)
        if module and hasattr(module, 'Tag'):
            Tag = module.Tag
        else:
            return []
    except Exception:
        return []
    
    if not Tag or not tag_names:
        return []
    
    tags = []
    for name in tag_names:
        if not name:
            continue
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
        tags.append(tag)
    
    if tags:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return []
    
    return tags


def create_ortus_webhook(app, db, BlogModel):
    """
    Create Ortus webhook blueprint.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy instance
        BlogModel: SQLAlchemy model for blogs
    
    Returns:
        Blueprint for registration
    """
    
    webhook_bp = Blueprint("ortus_webhook", __name__, url_prefix="/api/webhook")
    
    @webhook_bp.route("/blog", methods=["POST"])
    def receive_blog():
        try:
            signature = request.headers.get("X-Signature", "")
            event_type = request.headers.get("X-Event-Type", "")
            
            if event_type and event_type != "blog.published":
                return jsonify({"error": "Unknown event type"}), 400
            
            payload = request.get_json()
            
            if not payload or "blog" not in payload:
                return jsonify({"error": "Invalid payload"}), 400
            
            blog_data = payload["blog"]
            
            secret = current_app.config.get("ORTUS_WEBHOOK_SECRET")
            if secret and not verify_signature(request.get_data(as_text=True), signature, secret):
                return jsonify({"error": "Invalid signature"}), 401
            
            title = blog_data.get("title", "Untitled")
            image = blog_data.get("image") or ""
            snippet = blog_data.get("snippet") or blog_data.get("excerpt", "")[:200]
            author = blog_data.get("author") or "Ortus"
            tags_input = blog_data.get("tags", [])
            if isinstance(tags_input, str):
                tags_input = [t.strip() for t in tags_input.split(",") if t.strip()]
            category = blog_data.get("category") or "blog"
            
            content_json = blog_data.get("content_json", {})
            # If content_json contains 'editorjs' key, use it; otherwise assume content_json IS the editorjs data if it has 'blocks'
            editorjs_data = content_json.get("editorjs")
            if not editorjs_data and isinstance(content_json, dict) and 'blocks' in content_json:
                editorjs_data = content_json
            
            # We now exclusively use editorjs_data for content
            if not editorjs_data:
                 # Fallback to creating a single paragraph from legacy content if needed, 
                 # but usually we expect full editorjs_data now.
                 pass
            
            # Uniquely identify blog by remote_id (the ID from the source Ortus site) or slug
            remote_id = blog_data.get("remote_id") or blog_data.get("id")
            slug = blog_data.get("slug")
            
            existing = None
            if remote_id:
                # First try to find by our tracked remote_id field
                if hasattr(BlogModel, 'remote_id'):
                    existing = BlogModel.query.filter_by(remote_id=str(remote_id)).first()
                
                # If not found and it's an integer, it MIGHT be a legacy direct ID match (less likely but safe)
                if not existing:
                    try:
                        existing = db.session.get(BlogModel, int(remote_id))
                    except Exception:
                        pass
            
            # Fallback to slug match
            if not existing and slug:
                existing = BlogModel.query.filter_by(slug=slug).first()
            
            if not slug:
                slug = title.lower().replace(" ", "-")
                slug = "".join(c if c.isalnum() or c in "-_" else "" for c in slug)
            
            if existing:
                existing.title = title
                # Handle snippet/excerpt naming differences
                if hasattr(existing, 'snippet'):
                    existing.snippet = snippet
                elif hasattr(existing, 'excerpt'):
                    existing.excerpt = snippet
                
                existing.slug = slug
                existing.image = image if image else None
                existing.author = author
                
                if hasattr(existing, 'category'):
                    existing.category = category
                    
                if hasattr(existing, 'tags'):
                    existing.tags = _get_or_create_tags(db, tags_input, BlogModel)
                    
                if hasattr(existing, 'editorjs_data'):
                    existing.editorjs_data = editorjs_data if editorjs_data else None
                
                # Handle date field gracefully
                if hasattr(existing, 'date'):
                    try:
                        existing.date = datetime.now()
                    except Exception:
                        existing.date = datetime.now().strftime("%Y-%m-%d")

                # Ensure remote_id is tracked if model supports it
                if hasattr(existing, 'remote_id') and remote_id:
                    existing.remote_id = str(remote_id)
                        
                db.session.commit()
                return jsonify({
                    "msg": "Blog updated successfully",
                    "id": existing.id,
                    "slug": existing.slug,
                    "updated": True
                }), 200
            
            # Create new blog with flexible attribute mapping
            blog_args = {
                "slug": slug,
                "title": title,
                "image": image if image else None,
                "author": author,
            }
            
            # Add optional fields if they exist in the model
            dummy_blog = BlogModel()
            if hasattr(dummy_blog, 'snippet'): blog_args['snippet'] = snippet
            elif hasattr(dummy_blog, 'excerpt'): blog_args['excerpt'] = snippet
            
            if hasattr(dummy_blog, 'category'): blog_args['category'] = category
            
            if hasattr(dummy_blog, 'date'):
                try:
                    blog_args['date'] = datetime.now()
                except Exception:
                    blog_args['date'] = datetime.now().strftime("%Y-%m-%d")

            if hasattr(BlogModel, 'remote_id') and remote_id:
                blog_args['remote_id'] = str(remote_id)

            new_blog = BlogModel(**blog_args)
            
            if hasattr(BlogModel, 'tags'):
                new_blog.tags = _get_or_create_tags(db, tags_input, BlogModel)
            
            if hasattr(BlogModel, 'editorjs_data'):
                new_blog.editorjs_data = editorjs_data if editorjs_data else None
            
            db.session.add(new_blog)
            db.session.commit()
            
            return jsonify({
                "msg": "Blog created successfully",
                "id": new_blog.id,
                "slug": new_blog.slug
            }), 201
            
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @webhook_bp.route("/config", methods=["GET"])
    def get_webhook_config():
        secret = current_app.config.get("ORTUS_WEBHOOK_SECRET", "")
        webhook_url = request.host_url + "api/webhook/blog"
        return jsonify({
            "webhook_url": webhook_url,
            "secret": secret,
            "configured": bool(secret)
        })
    
    logger.info("Ortus webhook endpoint registered at /api/webhook")
    return webhook_bp


# Alias for compatibility
create_webhook_blueprint = create_ortus_webhook