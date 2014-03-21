import sae

from movie import app

application = sae.create_wsgi_app(app)
