# Ortus Flask Integration

Ortus CMS integration package for Flask applications to enable:
- Webhook receiving for blog sync from Ortus CMS
- Authenticated API for Ortus to fetch blogs
- EditorJS data support

## Installation

```bash
pip install ortus-flask
```

## Usage

### 1. Update your Blog Model

Ensure your Blog model has the required fields:

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Blog(db.Model):
    __tablename__ = 'blogs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500))
    author = db.Column(db.String(100))
    tag = db.Column(db.String(50))
    category = db.Column(db.String(50))
    views = db.Column(db.String(20), default="0")
    date = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    editorjs_data = db.Column(db.JSON, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "excerpt": self.excerpt,
            "content": self.content,
            "image": self.image,
            "author": self.author,
            "tag": self.tag,
            "category": self.category,
            "views": self.views,
            "date": self.date,
            "editorjs_data": self.editorjs_data
        }
```

### 2. Initialize in your Flask app

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from ortus_flask import init_ortus
import os
from dotenv import load_dotenv

load_dotenv()  # Loads ORTUS_WEBHOOK_SECRET and ORTUS_API_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourapp.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import your Blog model
from models import Blog

# Initialize Ortus integration
app.config['ORTUS_WEBHOOK_SECRET'] = os.getenv('ORTUS_WEBHOOK_SECRET')
app.config['ORTUS_API_KEY'] = os.getenv('ORTUS_API_KEY')
init_ortus(app, db, Blog)
```

### 3. Add to your .env

```env
ORTUS_WEBHOOK_SECRET=your_webhook_secret
ORTUS_API_KEY=your_api_key
```

## API Endpoints

After integration, these endpoints are available:

- `POST /api/webhook/blog` - Receive blogs from Ortus
- `GET /api/webhook/config` - Get webhook configuration  
- `GET /api/sites/1/blogs` - Fetch all blogs (authenticated)

## Development

Install in editable mode:
```bash
pip install -e .
```

Build package:
```bash
python -m build
```