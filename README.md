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

### 1. Initialize in your Flask app

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