from flask import Flask
import populartimes


app = Flask(__name__,template_folder="/Users/Ria/Desktop/Shift/khalid/templates")

@app.route('/')
def hello_world():
    return 'Hello, World!'
