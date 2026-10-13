from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from services import storage, auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("auth.post_login_redirect"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        errors = auth_service.validate_login(email, password)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("login.html", email=email)

        user = auth_service.attempt_login(email, password)
        if user is None:
            flash("Incorrect email or password.", "error")
            return render_template("login.html", email=email)

        auth_service.login_user_session(user)
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(url_for("auth.post_login_redirect"))

    return render_template("login.html", email="")


@auth_bp.route("/post-login-redirect")
def post_login_redirect():
    """Redirects the freshly logged-in user to the correct dashboard."""
    role = session.get("role")
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    if role == "staff":
        return redirect(url_for("staff.dashboard"))
    return redirect(url_for("customer.dashboard"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("auth.post_login_redirect"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = auth_service.validate_registration(name, email, password, confirm_password)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("register.html", name=name, email=email)

        user = storage.create_user(name, email, password, role="customer")
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", name="", email="")


@auth_bp.route("/logout")
def logout():
    auth_service.logout_user_session()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))
