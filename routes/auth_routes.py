from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from db.models import HR
from core.security import (
    get_db,
    verify_password,
    get_password_hash,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class HRRegisterSchema(BaseModel):

    name: str
    email: EmailStr
    password: str


@router.post("/register")
def register_hr(
    payload: HRRegisterSchema,
    db: Session = Depends(get_db)
):

    existing = (
        db.query(HR)
        .filter(HR.email == payload.email)
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hr = HR(
        name=payload.name,
        email=payload.email,
        password=get_password_hash(
            payload.password
        )
    )

    db.add(hr)
    db.commit()
    db.refresh(hr)

    return {
        "message": "HR account created successfully",
        "hr_id": hr.id
    }


@router.post("/login")
def login_hr(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    hr = (
        db.query(HR)
        .filter(HR.email == form_data.username)
        .first()
    )

    if not hr:

        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    if not verify_password(
        form_data.password,
        hr.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    token = create_access_token({
        "sub": hr.email,
        "hr_id": hr.id
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "hr_id": hr.id,
        "hr_name": hr.name
    }