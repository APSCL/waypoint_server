from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        waypoint_msg = []

        x = request.form.get('x')
        y = request.form.get('y')
        waypoint_msg.append({'x': x, 'y': y})

        print(waypoint_msg)
        # requests.post('http://localhost:5000', json=waypoint_msg)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=5001)
