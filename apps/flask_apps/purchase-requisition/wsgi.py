import os
from app import create_app

config = 'production' if os.environ.get('FLASK_ENV') == 'production' else 'development'
app = create_app(config)

if __name__ == '__main__':
    app.run()
