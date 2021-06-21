from Interpreter.Interpreter import Interpret
from API.API import API

try:
    Interpret()
finally:
    API.api_quit()
