"""
SQLAlchemy Blog Repository Implementation.
Implements BlogRepositoryInterface for SQLAlchemy.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from ..interfaces.blog_repository import BlogRepositoryInterface


class SQLAlchemyBlogRepository(BlogRepositoryInterface):
    """
    SQLAlchemy implementation of BlogRepositoryInterface.
    """
    
    def __init__(self, db, BlogModel):
        """
        Args:
            db: SQLAlchemy instance
            BlogModel: SQLAlchemy Blog model class
        """
        self.db = db
        self.BlogModel = BlogModel
    
    def create(self, blog_data: Dict[str, Any]) -> Any:
        """Create a new blog"""
        blog = self.BlogModel(**blog_data)
        self.db.session.add(blog)
        self.db.session.commit()
        return blog
    
    def update(self, blog_id: int, blog_data: Dict[str, Any]) -> Optional[Any]:
        """Update an existing blog"""
        blog = self.BlogModel.query.get(blog_id)
        if blog:
            for key, value in blog_data.items():
                setattr(blog, key, value)
            self.db.session.commit()
        return blog
    
    def delete(self, blog_id: int) -> bool:
        """Delete a blog"""
        blog = self.BlogModel.query.get(blog_id)
        if blog:
            self.db.session.delete(blog)
            self.db.session.commit()
            return True
        return False
    
    def find_by_id(self, blog_id: int) -> Optional[Any]:
        """Find blog by ID"""
        return self.BlogModel.query.get(blog_id)
    
    def find_by_slug(self, slug: str) -> Optional[Any]:
        """Find blog by slug"""
        return self.BlogModel.query.filter_by(slug=slug).first()
    
    def find_all(self, page: int = 1, per_page: int = 50) -> List[Any]:
        """Get all blogs with pagination"""
        return self.BlogModel.query.order_by(
            self.BlogModel.id.desc()
        ).paginate(page=page, per_page=per_page, error_out=False).items
    
    def to_dict(self, blog: Any) -> Dict[str, Any]:
        """Convert blog to dictionary"""
        if hasattr(blog, 'to_dict'):
            try:
                return blog.to_dict()
            except Exception as e:
                # If the model's to_dict fails (e.g. missing attribute), fall back to manual mapping
                pass
        
        # Fallback for basic model or if to_dict failed
        data = {
            "id": blog.id,
            "title": blog.title,
            "slug": blog.slug,
            "excerpt": getattr(blog, 'excerpt', getattr(blog, 'snippet', '')),
            "content": getattr(blog, 'content', ''),
            "image": getattr(blog, 'image', None),
            "author": getattr(blog, 'author', ''),
            "category": getattr(blog, 'category', 'blog'),
            "views": str(getattr(blog, 'views', '0')),
            "date": str(getattr(blog, 'date', '')),
            "editorjs_data": getattr(blog, 'editorjs_data', None)
        }
        
        # Handle tags vs tag
        if hasattr(blog, 'tags'):
            try:
                data["tags"] = [t.name for t in blog.tags]
            except Exception:
                data["tags"] = []
        elif hasattr(blog, 'tag'):
            data["tags"] = [blog.tag] if blog.tag else []
        else:
            data["tags"] = []
            
        return data