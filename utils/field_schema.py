from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from utils.error_handler import ValidationError

class FieldType(str, Enum):
    """Supported field types"""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    NUMBER = "number"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    DATE = "date"
    DATETIME = "datetime"
    URL = "url"
    PASSWORD = "password"

class ValidationRule(str, Enum):
    """Validation rules"""
    REQUIRED = "required"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    PATTERN = "pattern"

@dataclass
class FieldValidation:
    """Field validation rules"""
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    custom_rules: List[str] = field(default_factory=list)

@dataclass
class FieldSchema:
    """Field schema definition"""
    field_name: str
    field_label: str
    field_type: FieldType
    section_name: str
    sort_order: int
    is_required: bool = False
    is_visible: bool = True
    validation: FieldValidation = None
    options: List[Dict[str, Any]] = field(default_factory=list)
    default_value: Any = None
    help_text: str = ""
    
    def __post_init__(self):
        if self.validation is None:
            self.validation = FieldValidation(required=self.is_required)
    
    def validate(self) -> List[str]:
        """Validate the field schema itself"""
        errors = []
        
        # Validate field name
        if not self.field_name or not self.field_name.strip():
            errors.append("Field name is required")
        elif not self.field_name.replace('_', '').isalnum():
            errors.append("Field name must contain only letters, numbers, and underscores")
        elif self.field_name[0].isdigit():
            errors.append("Field name cannot start with a number")
        
        # Validate field label
        if not self.field_label or not self.field_label.strip():
            errors.append("Field label is required")
        
        # Validate section name
        if not self.section_name or not self.section_name.strip():
            errors.append("Section name is required")
        
        # Validate sort order
        if self.sort_order < 0:
            errors.append("Sort order must be non-negative")
        
        # Validate field type specific rules
        if self.field_type in [FieldType.DROPDOWN, FieldType.RADIO]:
            if not self.options:
                errors.append(f"Field type '{self.field_type}' requires options")
        
        return errors
    
    def validate_value(self, value: Any) -> List[str]:
        """Validate a field value against the schema"""
        errors = []
        
        # Check required
        if self.validation.required and (value is None or value == ""):
            errors.append(f"Field '{self.field_label}' is required")
            return errors
        
        if value is None or value == "":
            return errors  # Skip validation for empty optional fields
        
        # Type-specific validation
        if self.field_type == FieldType.EMAIL:
            if not self._is_valid_email(value):
                errors.append(f"Field '{self.field_label}' must be a valid email address")
        
        elif self.field_type == FieldType.PHONE:
            if not self._is_valid_phone(value):
                errors.append(f"Field '{self.field_label}' must be a valid phone number")
        
        elif self.field_type == FieldType.URL:
            if not self._is_valid_url(value):
                errors.append(f"Field '{self.field_label}' must be a valid URL")
        
        elif self.field_type == FieldType.NUMBER:
            try:
                num_value = float(value)
                if self.validation.min_value is not None and num_value < self.validation.min_value:
                    errors.append(f"Field '{self.field_label}' must be at least {self.validation.min_value}")
                if self.validation.max_value is not None and num_value > self.validation.max_value:
                    errors.append(f"Field '{self.field_label}' must be at most {self.validation.max_value}")
            except (ValueError, TypeError):
                errors.append(f"Field '{self.field_label}' must be a valid number")
        
        # Length validation
        str_value = str(value)
        if self.validation.min_length is not None and len(str_value) < self.validation.min_length:
            errors.append(f"Field '{self.field_label}' must be at least {self.validation.min_length} characters")
        if self.validation.max_length is not None and len(str_value) > self.validation.max_length:
            errors.append(f"Field '{self.field_label}' must be at most {self.validation.max_length} characters")
        
        # Pattern validation
        if self.validation.pattern:
            import re
            if not re.match(self.validation.pattern, str_value):
                errors.append(f"Field '{self.field_label}' does not match required pattern")
        
        return errors
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        import re
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        return len(digits) >= 10 and len(digits) <= 15
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        import re
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        return re.match(pattern, url) is not None

class FieldSchemaManager:
    """Manager for field schemas"""
    
    def __init__(self):
        self.schemas: Dict[str, FieldSchema] = {}
    
    def add_schema(self, schema: FieldSchema) -> None:
        """Add a field schema"""
        # Validate the schema
        errors = schema.validate()
        if errors:
            raise ValidationError(f"Invalid field schema: {'; '.join(errors)}")
        
        key = f"{schema.section_name}.{schema.field_name}"
        self.schemas[key] = schema
    
    def get_schema(self, section_name: str, field_name: str) -> Optional[FieldSchema]:
        """Get a field schema"""
        key = f"{section_name}.{field_name}"
        return self.schemas.get(key)
    
    def validate_field_value(self, section_name: str, field_name: str, value: Any) -> List[str]:
        """Validate a field value"""
        schema = self.get_schema(section_name, field_name)
        if not schema:
            return [f"Unknown field: {section_name}.{field_name}"]
        
        return schema.validate_value(value)
    
    def get_section_schemas(self, section_name: str) -> List[FieldSchema]:
        """Get all schemas for a section"""
        return [
            schema for key, schema in self.schemas.items()
            if key.startswith(f"{section_name}.")
        ]
    
    def create_schema_from_dict(self, data: Dict[str, Any]) -> FieldSchema:
        """Create a field schema from dictionary data"""
        try:
            field_type = FieldType(data.get('field_type', 'text'))
            validation = FieldValidation(
                required=data.get('is_required', False),
                min_length=data.get('min_length'),
                max_length=data.get('max_length'),
                min_value=data.get('min_value'),
                max_value=data.get('max_value'),
                pattern=data.get('pattern')
            )
            
            return FieldSchema(
                field_name=data['field_name'],
                field_label=data['field_label'],
                field_type=field_type,
                section_name=data['section_name'],
                sort_order=data.get('sort_order', 0),
                is_required=data.get('is_required', False),
                is_visible=data.get('is_visible', True),
                validation=validation,
                options=data.get('options', []),
                default_value=data.get('default_value'),
                help_text=data.get('help_text', '')
            )
        except KeyError as e:
            raise ValidationError(f"Missing required field: {e}")
        except ValueError as e:
            raise ValidationError(f"Invalid field value: {e}")

# Global schema manager instance
schema_manager = FieldSchemaManager()
