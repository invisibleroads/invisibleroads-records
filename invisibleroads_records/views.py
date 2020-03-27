from invisibleroads_macros_log import get_log
from pyramid.view import exception_view_config
from sqlalchemy.exc import OperationalError


@exception_view_config(OperationalError)
def handle_database_operational_error(context, request):
    response = request.response
    response.status_int = 500
    L.error(DATABASE_ERROR_MESSAGE % context)
    return response


L = get_log(__name__)


DATABASE_ERROR_MESSAGE = """%s

Did you run the initialization script?

invisibleroads initialize development.ini
invisibleroads initialize production.ini"""
