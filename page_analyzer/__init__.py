from page_analyzer.app import create_app
from page_analyzer.settings import TESTING

__all__ = ["create_app"]

if not TESTING:
    app = create_app()
