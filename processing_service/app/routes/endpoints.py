import logging
from fastapi import APIRouter, HTTPException, FastAPI
from processing_service.app.models.processing_model import ProcessingResponse
from processing_service.app.utils.summary_retriever import read_target_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/result", tags=["Result"])


@router.get("/{job_id}", response_model=ProcessingResponse,
            summary="Fetch processed result by job ID")
async def get_result(job_id: str) -> ProcessingResponse:
    """
    Retrieve the processed result for a given job ID.
    Returns 202 if the result is not yet available.
    """
    try:
        result = read_target_file(job_id)
        if result is None:
            logger.info("Result not ready for job_id=%s", job_id)
            raise HTTPException(status_code=202,
                                detail="Resource not ready yet.")
        return ProcessingResponse(output=result)

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Failed to retrieve result for job_id=%s", job_id)
        raise HTTPException(status_code=500, detail="Internal server error")


def create_instance() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    """
    app = FastAPI(title="Processing API", version="1.0.0")
    app.include_router(router)
    logger.info("FastAPI instance created with result router")
    return app
