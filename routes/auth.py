from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

auth_routes = Blueprint("auth", __name__)

@auth_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        # ohlidani vstupu na beckendu
        if len(password) < 8:
            flash("Heslo musí mít alespoň 8 znaků.")
            current_app.logger.warning(f"[REGISTRACE] Uživatel '{username}' zadal krátké heslo.")
            return render_template("register.html")

        # musi se rovna obe hesla
        if password != confirm:
            flash("Hesla se neshodují.")
            current_app.logger.warning(f"[REGISTRACE] Uživatel '{username}' zadal neshodná hesla.")
            return render_template("register.html")


        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()

            # kontrola existujiciho uzivatele
            if existing_user:
                flash("Tento uživatel již existuje. Zvol jiné jméno.")
                current_app.logger.warning(f"[REGISTRACE] Duplikace jména: {username}")
                return render_template("register.html")

            # hasovani hesla + lozeni do databaze
            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            conn.commit()
            conn.close()

            current_app.logger.info(f"[REGISTRACE] Uživatel '{username}' úspěšně zaregistrován.")
            flash("Registrace proběhla úspěšně.")
            return redirect(url_for("auth.login"))

        except Exception as e:
            current_app.logger.exception("[REGISTRACE] Neočekávaná chyba při registraci:")
            flash("Nastala chyba při registraci.")
            return render_template("register.html")

    return render_template("register.html")


@auth_routes.route("/login", methods=["GET", "POST"])
# prihlaseni uzivatele pomoci username a password
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            current_app.logger.info(f"[LOGIN] Uživatel '{username}' přihlášen.")
            return redirect(url_for("main.index"))
        else:
            flash("Špatné jméno nebo heslo.")
            current_app.logger.warning(f"[LOGIN] Neplatný pokus o přihlášení: {username}")

    return render_template("login.html")

@auth_routes.route("/logout")
def logout():
    user = session.pop("username", None)
    session.pop("user_id", None)
    current_app.logger.info(f"[LOGOUT] Uživatel '{user}' odhlášen.")
    return redirect(url_for("main.index"))
