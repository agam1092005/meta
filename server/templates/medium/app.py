from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    # BUG: Returns 404 instead of 200 message
    return "Not Found", 404

if __name__ == '__main__':
    app.run()
