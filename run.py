import os
from app import create_app
from flask import url_for, redirect
from app.api.v1 import store_v1

config_name = os.environ.get('FLASK_ENV')
app = create_app(config_name)

@app.route('/')
def index():
    return redirect(url_for('store_v1.index'))

if __name__ == '__main__':
    app.run()
