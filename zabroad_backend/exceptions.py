import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception — log it and return a clean 500
        logger.exception('Unhandled exception in %s', context.get('view'))
        return Response(
            {'detail': 'An unexpected error occurred. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Normalise all error payloads to always include a `detail` key
    if isinstance(response.data, dict) and 'detail' not in response.data:
        # Flatten first field error into detail for simple client consumption
        first = next(iter(response.data.values()), None)
        if isinstance(first, list) and first:
            response.data['detail'] = str(first[0])
        elif isinstance(first, str):
            response.data['detail'] = first

    return response
