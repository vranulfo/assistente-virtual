import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / 'backend'))

from app import app


class ApiPrefixMiddleware:
	def __init__(self, application):
		self.application = application

	def __call__(self, environ, start_response):
		path = environ.get('PATH_INFO', '')
		if path == '/api' or path.startswith('/api/'):
			environ['PATH_INFO'] = path[4:] or '/'
		return self.application(environ, start_response)


app.wsgi_app = ApiPrefixMiddleware(app.wsgi_app)

__all__ = ['app']
