"""
Blog Repository Interface.
Defines contract for blog data access operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BlogRepositoryInterface(ABC):
    """
    Interface for blog data operations.
    Implement this to define how blogs are stored/retrieved.
    """
    
    @abstractmethod
    def create(self, blog_data: Dict[str, Any]) -> Any:
        """Create a new blog"""
        pass
    
    @abstractmethod
    def update(self, blog_id: int, blog_data: Dict[str, Any]) -> Optional[Any]:
        """Update an existing blog"""
        pass
    
    @abstractmethod
    def delete(self, blog_id: int) -> bool:
        """Delete a blog"""
        pass
    
    @abstractmethod
    def find_by_id(self, blog_id: int) -> Optional[Any]:
        """Find blog by ID"""
        pass
    
    @abstractmethod
    def find_by_slug(self, slug: str) -> Optional[Any]:
        """Find blog by slug"""
        pass
    
    @abstractmethod
    def find_all(self, page: int = 1, per_page: int = 50) -> List[Any]:
        """Get all blogs with pagination"""
        pass
    
    @abstractmethod
    def to_dict(self, blog: Any) -> Dict[str, Any]:
        """Convert blog to dictionary"""
        pass