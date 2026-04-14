"""Configurações de desenvolvimento."""
import os

from .base import *  # noqa: F401,F403

# Em dev, permite bootstrap se não definido explicitamente
if "ALLOW_TOKEN_BOOTSTRAP" not in os.environ:  # noqa: F405
    ALLOW_TOKEN_BOOTSTRAP = True  # noqa: F405
