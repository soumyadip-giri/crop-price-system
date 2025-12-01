# backend/app.py
import os
from flask import Flask, render_template, redirect, session
from flask_cors import CORS

# Optional: load .env when running locally
# (On Render or other hosting you will set env variables in the dashboard instead)
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def create_app():
    """
    Application factory for KrishiSense.
    Used both locally (python -m backend.app) and in production
    (gunicorn 'backend.app:create_app()').
    """
    # ---------------- base paths ----------------
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates = os.path.join(base_dir, "frontend", "templates")
    static = os.path.join(base_dir, "frontend", "static")

    # Load .env only when running locally
    env_path = os.path.join(base_dir, ".env")
    if load_dotenv is not None and os.path.exists(env_path):
        load_dotenv(env_path)

    # ---------------- Flask app ----------------
    app = Flask(
        __name__,
        template_folder=templates,
        static_folder=static,
        static_url_path="/static",
    )

    # Secret key for sessions / flashes
    # Prefer FLASK_SECRET_KEY, fallback to JWT_SECRET, then a dev value
    app.secret_key = (
        os.environ.get("FLASK_SECRET_KEY")
        or os.environ.get("JWT_SECRET")
        or "dev-secret-change-me"
    )

    # Allow frontend JS to call backend APIs
    CORS(app)

    # ---------------- Blueprints ----------------
    # Import here to avoid circular imports when gunicorn imports create_app()
    from .auth_routes import auth_bp
    from .prediction_routes import prediction_bp
    from .services import advice_service  # for GLOBAL_MAE / GLOBAL_RMSE

    app.register_blueprint(auth_bp)
    app.register_blueprint(prediction_bp)

    # ---------------- Page routes ----------------

    @app.route("/")
    def index():
        # Homepage with hero + background video
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        # video_bg handled inside login.html via Jinja variable
        return render_template("login.html", video_bg=True)

    @app.route("/register")
    def register_page():
        # video_bg handled inside register.html via Jinja variable
        return render_template("register.html", video_bg=True)

    @app.route("/dashboard")
    def dashboard_page():
        # Optional: protect dashboard if you want session-based guard
        # if "user_id" not in session:
        #     return redirect("/login")
        return render_template("dashboard.html")

    @app.route("/about-model")
    def about_model_page():
        # Pass approximate global metrics from advice_service to the template
        return render_template(
            "about_model.html",
            GLOBAL_MAE=advice_service.GLOBAL_MAE,
            GLOBAL_RMSE=advice_service.GLOBAL_RMSE,
        )

    return app


# Local dev entrypoint: `python -m backend.app` OR `python backend/app.py`
if __name__ == "__main__":
    # Load .env for local dev
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if load_dotenv is not None:
        env_path = os.path.join(base_dir, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)

    app = create_app()
    # debug=True only for local development
    app.run(host="0.0.0.0", port=5000, debug=True)
