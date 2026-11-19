"""Transaction helper shared by SQLite and django-mongodb-backend."""

from django.db import connection, transaction as django_transaction

try:
    from django_mongodb_backend import transaction as mongodb_transaction
except ImportError:  # pragma: no cover - only relevant without the optional backend installed.
    mongodb_transaction = None


def atomic():
    """Use the backend-native transaction implementation."""
    if connection.vendor == "mongodb" and mongodb_transaction is not None:
        return mongodb_transaction.atomic()
    return django_transaction.atomic()
