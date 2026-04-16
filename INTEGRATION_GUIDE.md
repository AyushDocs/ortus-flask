# Ortus Integration Guide

This guide explains how to integrate `ortus-flask` package into any Flask project to enable blog management from Ortus CMS.

## Overview

`ortus-flask` is a modular Flask package that provides:
- Webhook endpoints to receive blogs from Ortus CMS
- REST API for fetching/managing blogs locally
- Image upload endpoints for blog covers and EditorJS images
- Health check endpoints for monitoring
- Tags support (many-to-many relationship)

## Quick Start

### 1. Install the Package

```bash
pip install ortus-flask
```

### 2. Configure Your Flask App

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ortus_flask import init_ortus
from your_models import Blog  # Your Blog model

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Required: Set Ortus credentials
app.config['ORTUS_WEBHOOK_SECRET'] = 'your_webhook_secret'
app.config['ORTUS_API_KEY'] = 'your_api_key'

# Optional: Set upload folder for images
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

# Initialize Ortus integration
init_ortus(app, db, Blog)
```

## Your Blog Model Requirements

Your Blog model must have these fields:

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

blog_tags = db.Table('blog_tags',
    db.Column('blog_id', db.Integer, db.ForeignKey('blogs.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    blogs = db.relationship('Blog', secondary=blog_tags, back_populates='tags')

class Blog(db.Model):
    __tablename__ = 'blogs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500))  # Cover image URL
    author = db.Column(db.String(100))
    category = db.Column(db.String(50))
    views = db.Column(db.String(20), default="0")
    date = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    editorjs_data = db.Column(db.JSON, nullable=True)  # EditorJS JSON format
    
    tags = db.relationship('Tag', secondary=blog_tags, back_populates='blogs')
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "excerpt": self.excerpt,
            "content": self.content,
            "image": self.image,
            "author": self.author,
            "tags": [t.name for t in self.tags] if self.tags else [],
            "category": self.category,
            "views": self.views,
            "date": self.date,
            "editorjs_data": self.editorjs_data
        }
```

Create tables:
```bash
flask db create  # or your migration command
```

## Available Endpoints

### Webhook (Receive from Ortus)
- `POST /api/webhook/blog` - Receive blog posts from Ortus CMS
- `POST /api/webhook/config` - Register webhook configuration

### Blogs API (Authenticated)
- `GET /api/sites/1/blogs` - List all blogs (requires X-API-Key header)
- `GET /api/sites/1/blogs/tags` - List all unique tags

### Blog CRUD (Backwards Compatible)
- `GET /api/blogs` - List blogs (supports ?page, ?per_page, ?category, ?tag)
- `GET /api/blogs/<slug>` - Get single blog by slug
- `POST /api/blogs` - Create new blog
- `PUT /api/blogs/<slug>` - Update blog
- `DELETE /api/blogs/<slug>` - Delete blog

### Images API
- `POST /api/images/upload` - Upload cover image (multipart/form-data)
- `POST /api/images/editorjs` - Upload EditorJS inline images
- `GET /api/images/view/<filename>` - Serve uploaded image
- `DELETE /api/images/delete/<filename>` - Delete image

### Health Check
- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Health check with database status

## Authentication

All authenticated endpoints require either:
- `X-API-Key` header with the API key
- `X-API-Key` header with the webhook secret

The package accepts either `ORTUS_API_KEY` or `ORTUS_WEBHOOK_SECRET` as valid keys.

## Configuration Options

| Config Key | Required | Default | Description |
|------------|----------|---------|--------------|
| `ORTUS_WEBHOOK_SECRET` | No | env var | Secret for webhook verification |
| `ORTUS_API_KEY` | No | env var | API key for authenticated requests |
| `ORTUS_BLOG_MODEL` | Yes (auto) | - | Set automatically by init_ortus |
| `ORTUS_DB` | Yes (auto) | - | Set automatically by init_ortus |
| `UPLOAD_FOLDER` | No | `uploads` | Directory for uploaded images |

## Ortus CMS Side Configuration

In Ortus admin panel for each site:

1. Go to Site Settings
2. Set Webhook URL: `http://your-domain.com/api/webhook/blog`
3. A webhook secret will be generated automatically
4. Use the same secret in your Flask app's `ORTUS_WEBHOOK_SECRET` config

## Webhook Payload Format

Ortus sends this payload structure:

```json
{
  "event": "blog.published",
  "site_id": 1,
  "site_name": "My Site",
  "blog": {
    "id": 123,
    "title": "My Blog Post",
    "content_json": { "blocks": [...] },
    "snippet": "Short description...",
    "image": "https://...",
    "author": "John Doe",
    "tags": ["tech", "news"],
    "published_at": "2026-04-07T12:00:00Z"
  }
}
```

## Development vs Production

### Development
```bash
# Run Flask in non-debug mode for file uploads to work
python app.py  # debug=True won't work well with uploads
```

### Production
Use a production WSGI server (gunicorn, waitress, etc.):

```bash
gunicorn -w 4 "app:create_app()" --bind 0.0.0.0:5000
```

## Environment Variables

Create a `.env` file:

```bash
FLASK_SECRET_KEY=your-secret-key
SQLALCHEMY_DATABASE_URI=sqlite:///your.db
ORTUS_WEBHOOK_SECRET=ortus_webhook_secret_change_me
ORTUS_API_KEY=your_api_key_secure_123
```

## Troubleshooting

### Images not uploading
- Ensure Flask is running in non-debug mode or with `use_reloader=False`
- Check the `UPLOAD_FOLDER` exists and is writable

### 401 Unauthorized
- Verify `ORTUS_WEBHOOK_SECRET` or `ORTUS_API_KEY` matches between Ortus and your app

### Tags not syncing
- Ensure your Blog model has the `tags` relationship defined
- Ensure `Tag` model exists with proper relationship

## Package Repository

The package is available on PyPI: https://pypi.org/project/ortus-flask/

To update:
```bash
cd /path/to/ortus-integration
rm -rf dist/ build/ *.egg-info
python -m build
twine upload dist/ortus_flask-*.whl
```

## File Structure Reference

```
ortus-integration/
├── ortus_flask/
│   ├── __init__.py          # Main entry point, init_ortus()
│   ├── webhook.py           # Webhook endpoint handlers
│   ├── blogs_api.py         # Blog CRUD API
│   ├── images_api.py         # Image upload endpoints
│   ├── health_api.py        # Health check endpoints
│   ├── models.py            # Base models (optional)
│   ├── interfaces/          # SOLID interfaces
│   └── implementations/      # Default implementations
├── pyproject.toml
└── README.md
```
