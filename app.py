from sanic import Sanic
from sanic_cors import CORS
app = Sanic("hello")
CORS(app)