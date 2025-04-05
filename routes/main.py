from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, flash
from utils.predictor import predict_price
from db import get_db_connection

main_routes = Blueprint("main", __name__)


@main_routes.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    comparison_table = []
    form_data = request.form if request.method == "POST" else {}
    app = current_app

    if request.method == "POST":
        action = form_data.get("action")
        try:
            try:
                metraz = float(form_data["metraz"])
                if metraz < 0 or metraz > 150:
                    current_app.logger.warning(f"[PREDIKCE] Metraz mimo rozsah: {metraz}")
                metraz = max(0, min(metraz, 150))  # omezíme rozsah
            except ValueError:
                flash("Zadejte platné číslo pro metráž (0–150 m²).")
                current_app.logger.warning(f"[PREDIKCE] Neplatný vstup pro metráž: {form_data.get('metraz')}")
                return render_template(
                    "index.html",
                    prediction=None,
                    location_mapping=app.location_mapping,
                    form_data=form_data,
                    comparison_table=[]
                )

            rozloha = form_data["rozloha"]
            energeticka = form_data["energeticka"]
            stav = form_data["stav"]
            lokalita = form_data["lokalita"]

            # Validace hodnot
            valid_dispozice = ['1+kk', '2+kk', '3+kk', '4+kk', '5+kk']
            valid_energie = list(app.energy_mapping.keys())
            valid_stavy = list(app.condition_mapping.keys())
            valid_lokality = list(app.location_mapping.keys())

            if rozloha not in valid_dispozice:
                flash("Neplatná dispozice.")
                current_app.logger.warning(f"[PREDIKCE] Neplatná dispozice: {rozloha}")
                return render_template(...)

            if energeticka not in valid_energie:
                flash("Neplatná energetická třída.")
                current_app.logger.warning(f"[PREDIKCE] Neplatná energetická třída: {energeticka}")
                return render_template(...)

            if stav not in valid_stavy:
                flash("Neplatný stav nemovitosti.")
                current_app.logger.warning(f"[PREDIKCE] Neplatný stav: {stav}")
                return render_template(...)

            if lokalita not in valid_lokality:
                flash("Neplatná lokalita.")
                current_app.logger.warning(f"[PREDIKCE] Neplatná lokalita: {lokalita}")
                return render_template(...)

            app.logger.info(
                f"[FORMULÁŘ] metraz={metraz}, rozloha={rozloha}, energeticka={energeticka}, stav={stav}, lokalita={lokalita}")

            prediction = predict_price(
                app=app,
                metraz=metraz,
                rozloha_text=rozloha,
                energeticka_text=energeticka,
                stav_text=stav,
                lokalita_text=lokalita
            )

            if prediction is None:
                app.logger.warning("[PREDIKCE] Predikce selhala nebo vrací None.")

            if action == "srovnani":
                for nazev_lokalita, kod in app.location_mapping.items():
                    if nazev_lokalita == lokalita:
                        continue

                    cena = predict_price(
                        app=app,
                        metraz=metraz,
                        rozloha_text=rozloha,
                        energeticka_text=energeticka,
                        stav_text=stav,
                        lokalita_text=nazev_lokalita
                    )

                    comparison_table.append({
                        "lokalita": nazev_lokalita,
                        "predikovana_cena": round(cena, 2)
                    })

                app.logger.info(f"[SROVNÁNÍ] Vygenerováno {len(comparison_table)} řádků pro srovnání.")

                comparison_table.sort(key=lambda x: x["predikovana_cena"])
        except Exception as e:
            app.logger.exception("[INDEX] Neočekávaná chyba:")

    return render_template(
        "index.html",
        prediction=prediction,
        location_mapping=app.location_mapping,
        form_data=form_data,
        comparison_table=comparison_table
    )

#routy na predikce mazani,ulozeni a nacteni na stranku
@main_routes.route("/ulozit-predikci", methods=["POST"])
def ulozit_predikci():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    form_data = request.form
    cena = request.form.get("cena", type=float)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prediction_history (user_id, metraz, rozloha, energeticka, stav, lokalita, cena)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session["user_id"],
            form_data.get("metraz"),
            form_data.get("rozloha"),
            form_data.get("energeticka"),
            form_data.get("stav"),
            form_data.get("lokalita"),
            cena
        ))
        conn.commit()
        conn.close()

        current_app.logger.info(f"[PREDIKCE] Uživatel {session['username']} uložil predikci.")
        return redirect(url_for("main.index"))

    except Exception as e:
        current_app.logger.exception("[PREDIKCE] Chyba při ukládání predikce:")
        return redirect(url_for("main.index"))

@main_routes.route("/moje-predikce")
def moje_predikce():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM prediction_history
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (session["user_id"],))
        predikce = cursor.fetchall()
        conn.close()
        return render_template("moje_predikce.html", predikce=predikce)

    except Exception as e:
        current_app.logger.exception("[PREDIKCE] Chyba při načítání historie predikcí:")
        return render_template("moje_predikce.html", predikce=[])

@main_routes.route("/smazat-predikci/<int:predikce_id>")
def smazat_predikci(predikce_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM prediction_history
            WHERE id = %s AND user_id = %s
        """, (predikce_id, session["user_id"]))
        conn.commit()
        conn.close()
        current_app.logger.info(f"[PREDIKCE] Smazána predikce {predikce_id} uživatelem {session['username']}")
    except Exception as e:
        current_app.logger.exception("[PREDIKCE] Chyba při mazání predikce:")

    return redirect(url_for("main.moje_predikce"))
