from app.endpoints.flights import api_router as flights_router
from app.endpoints.ping import api_router as application_health_router
from app.endpoints.user import api_router as user_router

list_of_routes = [
    flights_router,
    application_health_router,
    user_router,
]


__all__ = [
    "list_of_routes",
]
