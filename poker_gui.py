import tkinter as tk
import math
from typing import List


class Card:
    def __init__(self, card: str):
        self.card = card
        if len(card) != 2:
            raise Exception(f"Weird card? {card}")

    def __get_color(self):
        color = self.card[1]
        match color:
            case "s":  # spades
                return "dim gray"
            case "h":  # hearts
                return "red"
            case "d":  # diamonds
                return "blue"
            case "c":  # clubs
                return "dark green"
            case _:
                raise Exception(f"What's that color? {color}")

    # x0, y0 is top left corner of cards, x1, y1 is bottom right corner
    def draw(self, canvas: tk.Canvas, x0: int, y0: int, x1: int, y1: int):
        canvas.create_rectangle(
            x0, y0, x1, y1, fill=self.__get_color(), outline="white", width=2
        )
        center_x = (x0 + x1) // 2
        center_y = (y0 + y1) // 2
        canvas.create_text(
            center_x,
            center_y,
            text=self.card[0],
            fill="white",
            font=("Helvetica", 24, "bold"),
        )


class Player:
    name_font_size = 22
    stack_font_size = 22

    def __init__(self, name: str, big_blinds: int, card_1: Card, card_2: Card):
        self.name = name
        self.big_blinds = big_blinds
        self.card_1 = card_1
        self.card_2 = card_2

    def draw(self, canvas: tk.Canvas, x0: int, y0: int, x1: int, y1: int):
        # drawing cards
        card_x1 = (x0 + x1) // 2
        card_y1 = (y0 + y1) // 2
        self.card_1.draw(canvas, x0, y0, card_x1, card_y1)
        self.card_2.draw(canvas, card_x1, y0, x1, card_y1)
        # drawing name
        name_y1 = (card_y1 + y1) // 2
        canvas.create_rectangle(
            x0, card_y1, x1, name_y1, fill="black", outline="white", width=2
        )
        canvas.create_text(
            (x0 + x1) // 2,
            (card_y1 + name_y1) // 2,
            text=self.name,
            fill="white",
            font=("Helvetica", Player.name_font_size, "bold"),
        )

        # drawing stack
        canvas.create_rectangle(
            x0, name_y1, x1, y1, fill="black", outline="white", width=2
        )
        canvas.create_text(
            (x0 + x1) // 2,
            (y1 + name_y1) // 2,
            text=str(self.big_blinds) + " BB",
            fill="white",
            font=("Helvetica", Player.stack_font_size, "bold"),
        )


class Table:
    player_buffer = 0.5
    player_width = 100
    player_height = 140

    def __init__(self, max_players: int, radius: int, x: int, y: int):
        self.max_players = max_players
        self.radius = radius
        self.x = x
        self.y = y
        self.players: List[Player] = []

    def add_player(self, player: Player):
        self.players.append(player)

        if len(self.players) > self.max_players:
            raise Exception("Too many players!")

    def draw(self, canvas: tk.Canvas):
        x0 = self.x - self.radius
        y0 = self.y - self.radius
        x1 = self.x + self.radius
        y1 = self.y + self.radius

        canvas.create_oval(x0, y0, x1, y1, fill="black", outline="white")

        r = self.radius * (1 + Table.player_buffer)

        for n, player in enumerate(self.players):
            angle = (360 // self.max_players) * n
            rad = math.radians(angle)
            x = math.cos(rad) * r
            y = math.sin(rad) * r

            x0 = self.x + int(x) - Table.player_width // 2
            x1 = self.x + int(x) + Table.player_width // 2

            y0 = self.y + int(y) - Table.player_height // 2
            y1 = self.y + int(y) + Table.player_height // 2

            player.draw(canvas, x0, y0, x1, y1)

        pass


class GUI:
    def __init__(self, canvas_width=800, canvas_height=800):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def create_window(self):
        self.root = tk.Tk()
        self.root.title("Poker Table")
        self.canvas = tk.Canvas(
            self.root, width=self.canvas_width, height=self.canvas_height, bg="black"
        )
        self.canvas.pack()

    def create_table(self, max_players=8, table_radius=200):
        self.table = Table(
            max_players, table_radius, self.canvas_width // 2, self.canvas_height // 2
        )

    def add_player(self, player: Player):
        self.table.add_player(player)

    def draw(self):
        self.table.draw(self.canvas)

    def main_loop(self):
        self.root.mainloop()


def example_1():
    gui = GUI()
    gui.create_window()
    gui.create_table()
    gui.add_player(Player("Hans", 8, Card("Ac"), Card("As")))
    gui.add_player(Player("Negranu", 25, Card("7h"), Card("6h")))
    gui.add_player(Player("Helmuth", 125, Card("Qd"), Card("Jc")))
    gui.draw()
    gui.main_loop()


def main():
    example_1()


if __name__ == "__main__":
    main()
