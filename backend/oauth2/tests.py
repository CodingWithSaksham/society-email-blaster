from django.test import TestCase
from os import path
# Create your tests here.

print(path.join(path.dirname(__name__), "client_secrets.json"))
print(path.dirname(__file__))
