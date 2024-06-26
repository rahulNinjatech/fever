from fastapi import APIRouter
from fastapi import Response
from fastapi import status


health_router = APIRouter(
    tags=["healthcheck"],
)


@health_router.get("/", status_code=status.HTTP_200_OK)
async def check_health() -> str:
    """
    Perform a health check of the server.

    This endpoint is used to check the health of the server and ensures that the server is running and capable
    of handling requests. It is typically used by infrastructure services to verify the server's status.

    Returns:
        str: A message indicating that the server is up and running.
    """
    return Response(content="Server is up and running", media_type="text/plain")
