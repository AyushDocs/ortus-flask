"""
Webhook Handler Interface.
Defines contract for processing incoming webhook events.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class WebhookHandlerInterface(ABC):
    """
    Interface for handling webhook events.
    Implement this to customize how webhooks are processed.
    """
    
    @abstractmethod
    def validate_signature(self, payload: str, signature: str) -> bool:
        """Validate webhook signature"""
        pass
    
    @abstractmethod
    def parse_payload(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse and extract blog data from webhook payload"""
        pass
    
    @abstractmethod
    def process_blog(self, blog_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize blog data"""
        pass
    
    @abstractmethod
    def create_or_update_blog(self, blog_data: Dict[str, Any]) -> Any:
        """Create or update blog in storage"""
        pass