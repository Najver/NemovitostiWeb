from utils.predictor import predict_price
from unittest.mock import MagicMock

class MockApp:
    def __init__(self):
        self.location_mapping = {"Praha": 1}
        self.energy_mapping = {"C": 3}
        self.condition_mapping = {"Po rekonstrukci": 4}
        self.scaler = MagicMock()
        self.model = MagicMock()
        self.scaler.transform = lambda x: x
        self.model.predict = lambda x, verbose=0: [[7.2]]

def test_predict_price_returns_value():
    app = MockApp()

    price = predict_price(
        app,
        metraz=60,
        rozloha_text="3+kk",
        energeticka_text="C",
        stav_text="Po rekonstrukci",
        lokalita_text="Praha"
    )

    assert price == 7_200_000
