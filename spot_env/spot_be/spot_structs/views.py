from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import User
from .serializers import *

#once i've outlined methods in User, implement them here in terms of HTTP calls: get, put, post, etc
