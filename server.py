from flask import Flask  # Import Flask framework

app = Flask(__name__)  # Create a Flask app instance

@app.route('/')  # Define a route for the home page
def home():
    return "Hello, Flask in WSL!"  # What the user sees when visiting "/"

@app.route('/about')
def about():
    return "This is the About page!"

if __name__ == "__main__":  # Ensures the app runs only when executed directly
    app.run(host="0.0.0.0", port=5000, debug=True)  # Start the Flask web server

