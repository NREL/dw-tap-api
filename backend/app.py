from flask import Flask
app = Flask(__name__)

# Example REST endpoint
@app.route('/api/hello')
def hello_api():
    return {'message': 'Hello from Flask API'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
