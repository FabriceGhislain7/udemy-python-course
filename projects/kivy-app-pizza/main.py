from kivy.app import App
from kivy.properties import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.behaviors import CoverBehavior

from http_client import HttpClient
from models import Pizza
from storage_manager import StorageManager


class PizzaWidget(BoxLayout):
    nom = StringProperty()
    # NumericProperty / BooleanProperty
    ingredients = StringProperty()
    prix = NumericProperty()
    vegetarienne = BooleanProperty()


class MainWidget(FloatLayout):
    recycleView = ObjectProperty(None)
    error_str = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        """self.pizzas = [
            Pizza("4 fromages", "chèvre, emmental, brie, comté", 9.5, True),
            Pizza("Chorizo", "tomates, chorizo, parmesan", 11.2, False),
            Pizza("Calzone", "fromage, jambon, champignons", 10, False)
        ]"""

        HttpClient().get_pizzas(self.on_server_data, self.on_server_error)

    def on_parent(self, widget, parent):
        # l = [pizza.get_dictionary() for pizza in self.pizzas]
        pizzas_dict = StorageManager().load_data("pizzas")
        if pizzas_dict:
            self.recycleView.data = pizzas_dict

    def on_server_data(self, pizzas_dict):
        self.recycleView.data = pizzas_dict
        StorageManager().save_data("pizzas", pizzas_dict)

    def on_server_error(self, error):
        print("ERREUR: " + error)
        self.error_str = "ERREUR: " + error


class PizzaApp(App):
    pass


PizzaApp().run()

