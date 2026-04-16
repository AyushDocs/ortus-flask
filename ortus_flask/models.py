"""
Blog models and factories.
Provides standardized models for blogs, tags, and likes.
"""

from datetime import datetime
from sqlalchemy import UniqueConstraint

def create_blog_models(db, tag_model_name='Tag', tag_table_name='tags', blog_tag_table_name='blog_tags'):
    """
    Factory function to create standardized SQLAlchemy models.
    
    Returns:
        tuple: (BlogPost, Tag, Like) model classes
    """
    
    # Association table for many-to-many relationship
    blog_tags = db.Table(blog_tag_table_name,
        db.Column('blog_id', db.Integer, db.ForeignKey('blog_posts.id'), primary_key=True),
        db.Column('tag_id', db.Integer, db.ForeignKey(f'{tag_table_name}.id'), primary_key=True)
    )

    # Dynamically define the Tag class with the chosen name
    class_attrs = {
        '__tablename__': tag_table_name,
        'id': db.Column(db.Integer, primary_key=True),
        'name': db.Column(db.String(100), unique=True, nullable=False),
        'to_dict': lambda self: {"id": self.id, "name": self.name}
    }
    
    TagModel = type(tag_model_name, (db.Model,), class_attrs)

    class BlogPost(db.Model):
        __tablename__ = 'blog_posts'
        id = db.Column(db.Integer, primary_key=True)
        slug = db.Column(db.String(255), unique=True, nullable=False)
        title = db.Column(db.String(255), nullable=False)
        date = db.Column(db.String(20), nullable=False)
        author = db.Column(db.String(100), nullable=False)
        image = db.Column(db.String(500), nullable=False)
        excerpt = db.Column(db.Text, nullable=False)
        category = db.Column(db.String(50), default="blog")
        editorjs_data = db.Column(db.JSON, nullable=True)
        views = db.Column(db.String(20), default="0")
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        remote_id = db.Column(db.String(255), nullable=True) # For sync tracking
        
        # Relationship with tags
        tags = db.relationship(TagModel, secondary=blog_tags, lazy='subquery',
            backref=db.backref('blogs', lazy=True))
        
        def to_dict(self):
            return {
                "id": self.id,
                "slug": self.slug,
                "title": self.title,
                "date": self.date,
                "tag": [tag.to_dict() for tag in self.tags], # Keep legacy 'tag' for frontend
                "tags": [tag.name for tag in self.tags],    # Add 'tags' strings
                "author": self.author,
                "image": self.image,
                "excerpt": self.excerpt,
                "snippet": self.excerpt,
                "category": self.category,
                "editorjs_data": self.editorjs_data,
                "views": self.views,
                "remote_id": self.remote_id
            }

    class Like(db.Model):
        __tablename__ = 'likes'
        id = db.Column(db.Integer, primary_key=True)
        browser_id = db.Column(db.String(255), nullable=False)
        blog_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
        
        __table_args__ = (UniqueConstraint('browser_id', 'blog_id', name='unique_like'),)
        
        def to_dict(self):
            return {
                "id": self.id,
                "browser_id": self.browser_id,
                "blog_id": self.blog_id
            }

    return BlogPost, TagModel, Like