from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():

    return {
        "message": "Financial Research AI API",
        "version": "1.0.0",
        "status": "running"
    }


@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "Financial Research AI Backend"
    }