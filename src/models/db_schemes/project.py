from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectID

class Project(BaseModel):
    _id: Optional[str]
    project_id: str = Field(...,min_length=1)
    
    @field_validator('project_id')
    def validate_project(cls,value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return value