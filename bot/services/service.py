import requests


class BotService:

    base_url = "http://localhost:8000/"

    def check_availability(self):
        response = requests.get(f"{self.base_url}ping/")
        response.raise_for_status()

    def get_menu(self):
        response = requests.get(f'{self.base_url}position/')
        response.raise_for_status()
        return response.json()

    def get_position(self, position_id: int):
        response = requests.get(f"{self.base_url}position/{position_id}/")
        response.raise_for_status()
        return response.json()

    def get_qty_p(self):
        response = requests.get(f'{self.base_url}position/get_qty_p/')
        response.raise_for_status()
        return response.json()

    def add_new_order(self, dt: dict) -> dict:
        response = requests.post(f"{self.base_url}order/", json=dt)
        response.raise_for_status()
        return response.json()

    def get_history(self):
        response = requests.get(f"{self.base_url}/get_history")
        response.raise_for_status()
        return response.json()


bot_service = BotService()
