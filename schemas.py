from pydantic import BaseModel, Field

# Schema for creating a new fault report
class FaultCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    location: str = Field(min_length=2, max_length=100)
    severity: int = Field(ge=1, le=3)

# Schema for returning fault data in API responses
class FaultOut(BaseModel):
    id: int
    title: str
    location: str
    severity: int
    status: str

    class Config:
        from_attributes = True

# Schema for updating fault status
class FaultUpdate(BaseModel):
    status: str = Field(pattern="^(open|closed)$")

# Schema for creating a new maintenance tool
class ToolCreate(BaseModel):
    name: str = Field(min_length=2, max_length=60)

# Schema for returning tool data in API responses
class ToolOut(BaseModel):
    id: int
    name: str
    status: str

    class Config:
        # Tells Pydantic to read data from ORM objects (like SQLAlchemy models)
        from_attributes = True

# Schema for updating tool status
class ToolUpdate(BaseModel):
    status: str = Field(pattern="^(checked_in|checked_out)$")