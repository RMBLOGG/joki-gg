from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.order import order_bp
    from routes.admin import admin_bp
    from routes.joki import joki_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(joki_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
