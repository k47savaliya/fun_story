from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server import crud, schemas
from server.utils.auth import (
    authenticate_user,
    create_access_token,
    create_access_token_from_refresh_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from ..deps import get_db

TOKEN_EXPIRE_DELTA = 20160

# JSONify the user response
def user_jsonify(user):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
    }


user_router = APIRouter(prefix="/auth", tags=["User"])


@user_router.post("/login", response_model=schemas.RespUser)
async def login_for_access_token(
    form_data: schemas.LoginInput,
    db: Session = Depends(get_db),
):
    """
    user login
    """
    try:
        # Check if user exists
        user = crud.user.get_by_email(db, email=form_data.email)
        if not user:
            raise HTTPException(
                status_code=400,
                detail="We couldn't find account with this email, please signup",
            )

        # Authenticate user
        user = authenticate_user(db, form_data.email, form_data.password)
        if not user:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "Incorrect email or password",
                },
            )

        # Create access token
        access_token_expires = timedelta(minutes=TOKEN_EXPIRE_DELTA)
        access_token = create_access_token(
            data={"sub": user.email, "id": user.id}, expires_delta=access_token_expires
        )
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": user.email, "id": user.id}
        )

        # Return user data
        user_data = {"user": user_jsonify(user), "access_token": access_token, "refresh_token": refresh_token}
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": user_data,
                "message": "Login Successfull",
            },
        )
    
    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@user_router.post("/signup")
async def sign_up(
    data: schemas.UserCreateInput, 
    db: Session = Depends(get_db)
):
    """
    user signup
    """

    try:
        # Check if user exists
        email = data.email.lower().strip()
        user = crud.user.get_by_email(db, email=email)

        if user:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "You already have an account with us. please continue with login",
                },
            )

        # Create user and hash password
        hashed_password = get_password_hash(data.password)
        user = crud.user.create(
            db,
            obj_in=schemas.UserBase(
                name=data.name, email=data.email, hashed_password=hashed_password
            ),
        )

        # Create access token
        access_token_expires = timedelta(minutes=TOKEN_EXPIRE_DELTA)
        access_token = create_access_token(
            data={"sub": user.email, "id": user.id}, expires_delta=access_token_expires
        )
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": user.email, "id": user.id}
        )

        # Return user data
        user_data = {"user": user_jsonify(user),"access_token": access_token, "refresh_token": refresh_token}

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": user_data,
                "message": "Signup Successfull",
            },
        )

    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )

    finally:
        db.close()


@user_router.post("/change-password")
async def change_password(
    data: schemas.ChangePassword,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Change user password
    """

    try:
        old_password = data.old_password
        new_password = data.new_password
        user_obj = crud.user.get_by_email(db, email=current_user.email)

        # Check if user exists
        if not user_obj:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "User not found",
                },
            )
        
        # Verify old password
        if not verify_password(old_password, user_obj.hashed_password):
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "Old password is incorrect",
                },
            )

        # Check if new password is same as old password
        if verify_password(new_password, user_obj.hashed_password):
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "New password is same as your old password",
                },
            )

        # Update password
        hashed_password = get_password_hash(new_password)
        user_obj = crud.user.update(
            db,
            db_obj=user_obj,
            obj_in=schemas.UserUpdate(hashed_password=hashed_password),
        )

        # Create access token
        access_token_expires = timedelta(minutes=TOKEN_EXPIRE_DELTA)
        access_token = create_access_token(
            data={"sub": user_obj.email, "id": user_obj.id},
            expires_delta=access_token_expires,
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Password changed successfully",
                "data": {"token": access_token, "token_type": "bearer"},
            },
        )

    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )

    finally:
        db.close()


@user_router.post("/update-profile")
async def update_profile(
    data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update user profile
    """

    try:
        # Check if user is active
        user_obj = crud.user.get_by_email(db, email=current_user.email)
        if not user_obj:
            raise HTTPException(status_code=400, detail="User not found")

        # Update user profile
        user_obj = crud.user.update(db, db_obj=user_obj, obj_in=data)
        return JSONResponse(
            status_code=200,
            content={"success": True, "data": user_jsonify(user_obj), "message": "Profile updated successfully"},
        )

    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )

    finally:
        db.close()


@user_router.get("/get-all-user")
async def get_all_user(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get all users
    """

    try:
        # Fetch all users
        limit = int(request.query_params.get("limit", 10))
        page = int(request.query_params.get("page", 1))
        offset = (page - 1) * limit
        user_obj = crud.user.get_all(db, limit=limit, offset=offset)
        total_users = crud.user.get_total_users_count(db)

        # Return user data
        if user_obj:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data":[
                        {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email,
                            "is_active": user.is_active,
                            "created_at": str(user.created_at),
                            "updated_at": str(user.updated_at)
                        }
                        for user in user_obj
                    ],
                    "total_users": total_users,
                    "current_page": page,
                    "total_pages": -(-total_users // limit),
                    "error": None,
                    "message": "All users fetched successfully",
                },
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@user_router.post("/access-token")
async def refresh_token(
    request: Request,
):
    """
    generate access token from refresh token
    """

    try:
        # Get refresh token
        refresh_token = request.headers.get("Authorization")
        if not refresh_token:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "Refresh token is required",
                },
            )

        # Create access token from refresh token
        access_token = create_access_token_from_refresh_token(refresh_token=refresh_token)
        if not access_token:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "Invalid refresh token",
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {"token": access_token},
                "message": "Refreshed token generated successfully",
            },
        )

    except HTTPException:
        raise

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
