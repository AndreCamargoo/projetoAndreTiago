import re

from django.db import models

from app.utils.exceptions import ValidationError


TIPO_CHOICES = (
    ("A", "Analítica"),
    ("S", "Sintética"),
)
