from django.db import OperationalError, connection
from django.http import JsonResponse


def health(request):
    """Report that the app is running and can reach the database."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except OperationalError:
        return JsonResponse({"status": "database unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
