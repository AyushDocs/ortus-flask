"""
Default Webhook Handler Implementation.
Implements WebhookHandlerInterface with standard Ortus payload format.
"""

import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from ..interfaces.webhook_handler import WebhookHandlerInterface
from ..interfaces.blog_repository import BlogRepositoryInterface


class DefaultWebhookHandler(WebhookHandlerInterface):
    """
    Default implementation for handling Ortus webhook events.
    """
    
    def __init__(self, repository: BlogRepositoryInterface, secret: str = ""):
        """
        Args:
            repository: Blog repository instance
            secret: Webhook secret for signature verification
        """
        self.repository = repository
        self.secret = secret
    
    def validate_signature(self, payload: str, signature: str) -> bool:
        """Validate webhook signature"""
        if not self.secret or not signature:
            return True
        expected = hmac.new(
            self.secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)
    
    def parse_payload(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse and extract blog data from webhook payload"""
        if not payload or "blog" not in payload:
            return None
        return payload["blog"]
    
    def process_blog(self, blog_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize blog data"""
        title = blog_data.get("title", "Untitled")
        
        # Generate slug
        slug = title.lower().replace(" ", "-")
        slug = "".join(c if c.isalnum() or c in "-_" else "" for c in slug)
        
        # Extract content
        content_json = blog_data.get("content_json", {})
        editorjs_data = content_json.get("editorjs")
        html_content = (
            blog_data.get("content") or 
            content_json.get("content", "") or 
            blog_data.get("snippet") or 
            blog_data.get("excerpt", "")[:200]
        )
        
        return {
            "title": title,
            "slug": slug,
            "excerpt": blog_data.get("snippet") or blog_data.get("excerpt", "")[:200],
            "content": html_content,
            "image": blog_data.get("image") or "",
            "author": blog_data.get("author") or "Ortus",
            "tag": blog_data.get("tag") or (
                blog_data.get("tags", "").split(",")[0] 
                if blog_data.get("tags") else None
            ),
            "category": blog_data.get("category") or "blog",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "editorjs_data": editorjs_data
        }
    
    def create_or_update_blog(self, blog_data: Dict[str, Any]) -> Any:
        """Create or update blog in storage"""
        processed = self.process_blog(blog_data)
        existing = self.repository.find_by_slug(processed["slug"])
        
        if existing:
            # Clean data for update (remove None values)
            update_data = {k: v for k, v in processed.items() if v}
            # Remove editorjs_data if None
            if 'editorjs_data' in update_data and not update_data['editorjs_data']:
                del update_data['editorjs_data']
            return self.repository.update(existing.id, update_data)
        else:
            # Clean data for create
            create_data = {k: v for k, v in processed.items() if v}
            return self.repository.create(create_data)