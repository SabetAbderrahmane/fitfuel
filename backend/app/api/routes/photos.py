from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.food_log import FoodLogResponse
from app.schemas.photo import (
    AIFeedbackHistoryResponse,
    PhotoPredictionConfirmRequest,
    PhotoPredictionCorrectionRequest,
    PhotoPredictionCreateRequest,
    PhotoPredictionResponse,
    PhotoPredictionToFoodLogRequest,
    PhotoUploadResponse,
    VisionInferenceResponse,
)
from app.services.auth_service import get_current_user
from app.services.photo_service import PhotoService

router = APIRouter()


@router.post(
    "/upload",
    response_model=PhotoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a food photo",
)
async def upload_photo(
    file: UploadFile = File(...),
    notes: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PhotoUploadResponse:
    service = PhotoService(db)
    photo_upload = await service.upload_photo(
        current_user=current_user,
        upload_file=file,
        notes=notes,
    )
    return PhotoUploadResponse.model_validate(photo_upload)


@router.get(
    "",
    response_model=list[PhotoUploadResponse],
    summary="List uploaded photos",
)
async def list_photos(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PhotoUploadResponse]:
    service = PhotoService(db)
    uploads = service.list_photo_uploads(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return [PhotoUploadResponse.model_validate(upload) for upload in uploads]


@router.get(
    "/{photo_upload_id}",
    response_model=PhotoUploadResponse,
    summary="Get one uploaded photo record",
)
async def get_photo(
    photo_upload_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PhotoUploadResponse:
    service = PhotoService(db)
    photo_upload = service.get_photo_upload(
        current_user=current_user,
        photo_upload_id=photo_upload_id,
    )
    return PhotoUploadResponse.model_validate(photo_upload)


@router.get(
    "/{photo_upload_id}/file",
    summary="Serve a locally stored uploaded file",
)
async def get_local_photo_file(
    photo_upload_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    service = PhotoService(db)
    local_path = service.get_local_photo_path(
        current_user=current_user,
        photo_upload_id=photo_upload_id,
    )
    return FileResponse(path=str(local_path))


@router.post(
    "/{photo_upload_id}/predictions",
    response_model=PhotoPredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Attach a prediction result to an uploaded photo",
)
async def add_prediction(
    photo_upload_id: str,
    payload: PhotoPredictionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PhotoPredictionResponse:
    service = PhotoService(db)
    prediction = service.add_prediction_result(
        current_user=current_user,
        photo_upload_id=photo_upload_id,
        payload=payload,
    )
    return PhotoPredictionResponse.model_validate(prediction)


@router.post(
    "/{photo_upload_id}/run-inference",
    response_model=VisionInferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Run vision inference on an uploaded photo",
)
async def run_inference(
    photo_upload_id: str,
    top_k: int = Query(default=3, ge=1, le=10),
    save_prediction: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VisionInferenceResponse:
    service = PhotoService(db)
    return service.run_inference(
        current_user=current_user,
        photo_upload_id=photo_upload_id,
        top_k=top_k,
        save_prediction=save_prediction,
    )


@router.get(
    "/{photo_upload_id}/feedback",
    response_model=list[AIFeedbackHistoryResponse],
    summary="List feedback history for one uploaded photo",
)
async def list_feedback_history(
    photo_upload_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AIFeedbackHistoryResponse]:
    service = PhotoService(db)
    history = service.list_feedback_history(
        current_user=current_user,
        photo_upload_id=photo_upload_id,
    )
    return [AIFeedbackHistoryResponse.model_validate(entry) for entry in history]


@router.post(
    "/{photo_upload_id}/predictions/{prediction_id}/confirm",
    response_model=PhotoPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm a prediction as correct",
)
async def confirm_prediction(
    photo_upload_id: str,
    prediction_id: str,
    payload: PhotoPredictionConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PhotoPredictionResponse:
    service = PhotoService(db)
    prediction = service.confirm_prediction(
        current_user=current_user,
        photo_upload_id=photo_upload_id,
        prediction_id=prediction_id,
        payload=payload,
    )
    return PhotoPredictionResponse.model_validate(prediction)


@router.post(
    "/{photo_upload_id}/predictions/{prediction_id}/correct",
    response_model=PhotoPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Correct a prediction",
)
async def correct_prediction(
    photo_upload_id: str,
    prediction_id: str,
    payload: PhotoPredictionCorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PhotoPredictionResponse:
    service = PhotoService(db)
    prediction = service.correct_prediction(
        current_user=current_user,
        photo_upload_id=photo_upload_id,
        prediction_id=prediction_id,
        payload=payload,
    )
    return PhotoPredictionResponse.model_validate(prediction)


@router.post(
    "/{photo_upload_id}/predictions/{prediction_id}/log-to-food-log",
    response_model=FoodLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Convert a prediction into a food log entry",
)
async def log_prediction_to_food_log(
    photo_upload_id: str,
    prediction_id: str,
    payload: PhotoPredictionToFoodLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FoodLogResponse:
    service = PhotoService(db)
    food_log = service.log_prediction_to_food_log(
        current_user=current_user,
        photo_upload_id=photo_upload_id,
        prediction_id=prediction_id,
        payload=payload,
    )
    return FoodLogResponse.model_validate(food_log)