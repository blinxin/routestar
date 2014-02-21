routestar
=========

A simple routing library for tornado

usage
=========

```python
from tornado import ioloop, web, httpserver
from tornado import escape
from router.routestar import *
import os

class ServerApp(web.Application):
    def __init__(self, path = None):
	# Autoload all the modules specified in the path provided
        dl = DynLoad(path)
        dl.load_modules()
        
        settings = {
            'app_name':'myapp',
            'xsrf_cookies':True,
            'login_url': r'/login',
            'gzip': True,
            'template_path': os.path.join(os.path.dirname(__file__), 
                                          "templates"),
            'static_path': os.path.join(os.path.dirname(__file__), 
                                        "static"),
            'cookie_secret':'<insertsecret>',
            }

        super(ServerApp, self).__init__(AddRoute.get_routes(), # Load all the routes and their handlers
                                        debug = True,
                                        **settings)
        
if __name__ == "__main__":
    #Specify the path to load the route handlers from
    application = ServerApp(path = 'routes/')

    http_server = httpserver.HTTPServer(application)
    http_server.listen(8889)
```

Within each handler utilize the "AddRoute" decorator to add a new map to the handler it decorates

below is an example of using it in a route/auth.py file

```python
from tornado import web, escape
from tornado.auth import GoogleMixin
from router.routestar import AddRoute #import the AddRoute decorator

# Note these are regular expressions just like you would hand into the initalization of your application
@AddRoute(r'/login')
class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html', next_uri=self.get_argument('next', u'/'))

    def post(self):
        self.set_secure_cookie('user',
                               self.get_argument("email"))

        self.redirect(self.get_argument('next', u'/'))
        
@AddRoute(r'/login/google')
class AuthHandler(BaseHandler, GoogleMixin):
    """
    Base Google auth handler
    We'll need to break this out to include things like
    facebook,twitter
    """
    def _on_auth(self, user):
        if not user:
            self.send_error(500, 'Google Auth Failed')
        self.set_secure_cookie('user', escape.json_encode(user))
        self.redirect(self.get_argument('next', u'/'))

    @web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()        

@AddRoute(r'/logout')
class LogoutHandler(BaseHandler):
    """
    Logout handler
    Gets removes cookie from client
    """
    def get(self):
        """
        Clear cookie and return user to front of site
        """
        self.clear_cookie('user')
        self.redirect('/')
```
