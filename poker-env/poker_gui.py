import tkinter as tk
import math
import queue

from pokerkit import State
from game_state import SimpleState, PlayerData


player_name_font_size = 22
player_stack_font_size = 18

player_box_width = 100
player_box_height = 140

card_width = player_box_width / 2
card_height = player_box_height / 2

chip_width = 10
chips_font_size = 16
chip_text_buffor = 20
chip_box_width = 40
chip_box_height = 40

table_player_buffer = 1.5
table_chip_buffer = 0.8

community_cards_total_pot_buffer = 10
total_pot_width = 200
total_pot_height = 25
total_pot_font_size = 16

community_cards_middle_pot_buffer = 40


def get_cards(cards: str):
    return Card(cards[:2]), Card(cards[2:])


def center(x0, y0, x1, y1):
    return (x0 + x1) // 2, (y0 + y1) // 2


def draw_text_rectangle(canvas: tk.Canvas, x0, y0, x1, y1, text, font_size):
    canvas.create_rectangle(
        x0,
        y0,
        x1,
        y1,
        outline="white",
        width=2,
    )
    center_x, center_y = center(x0, y0, x1, y1)
    canvas.create_text(
        center_x,
        center_y,
        text=text,
        fill="white",
        font=("Helvetica", font_size, "bold"),
    )


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
            case "?":  # clubs
                return "black"
            case _:
                raise Exception(f"What's that color? {color}")

    def draw(self, canvas: tk.Canvas, x0: int, y0: int):
        canvas.create_rectangle(
            x0,
            y0,
            x0 + card_width,
            y0 + card_height,
            fill=self.__get_color(),
            outline="white",
            width=2,
        )
        center_x, center_y = center(x0, y0, x0 + card_width, y0 + card_height)
        canvas.create_text(
            center_x,
            center_y,
            text=self.card[0],
            fill="white",
            font=("Helvetica", 24, "bold"),
        )


class Player:
    def __init__(self, player_data: PlayerData):
        self.player_data = player_data

    def draw(self, canvas: tk.Canvas, x0: int, y0: int):
        x1 = x0 + player_box_width
        y1 = y0 + player_box_height
        # drawing cards
        card_1, card_2 = get_cards(self.player_data.cards)
        card_1.draw(canvas, x0, y0)
        card_2.draw(canvas, x0 + card_width, y0)

        # drawing name
        card_y1 = y0 + card_height
        name_box_y1 = (y0 + card_height + y0 + player_box_height) // 2

        draw_text_rectangle(
            canvas,
            x0,
            card_y1,
            x1,
            name_box_y1,
            self.player_data.name,
            player_name_font_size,
        )

        # drawing stack
        draw_text_rectangle(
            canvas,
            x0,
            name_box_y1,
            x1,
            y1,
            str(self.player_data.stack) + " BB",
            player_stack_font_size,
        )

        # actor outline
        if self.player_data.actor:
            canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                outline="yellow",
                width=3,
            )


class Chips:
    def __init__(self, amount: float):
        self.amount = amount

    def draw(self, canvas: tk.Canvas, x0: int, y0: int):
        x1 = x0 + chip_box_width
        y1 = y0 + chip_box_height

        if self.amount <= 0.001:
            return

        # drawing chips
        r = min(y1 - y0, x1 - x0) // 2
        center_x, center_y = center(x0, y0, x1, y1)

        canvas.create_oval(
            center_x - r,
            center_y - r,
            center_x + r,
            center_y + r,
            fill="white",
            outline="red",
            width=chip_width,
        )

        # drawing amount

        canvas.create_text(
            (x0 + x1) // 2,
            y1 + chip_text_buffor,
            text=str(self.amount) + " BB",
            fill="white",
            font=("Helvetica", chips_font_size, "bold"),
        )


class Table:
    def __init__(self, radius: int, x: int, y: int):
        self.radius = radius
        self.x = x
        self.y = y

    def draw(self, canvas: tk.Canvas, simple_state: SimpleState):
        max_players = len(simple_state.players_data)

        x0 = self.x - self.radius
        y0 = self.y - self.radius
        x1 = self.x + self.radius
        y1 = self.y + self.radius

        canvas.create_oval(x0, y0, x1, y1, fill="black", outline="white")

        r_player = self.radius * table_player_buffer
        r_chips = self.radius * table_chip_buffer

        def drawing_coords(angle, r, w, h):
            rad = math.radians(angle)
            x = math.cos(rad) * r
            y = math.sin(rad) * r

            x0 = self.x + int(x) - w // 2
            y0 = self.y + int(y) - h // 2

            return x0, y0

        for n, player_data in enumerate(simple_state.players_data):
            angle = (360 // max_players) * n

            # draw player
            Player(player_data).draw(
                canvas,
                *drawing_coords(angle, r_player, player_box_width, player_box_height),
            )

            # draw player bet
            Chips(player_data.bet).draw(
                canvas,
                *drawing_coords(angle, r_chips, chip_box_width, chip_box_height),
            )

        # draw community cards
        total_community_cards_width = card_width * 5
        r = self.radius * 1.6
        community_cards_offset = (r - total_community_cards_width) // 2
        x0 = self.x - r // 2 + community_cards_offset
        y0 = self.x - self.radius // 2

        community_cards = simple_state.community_cards
        cards = [community_cards[i : i + 2] for i in range(0, len(community_cards), 2)]

        for n, card in enumerate(cards):
            Card(card).draw(canvas, x0 + n * card_width, y0)

        # draw total pot
        draw_text_rectangle(
            canvas,
            self.x - total_pot_width / 2,
            y0 - community_cards_total_pot_buffer - total_pot_height,
            self.x + total_pot_width / 2,
            y0 - community_cards_total_pot_buffer,
            f"Total pot: {simple_state.pot} BB",
            total_pot_font_size,
        )

        # draw middle pot
        Chips(simple_state.middle_pot).draw(
            canvas,
            self.x - chip_box_width / 2,
            y0 + card_height + community_cards_middle_pot_buffer,
        )


class GUI:
    def __init__(self, simple_state: SimpleState, canvas_width=800, canvas_height=800):
        self.simple_state = simple_state
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.event_queue = queue.Queue()

    def create_window(self):
        self.root = tk.Tk()
        self.root.title("Poker Table")
        self.canvas = tk.Canvas(
            self.root, width=self.canvas_width, height=self.canvas_height, bg="black"
        )
        self.canvas.pack()

    def create_table(self, table_radius=200):
        self.table = Table(
            table_radius,
            self.canvas_width // 2,
            self.canvas_height // 2,
        )

    def draw(self):
        self.canvas.delete("all")
        self.table.draw(self.canvas, self.simple_state)

    def update_state(self, pokerkit_state: State):
        self.simple_state.update_state(pokerkit_state)

    def add_event(self, event, *args):
        self.event_queue.put((event, args))

    def _handle_event(self, event, *args):
        event(*args)

    def _proces_events(self):
        try:
            event, args = self.event_queue.get_nowait()
            self._handle_event(event, *args)
            self.event_queue.task_done()
            return True
        except queue.Empty:
            return False

    def _update(self):
        if self._proces_events():
            self.draw()

        self.root.after(100, self._update)

    def main_loop(self):
        self.draw()
        self._update()
        self.root.mainloop()


def example_1():
    gui = GUI()
    gui.create_window()
    gui.create_table()
    gui.add_player(Player("Hans", 8, "AcAd"))
    gui.add_player(Player("Negranu", 25, "5s6h"))
    gui.add_player(Player("Helmuth", 125, "????"))
    gui.draw()
    gui.main_loop()


if __name__ == "__main__":
    example_1()
