from fastapi import APIRouter
from oidc_routes import router as oidc_router
from jwt_issue_routes import router as issue_router
from jwt_verify_routes import router as verify_router

def get_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health():
        """
        Liveness probe endpoint.
        Used by Docker, Kubernetes, and monitoring systems.
        """
        return {"status": "ok", "service": "Auth Service"}

    router.include_router(oidc_router)
    router.include_router(issue_router)
    router.include_router(verify_router)

    return router
