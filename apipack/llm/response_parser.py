"""
Response Parser for LLM API responses.

This module provides the ResponseParser class which is responsible for parsing
and validating responses from the LLM API.
"""
from typing import Dict, Any, Optional, List, TypeVar, Generic, Type
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)

class ResponseParser(Generic[T]):
    """Parser for LLM API responses.
    
    This class handles parsing and validating responses from the LLM API
    into strongly-typed Python objects using Pydantic models.
    """
    
    def __init__(self, response_model: Type[T]):
        """Initialize the response parser with a response model.
        
        Args:
            response_model: A Pydantic model class that defines the expected
                         response structure.
        """
        self.response_model = response_model
    
    def parse(self, response_data: Dict[str, Any]) -> T:
        """Parse and validate the response data.
        
        Args:
            response_data: The raw response data from the LLM API.
            
        Returns:
            An instance of the response model with the parsed data.
            
        Raises:
            ValidationError: If the response data doesn't match the expected schema.
        """
        try:
            return self.response_model(**response_data)
        except ValidationError as e:
            # Log the validation error for debugging
            print(f"Validation error parsing LLM response: {e}")
            raise
    
    def parse_streaming_response(self, chunks: List[Dict[str, Any]]) -> T:
        """Parse a streaming response from the LLM API.
        
        Args:
            chunks: List of response chunks from a streaming API call.
            
        Returns:
            An instance of the response model with the combined data.
        """
        # Combine chunks into a single response
        combined = {}
        for chunk in chunks:
            combined.update(chunk)
        return self.parse(combined)
    
    @classmethod
    def get_default_parser(cls, response_model: Type[T]) -> 'ResponseParser[T]':
        """Create a default parser for a response model.
        
        Args:
            response_model: The Pydantic model class for the response.
            
        Returns:
            A ResponseParser instance configured for the given model.
        """
        return cls(response_model)
