"""
ML TopUp Lite - Main Flask application entry point.

A school-project demo Mobile Legends: Bang Bang top-up website.
- NO DATABASE: all data is stored in Python lists (see services/storage.py)
- Demonstrates Python OOP: encapsulation, inheritance, polymorphism (see models/)
- Three roles: admin, staff, customer with server-side role-based access control
- All payments are DEMO ONLY - no real payment processing occurs
"""
import os
from flask import Flask, render_template, session

from services import storage, auth_service
from routes.auth_routes import auth_bp
from routes.customer_routes import customer_bp
from routes.staff_routes import staff_bp
from routes.admin_routes import admin_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "school-demo-secret-key")

    # Seed demo accounts and demo products into the in-memory Python lists
    storage.seed_data()

    # Register blueprints (route groups)
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(admin_bp)

    # -----------------------------------------------------------------
    # PUBLIC HOMEPAGE
    # -----------------------------------------------------------------
    @app.route("/")
    def index():
        featured_products = storage.get_all_products()[:6]
        return render_template("index.html", products=featured_products,
                                logged_in=session.get("user_id") is not None)

    # -----------------------------------------------------------------
    # ERROR HANDLERS - never expose raw tracebacks to users
    # -----------------------------------------------------------------
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # -----------------------------------------------------------------
    # TEMPLATE CONTEXT: make current_user available in every template
    # -----------------------------------------------------------------
    @app.context_processor
    def inject_current_user():
        return {"current_user": auth_service.current_user()}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
