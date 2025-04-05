import pandas as pd

def predict_price(app, metraz, rozloha_text, energeticka_text, stav_text, lokalita_text):
    try:
        rozloha = int(''.join(filter(str.isdigit, rozloha_text)))
        energeticka = app.energy_mapping.get(energeticka_text)
        stav = app.condition_mapping.get(stav_text)
        lokalita = app.location_mapping.get(lokalita_text)

        if None in [energeticka, stav, lokalita]:
            app.logger.warning(f"[MAPOVÁNÍ] Chybějící hodnota: energeticka={energeticka}, stav={stav}, lokalita={lokalita}")
            return None

        input_data = pd.DataFrame([{
            "metraz": metraz / 10,
            "rozloha": rozloha,
            "energeticka_narocnost": energeticka,
            "stav": stav,
            "lokalita": lokalita
        }])

        scaled_input = app.scaler.transform(input_data)
        prediction = app.model.predict(scaled_input, verbose=0)
        return prediction[0][0] * 1_000_000

    except Exception as e:
        app.logger.exception(f"[PREDIKCE] Chyba při výpočtu predikce: {e}")
        return None
