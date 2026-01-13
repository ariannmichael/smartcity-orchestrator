from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}
