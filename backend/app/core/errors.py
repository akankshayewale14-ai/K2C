from fastapi import HTTPException, status


def http_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


unauthorized = lambda msg="Not authenticated": http_error(status.HTTP_401_UNAUTHORIZED, "unauthorized", msg)
forbidden = lambda msg="Not allowed": http_error(status.HTTP_403_FORBIDDEN, "forbidden", msg)
not_found = lambda msg="Not found": http_error(status.HTTP_404_NOT_FOUND, "not_found", msg)
bad_request = lambda msg="Bad request": http_error(status.HTTP_400_BAD_REQUEST, "bad_request", msg)
conflict = lambda msg="Conflict": http_error(status.HTTP_409_CONFLICT, "conflict", msg)
unavailable = lambda msg="Service unavailable": http_error(status.HTTP_503_SERVICE_UNAVAILABLE, "unavailable", msg)
