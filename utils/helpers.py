"""utils/helpers.py — Miscellaneous Flask helpers"""
from flask import flash


def flash_errors(form) -> None:
    """Flash all WTForms validation errors."""
    for field, errors in form.errors.items():
        for error in errors:
            label = getattr(form, field).label.text if hasattr(form, field) else field
            flash(f"{label}: {error}", "danger")


def paginate_query(query, page: int, per_page: int = 10):
    """
    Return a Flask-SQLAlchemy pagination object.
    Falls back gracefully if page is out of range.
    """
    return query.paginate(page=page, per_page=per_page, error_out=False)
