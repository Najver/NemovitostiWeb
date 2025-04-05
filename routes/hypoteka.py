from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, flash
from db import get_db_connection

hypoteka_routes = Blueprint("hypoteka", __name__)

@hypoteka_routes.route("/hypoteka", methods=["GET", "POST"])
def hypoteka():
    splatka = None
    total = None
    app = current_app

    cena_predikce = request.args.get("cena", type=float)
    form_data = request.form.to_dict() if request.method == "POST" else {}

    if request.method == "POST":
        try:
            if cena_predikce:
                vlastni = float(request.form["vlastni"])
                if vlastni < 0:
                    flash("Vlastní prostředky nemohou být záporné.")
                    current_app.logger.warning(f"[HYPOTEKA] Neplatné vlastní prostředky: {vlastni}")
                    return redirect(url_for("hypoteka.hypoteka", cena=cena_predikce))

                uver = cena_predikce - vlastni
                if uver < 0:
                    flash("Nemusíte si brát hypotéku – máte dostatek vlastních prostředků.")
                    current_app.logger.info(
                        f"[HYPOTEKA] Nepotřebná hypotéka – vlastní: {vlastni}, odhad: {cena_predikce}")
                    return redirect(url_for("hypoteka.hypoteka", cena=cena_predikce))
            else:
                uver = float(request.form["uver"])
                if uver < 0:
                    flash("Výše úvěru nemůže být záporná.")
                    current_app.logger.warning(f"[HYPOTEKA] Záporný úvěr: {uver}")
                    return redirect(url_for("hypoteka.hypoteka"))

            urok = float(request.form["urok"])
            if urok < 0:
                flash("Úroková sazba nemůže být záporná.")
                current_app.logger.warning(f"[HYPOTEKA] Záporný úrok: {urok}")
                return redirect(url_for("hypoteka.hypoteka"))

            mesice = int(request.form["mesice"])
            if mesice <= 0:
                flash("Doba splácení musí být větší než 0.")
                current_app.logger.warning(f"[HYPOTEKA] Neplatný počet měsíců: {mesice}")
                return redirect(url_for("hypoteka.hypoteka"))

            fixace = int(request.form.get("fixace", "0"))
            if fixace > 0 and mesice < fixace * 12:
                flash(f"Při fixaci na {fixace} let musí být doba splácení alespoň {fixace * 12} měsíců.")
                current_app.logger.warning(
                    f"[HYPOTEKA] Fixace delší než splácení | fixace: {fixace} let, měsíce: {mesice}")
                return redirect(url_for("hypoteka.hypoteka", cena=cena_predikce))

            # Výpočet splátky
            r = (urok / 100) / 12
            splatka = uver * r / (1 - (1 + r) ** -mesice) if r > 0 else uver / mesice
            total = splatka * mesice

            current_app.logger.info(
                f"[HYPOTEKA] Výpočet OK | úvěr: {uver} Kč | úrok: {urok}% | splátky: {mesice} měs. | splatka: {round(splatka, 2)} Kč"
            )

            #ulozeni hypoteky do historie jestli je uzivatel prihlaseny
            if "user_id" in session:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO hypoteka_history (user_id, uver, sazba, mesice, splatka, total)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (session["user_id"], uver, urok, mesice, splatka, total))
                    conn.commit()
                    conn.close()
                    app.logger.info(f"[HISTORIE] Uložena splátka uživatele {session['username']}")
                except Exception as e:
                    app.logger.exception("[HISTORIE] Chyba při ukládání výpočtu:")

        except ValueError as ve:
            flash("Zadejte platné číselné hodnoty.")
            current_app.logger.warning(f"[HYPOTEKA] Chybný vstup: {str(e)}")
            return redirect(url_for("hypoteka.hypoteka", cena=cena_predikce))
        except Exception as e:
            app.logger.exception("[HYPOTÉKA] Neočekávaná chyba při výpočtu:")

    return render_template("hypoteka.html",
                           splatka=splatka,
                           total=total,
                           form_data=form_data,
                           cena_predikce=cena_predikce)


#routy na mazani historie hypotek a vypsani na stranku
@hypoteka_routes.route("/moje-vypocty")
def moje_vypocty():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM hypoteka_history
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (session["user_id"],))
        historie = cursor.fetchall()
        conn.close()

        return render_template("moje_vypocty.html", historie=historie)

    except Exception as e:
        current_app.logger.exception("[HISTORIE] Chyba při načítání historie:")
        return render_template("moje_vypocty.html", historie=[])

@hypoteka_routes.route("/smazat-vypocet/<int:vypocet_id>")
def smazat_vypocet(vypocet_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM hypoteka_history
            WHERE id = %s AND user_id = %s
        """, (vypocet_id, session["user_id"]))
        conn.commit()
        conn.close()
        current_app.logger.info(f"[HISTORIE] Výpočet {vypocet_id} smazán uživatelem {session['username']}")
    except Exception as e:
        current_app.logger.exception("[HISTORIE] Chyba při mazání výpočtu:")

    return redirect(url_for("hypoteka.moje_vypocty"))
