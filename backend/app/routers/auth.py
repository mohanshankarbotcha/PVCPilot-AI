from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from app.schemas.auth import UserRegister, Token, UserOut, UserLogin
from app.models.user import User
from app.utils.security import get_password_hash, create_access_token, create_refresh_token, decode_token
from app.services.auth_service import authenticate_user, get_current_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister):
    # Check if email is already registered
    existing_user = await get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system",
        )
    
    # Assign roles and default permissions
    # In a real system, roles map to specific permission strings
    role_permissions = {
        "factory_owner": ["view:all", "edit:all", "approve:all", "admin"],
        "plant_manager": ["view:all", "edit:production", "edit:machines", "approve:production"],
        "quality_engineer": ["view:quality", "edit:quality", "approve:quality"],
        "inventory_manager": ["view:inventory", "edit:inventory", "approve:inventory"],
        "procurement_manager": ["view:procurement", "edit:procurement", "approve:purchase_orders"],
        "sales_manager": ["view:sales", "view:finance", "edit:sales", "approve:sales"],
        "operator": ["view:production_own"],
        "admin": ["view:all", "edit:all", "approve:all", "admin"],
    }
    
    perms = role_permissions.get(user_in.role, ["view:production_own"])
    
    new_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        department=user_in.department,
        phone=user_in.phone,
        permissions=perms,
        is_active=True,  # Set to true for development seeding convenience
        is_verified=True
    )
    
    await new_user.insert()
    return new_user

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, response: Response):
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await user.save()
    
    access_token = create_access_token(subject=user.id, role=user.role, email=user.email)
    refresh_token = create_refresh_token(subject=user.id, role=user.role, email=user.email)
    
    # Store refresh token in HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # False for local dev, True in production
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        email=user.email,
        full_name=user.full_name,
        user=UserOut.model_validate(user)
    )

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    # Retrieve refresh token from cookie
    refresh_tok = request.cookies.get("refresh_token")
    if not refresh_tok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
        
    payload = decode_token(refresh_tok)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
        
    user_id = payload.get("sub")
    role = payload.get("role")
    email = payload.get("email")
    
    user = await User.get(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
        
    new_access_token = create_access_token(subject=user.id, role=role, email=email)
    new_refresh_token = create_refresh_token(subject=user.id, role=role, email=email)
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
