"""
Blogs API Blueprint.
Creates Flask blueprint for authenticated blog listing.
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)


def create_blogs_api_blueprint():
    """
    Create blogs API blueprint.
    
    Returns:
        Flask Blueprint
    """
    
    blogs_bp = Blueprint("ortus_blogs_api", __name__, url_prefix="/api/sites")
    
    @blogs_bp.route("/1/blogs", methods=["GET"])
    @blogs_bp.route("/<int:site_id>/blogs", methods=["GET"])
    def get_blogs(site_id: int = 1):
        try:
            # Authenticate
            api_key = request.headers.get("X-API-Key", "")
            expected_key = current_app.config.get("ORTUS_API_KEY", "")
            webhook_secret = current_app.config.get("ORTUS_WEBHOOK_SECRET", "")
            
            is_valid = False
            if api_key and expected_key and api_key == expected_key:
                is_valid = True
            elif api_key and webhook_secret and api_key == webhook_secret:
                is_valid = True
            elif not expected_key and not webhook_secret:
                is_valid = True
            
            if not is_valid:
                return jsonify({"error": "Unauthorized"}), 401
            
            # Get pagination params
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            
            # Get blogs from repository - use app.config stored db
            from ortus_flask.implementations import SQLAlchemyBlogRepository
            
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            if not db:
                from flask_sqlalchemy import SQLAlchemy
                sqla_ext = current_app.extensions.get('sqlalchemy')
                if sqla_ext:
                    db = sqla_ext.db
                else:
                    db = SQLAlchemy()
            
            repo = SQLAlchemyBlogRepository(db, BlogModel)
            
            blogs = repo.find_all(page, per_page)
            blogs_data = [repo.to_dict(b) for b in blogs]
            
            return jsonify({
                "blogs": blogs_data,
                "total": len(blogs_data),
                "pages": 1,
                "current_page": page
            }), 200
            
        except Exception as e:
            import traceback
            error_msg = f"Error fetching blogs: {str(e)}\n{traceback.format_exc()}"
            print(error_msg) # Direct print for visibility in console
            logger.error(error_msg)
            return jsonify({"error": str(e), "traceback": traceback.format_exc() if current_app.debug else None}), 500
    
    @blogs_bp.route("/1/blogs/tags", methods=["GET"])
    @blogs_bp.route("/<int:site_id>/blogs/tags", methods=["GET"])
    def get_tags(site_id: int = 1):
        try:
            api_key = request.headers.get("X-API-Key", "")
            expected_key = current_app.config.get("ORTUS_API_KEY", "")
            webhook_secret = current_app.config.get("ORTUS_WEBHOOK_SECRET", "")
            
            is_valid = False
            if api_key and expected_key and api_key == expected_key:
                is_valid = True
            elif api_key and webhook_secret and api_key == webhook_secret:
                is_valid = True
            elif not expected_key and not webhook_secret:
                is_valid = True
            
            if not is_valid:
                return jsonify({"error": "Unauthorized"}), 401
            
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            if not db:
                from flask_sqlalchemy import SQLAlchemy
                sqla_ext = current_app.extensions.get('sqlalchemy')
                if sqla_ext:
                    db = sqla_ext.db
            
            try:
                import sys
                module = sys.modules.get(BlogModel.__module__, None)
                if module and hasattr(module, 'Tag'):
                    Tag = module.Tag
                    all_tags = db.session.query(Tag.name).distinct().all()
                    tags_list = [t[0] for t in all_tags if t[0]]
                else:
                    tags_list = []
            except Exception as e:
                logger.error(f"Error querying tags: {e}")
                tags_list = []
            
            return jsonify(tags_list), 200
            
        except Exception as e:
            logger.error(f"Error fetching tags: {e}")
            return jsonify({"error": str(e)}), 500
    
    return blogs_bp


def create_compat_blueprint():
    """Create backwards-compatible blueprint for legacy /api/blogs endpoints"""
    
    compat_bp = Blueprint("ortus_compat", __name__, url_prefix="/api")
    
    @compat_bp.route("/blogs", methods=["GET"])
    def get_blogs():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 6, type=int)
            category = request.args.get('category', 'blog')
            tag = request.args.get('tag', '')
            
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            if not db:
                from flask_sqlalchemy import SQLAlchemy
                sqla_ext = current_app.extensions.get('sqlalchemy')
                if sqla_ext:
                    db = sqla_ext.db
            
            from ortus_flask.implementations import SQLAlchemyBlogRepository
            repo = SQLAlchemyBlogRepository(db, BlogModel)
            
            blogs = repo.find_all(page, per_page)
            blogs_data = [repo.to_dict(b) for b in blogs]
            
            if category:
                blogs_data = [b for b in blogs_data if b.get('category') == category]
            if tag:
                blogs_data = [b for b in blogs_data if b.get('tags') and tag in b.get('tags', [])]
            
            return jsonify({
                "blogs": blogs_data,
                "total": len(blogs_data),
                "pages": 1,
                "current_page": page
            }), 200
            
        except Exception as e:
            logger.error(f"Error fetching blogs: {e}")
            return jsonify({"error": str(e)}), 500
    
    @compat_bp.route("/blogs/tags", methods=["GET"])
    def get_tags():
        try:
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            if not db:
                from flask_sqlalchemy import SQLAlchemy
                sqla_ext = current_app.extensions.get('sqlalchemy')
                if sqla_ext:
                    db = sqla_ext.db
            
            try:
                import sys
                module = sys.modules.get(BlogModel.__module__, None)
                if module and hasattr(module, 'Tag'):
                    Tag = module.Tag
                    all_tags = db.session.query(Tag.name).distinct().all()
                    tags_list = [t[0] for t in all_tags if t[0]]
                else:
                    tags_list = []
            except Exception:
                tags_list = []
            
            return jsonify(tags_list), 200
            
        except Exception as e:
            logger.error(f"Error fetching tags: {e}")
            return jsonify({"error": str(e)}), 500
    
    @compat_bp.route("/blogs/<slug>", methods=["GET"])
    def get_blog_by_slug(slug):
        try:
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            if not db:
                from flask_sqlalchemy import SQLAlchemy
                sqla_ext = current_app.extensions.get('sqlalchemy')
                if sqla_ext:
                    db = sqla_ext.db
            
            from ortus_flask.implementations import SQLAlchemyBlogRepository
            repo = SQLAlchemyBlogRepository(db, BlogModel)
            
            blog = repo.find_by_slug(slug)
            if not blog:
                return jsonify({"error": "Blog not found"}), 404
            
            return jsonify(repo.to_dict(blog)), 200
            
        except Exception as e:
            logger.error(f"Error fetching blog: {e}")
            return jsonify({"error": str(e)}), 500
    
    @compat_bp.route("/blogs", methods=["POST"])
    def create_blog():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            if not db:
                from flask_sqlalchemy import SQLAlchemy
                sqla_ext = current_app.extensions.get('sqlalchemy')
                if sqla_ext:
                    db = sqla_ext.db
            
            title = data.get("title")
            slug = data.get("slug") or title.lower().replace(" ", "-")
            slug = "".join(c if c.isalnum() or c in "-_" else "" for c in slug)
            
            existing = BlogModel.query.filter_by(slug=slug).first()
            if existing:
                return jsonify({"error": "Blog with this slug already exists"}), 400
            
            blog_data = {
                "title": title,
                "slug": slug,
                "excerpt": data.get("excerpt", ""),
                "content": data.get("content", ""),
                "image": data.get("image"),
                "author": data.get("author", "Admin"),
                "category": data.get("category", "blog"),
                "date": data.get("date", datetime.now().strftime("%Y-%m-%d"))
            }
            
            if hasattr(BlogModel, 'editorjs_data'):
                blog_data['editorjs_data'] = data.get("editorjs_data")
            
            new_blog = BlogModel(**blog_data)
            
            if 'tags' in data and hasattr(BlogModel, 'tags'):
                try:
                    import sys
                    module = sys.modules.get(BlogModel.__module__, None)
                    if module and hasattr(module, 'Tag'):
                        Tag = module.Tag
                        tags = []
                        for tag_name in data.get('tags', []):
                            tag = Tag.query.filter_by(name=tag_name).first()
                            if not tag:
                                tag = Tag(name=tag_name)
                                db.session.add(tag)
                            tags.append(tag)
                        new_blog.tags = tags
                except Exception as e:
                    logger.warning(f"Could not set tags: {e}")
            
            from ortus_flask.implementations import SQLAlchemyBlogRepository
            repo = SQLAlchemyBlogRepository(db, BlogModel)
            return jsonify(repo.to_dict(new_blog)), 201
            
        except Exception as e:
            logger.error(f"Error creating blog: {e}")
            return jsonify({"error": str(e)}), 500
    
    @compat_bp.route("/blogs/<slug>", methods=["PUT"])
    def update_blog(slug):
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            if not db:
                from flask_sqlalchemy import SQLAlchemy
                sqla_ext = current_app.extensions.get('sqlalchemy')
                if sqla_ext:
                    db = sqla_ext.db
            
            blog = BlogModel.query.filter_by(slug=slug).first()
            if not blog:
                return jsonify({"error": "Blog not found"}), 404
            
            if 'title' in data:
                blog.title = data['title']
            if 'excerpt' in data:
                blog.excerpt = data['excerpt']
            if 'content' in data:
                blog.content = data['content']
            if 'image' in data:
                blog.image = data['image']
            if 'author' in data:
                blog.author = data['author']
            if 'category' in data:
                blog.category = data['category']
            if 'date' in data:
                blog.date = data['date']
            if 'editorjs_data' in data and hasattr(blog, 'editorjs_data'):
                blog.editorjs_data = data['editorjs_data']
            
            if 'tags' in data and hasattr(blog, 'tags'):
                try:
                    import sys
                    module = sys.modules.get(BlogModel.__module__, None)
                    if module and hasattr(module, 'Tag'):
                        Tag = module.Tag
                        tags = []
                        for tag_name in data.get('tags', []):
                            tag = Tag.query.filter_by(name=tag_name).first()
                            if not tag:
                                tag = Tag(name=tag_name)
                                db.session.add(tag)
                            tags.append(tag)
                        blog.tags = tags
                except Exception as e:
                    logger.warning(f"Could not update tags: {e}")
            
            db.session.commit()
            
            from ortus_flask.implementations import SQLAlchemyBlogRepository
            repo = SQLAlchemyBlogRepository(db, BlogModel)
            return jsonify({"msg": "Blog updated", "blog": repo.to_dict(blog)}), 200
            
        except Exception as e:
            logger.error(f"Error updating blog: {e}")
            return jsonify({"error": str(e)}), 500
    
    @compat_bp.route("/blogs/<slug>", methods=["DELETE"])
    def delete_blog(slug):
        try:
            BlogModel = current_app.config.get('ORTUS_BLOG_MODEL')
            db = current_app.config.get('ORTUS_DB')
            
            if not db:
                from flask_sqlalchemy import SQLAlchemy
                sqla_ext = current_app.extensions.get('sqlalchemy')
                if sqla_ext:
                    db = sqla_ext.db
            
            blog = BlogModel.query.filter_by(slug=slug).first()
            if not blog:
                return jsonify({"error": "Blog not found"}), 404
            
            db.session.delete(blog)
            db.session.commit()
            
            return jsonify({"msg": "Blog deleted"}), 200
            
        except Exception as e:
            logger.error(f"Error deleting blog: {e}")
            return jsonify({"error": str(e)}), 500
    
    return compat_bp