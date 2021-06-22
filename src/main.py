from Interpreter.Interpreter import Interpret
from API.API import API

try:
    Interpret()
# except:
#     print("Error encountered, quitting...")
finally:
    API.api_quit()
    print("Finish executing, bye...")