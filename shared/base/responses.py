from starlette import status

from shared.base.schemes import ExceptionScheme, ExceptionValidationScheme


class ResponseSchema:
    """Response Schema."""
    base = {
        status.HTTP_401_UNAUTHORIZED: {'model': ExceptionScheme},
        status.HTTP_403_FORBIDDEN: {'model': ExceptionScheme},
        status.HTTP_405_METHOD_NOT_ALLOWED: {'model': ExceptionScheme},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {'model': ExceptionValidationScheme},
    }

    def get_base_statuses(self, exclude: list = None) -> dict:
        """Get base statuses."""
        if exclude is not None:
            return {k: v for k, v in self.base.items() if k not in exclude}
        return self.base

    def statuses(
            self,
            schema,
            response_status: int = status.HTTP_200_OK,
            statuses: list = None,
            exclude: list = None
    ) -> dict:
        """Get create statuses."""
        exception_schema = {'model': ExceptionScheme}
        if statuses is None:
            statuses = []
        get_status = {response_status: {'model': schema}}
        for status_ in statuses:
            get_status[status_] = exception_schema if status_ != status.HTTP_204_NO_CONTENT else {'model': None}
        return {**get_status, **self.get_base_statuses(exclude=exclude)}

    def __call__(
            self,
            schema=None,
            response_status: int = status.HTTP_200_OK,
            statuses: list = None,
            exclude: list = None
    ) -> dict:
        return self.statuses(schema=schema, response_status=response_status, statuses=statuses, exclude=exclude)


responses = ResponseSchema()
