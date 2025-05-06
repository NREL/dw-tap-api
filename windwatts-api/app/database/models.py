from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Float, Boolean
from sqlalchemy.sql import func
from .connection import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(String, nullable=True, index=True)  # Can be null for unauthenticated requests
    action = Column(String, index=True)  # e.g., "api_request", "login", "data_access"
    resource = Column(String, index=True)  # e.g., "/api/v1/forecast", "user_profile"
    method = Column(String, index=True)  # HTTP method or custom action
    status_code = Column(Integer, nullable=True, index=True)  # HTTP status code if applicable
    ip_address = Column(String, nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    request_data = Column(JSON, nullable=True)  # Store request payload if needed
    response_data = Column(JSON, nullable=True)  # Store response data if needed
    duration_ms = Column(Integer, nullable=True, index=True)  # Request duration in milliseconds
    error_message = Column(Text, nullable=True)  # Store error messages if any
    log_metadata = Column(JSON, nullable=True)  # Additional custom metadata
    
    # New fields for enhanced analytics
    api_version = Column(String, nullable=True, index=True)  # e.g., "v1", "v2"
    endpoint_category = Column(String, nullable=True, index=True)  # e.g., "forecast", "user", "admin"
    request_size_bytes = Column(Integer, nullable=True)  # Size of request payload
    response_size_bytes = Column(Integer, nullable=True)  # Size of response payload
    is_error = Column(Boolean, default=False, index=True)  # Whether the request resulted in an error
    error_type = Column(String, nullable=True, index=True)  # Type of error if any
    client_type = Column(String, nullable=True, index=True)  # e.g., "web", "mobile", "api"
    country = Column(String, nullable=True, index=True)  # Country derived from IP
    referrer = Column(String, nullable=True)  # HTTP referrer
    request_id = Column(String, nullable=True, index=True)  # Unique request identifier
    parent_request_id = Column(String, nullable=True, index=True)  # For tracking related requests
    tags = Column(JSON, nullable=True)  # Custom tags for grouping/filtering 