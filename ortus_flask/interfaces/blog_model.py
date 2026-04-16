"""
Blog Model Interface.
Defines contract for Blog model fields and methods.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BlogModelInterface(ABC):
    """
    Interface for Blog model.
    Implement this to define custom Blog model while maintaining compatibility.
    """
    
    # Required properties
    @property
    @abstractmethod
    def id(self) -> int:
        """Primary key"""
        pass
    
    @property
    @abstractmethod
    def title(self) -> str:
        """Blog title"""
        pass
    
    @title.setter
    @abstractmethod
    def title(self, value: str) -> None:
        pass
    
    @property
    @abstractmethod
    def slug(self) -> str:
        """URL-friendly slug (unique)"""
        pass
    
    @slug.setter
    @abstractmethod
    def slug(self, value: str) -> None:
        pass
    
    @property
    @abstractmethod
    def excerpt(self) -> str:
        """Short description"""
        pass
    
    @excerpt.setter
    @abstractmethod
    def excerpt(self, value: str) -> None:
        pass
    
    @property
    @abstractmethod
    def content(self) -> str:
        """HTML content"""
        pass
    
    @content.setter
    @abstractmethod
    def content(self, value: str) -> None:
        pass
    
    @property
    @abstractmethod
    def image(self) -> Optional[str]:
        """Cover image URL"""
        pass
    
    @image.setter
    @abstractmethod
    def image(self, value: Optional[str]) -> None:
        pass
    
    @property
    @abstractmethod
    def author(self) -> Optional[str]:
        """Author name"""
        pass
    
    @author.setter
    @abstractmethod
    def author(self, value: Optional[str]) -> None:
        pass
    
    @property
    @abstractmethod
    def tag(self) -> Optional[str]:
        """Tag/category"""
        pass
    
    @tag.setter
    @abstractmethod
    def tag(self, value: Optional[str]) -> None:
        pass
    
    @property
    @abstractmethod
    def category(self) -> Optional[str]:
        """Blog category"""
        pass
    
    @category.setter
    @abstractmethod
    def category(self, value: Optional[str]) -> None:
        pass
    
    @property
    @abstractmethod
    def date(self) -> str:
        """Publication date"""
        pass
    
    @date.setter
    @abstractmethod
    def date(self, value: str) -> None:
        pass
    
    # Optional properties
    @property
    def views(self) -> str:
        return "0"
    
    @views.setter
    def views(self, value: str) -> None:
        pass
    
    @property
    def editorjs_data(self) -> Optional[Dict]:
        return None
    
    @editorjs_data.setter
    def editorjs_data(self, value: Optional[Dict]) -> None:
        pass
    
    # Required method
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert blog to dictionary"""
        pass