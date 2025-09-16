# Add Endpoint to Existing Service

## Task: Add a new API endpoint to an existing microservice

### Requirements Checklist
- [ ] Endpoint follows RESTful conventions
- [ ] Input validation using Pydantic models
- [ ] Proper HTTP status codes
- [ ] Error handling with Problem Details format
- [ ] Unit tests with 80%+ coverage
- [ ] OpenAPI documentation tags

### Endpoint Structure
```python
@router.post("/{resource}", 
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["resources"],
    summary="Create new resource"
)
async def create_resource(
    resource: ResourceCreate,
    current_user: User = Depends(get_current_user)
) -> ResourceResponse:
    """
    Create a new resource.
    
    Args:
        resource: Resource creation data
        current_user: Authenticated user
        
    Returns:
        Created resource with ID
        
    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 409 if resource already exists
    """
```

### Validation Rules
1. **Input Models**: Use Pydantic for request validation
2. **Output Models**: Define response schemas
3. **Error Models**: Use Problem Details format
4. **Authentication**: Validate tokens where required

### Testing Requirements
```python
def test_create_resource_success():
    """Test successful resource creation."""
    
def test_create_resource_validation_error():
    """Test input validation errors."""
    
def test_create_resource_unauthorized():
    """Test unauthorized access."""
    
def test_create_resource_duplicate():
    """Test duplicate resource handling."""
```

### Event Integration
If the endpoint triggers domain events:
1. Publish to appropriate NATS subject
2. Include correlation ID for tracing
3. Handle publish failures gracefully

### Documentation
- Add endpoint to OpenAPI tags
- Include request/response examples
- Document error codes and meanings
