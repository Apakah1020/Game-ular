from tkinter import *
import random
import os

GAME_WIDTH = 700
GAME_HEIGHT = 600
SPEED = 125
SPACE_SIZE = 50
BODY_PARTS = 3
SNAKE_COLOR = "#66ff00"
FOOD_COLOR = "#FF0000"
BACKGROUND_COLOR = "#ffffff"
HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "w") as f:
            f.write("0")
    with open(HIGHSCORE_FILE, "r") as f:
        return int(f.read().strip())

def save_highscore(new_highscore):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(new_highscore))

def start_game():
    global canvas, label, snake, foods, score, direction, highscore_label, highscore, enemy_snakes

    menu_frame.destroy()

    score = 0
    direction = 'down'

    label = Label(window, text="Score: {}".format(score), font=('consolas', 40))
    label.pack()

    highscore_label = Label(window, text="High Score: {}".format(highscore), font=('consolas', 20))
    highscore_label.pack()

    canvas = Canvas(window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
    canvas.pack()

    window.update()

    window_width = window.winfo_width()
    window_height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))

    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    window.bind('<Left>', lambda event: change_direction('left'))
    window.bind('<Right>', lambda event: change_direction('right'))
    window.bind('<Up>', lambda event: change_direction('up'))
    window.bind('<Down>', lambda event: change_direction('down'))

    snake = Snake()

    foods = []
    for _ in range(3):
        foods.append(Food())

    enemy_snakes = []
    for _ in range(1):
        enemy_snakes.append(EnemySnake())

    next_turn(snake, foods)

class Snake:
    def __init__(self):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []

        for i in range(0, BODY_PARTS):
            self.coordinates.append([0, 0])

        for x, y in self.coordinates:
            square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
            self.squares.append(square)

class Food:
    def __init__(self):
        self.coordinates = self.place_food()
        self.id = canvas.create_oval(
            self.coordinates[0], self.coordinates[1],
            self.coordinates[0] + SPACE_SIZE, self.coordinates[1] + SPACE_SIZE,
            fill=FOOD_COLOR, tag="food"
        )

    def place_food(self):
        while True:
            x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
            y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
            if [x, y] not in snake.coordinates:
                return [x, y]

class EnemySnake:
    def __init__(self):
        self.body_size = random.randint(3, 5)
        self.coordinates = []
        self.squares = []
        self.direction = random.choice(['up', 'down', 'left', 'right'])

        x = (GAME_WIDTH // (2 * SPACE_SIZE)) * SPACE_SIZE
        y = (GAME_HEIGHT // (2 * SPACE_SIZE)) * SPACE_SIZE

        for i in range(self.body_size):
            coord = [x, y + i * SPACE_SIZE]
            self.coordinates.append(coord)
            square = canvas.create_rectangle(
                coord[0], coord[1],
                coord[0] + SPACE_SIZE, coord[1] + SPACE_SIZE,
                fill="orange", tag="enemy"
            )
            self.squares.append(square)

    def move(self):
        x, y = self.coordinates[0]

        if self.direction == "up":
            y -= SPACE_SIZE
        elif self.direction == "down":
            y += SPACE_SIZE
        elif self.direction == "left":
            x -= SPACE_SIZE
        elif self.direction == "right":
            x += SPACE_SIZE

        if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
            self.direction = random.choice(['up', 'down', 'left', 'right'])
            return

        self.coordinates.insert(0, [x, y])
        new_square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill="red", tag="enemy")
        self.squares.insert(0, new_square)

        if len(self.coordinates) > self.body_size:
            del self.coordinates[-1]
            canvas.delete(self.squares[-1])
            del self.squares[-1]

        if random.randint(0, 10) < 3:
            self.direction = random.choice(['up', 'down', 'left', 'right'])

def next_turn(snake, foods):
    x, y = snake.coordinates[0]

    if direction == "up":
        y -= SPACE_SIZE
    elif direction == "down":
        y += SPACE_SIZE
    elif direction == "left":
        x -= SPACE_SIZE
    elif direction == "right":
        x += SPACE_SIZE

    snake.coordinates.insert(0, [x, y])
    square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR)
    snake.squares.insert(0, square)

    ate_food = False
    for food in foods:
        if x == food.coordinates[0] and y == food.coordinates[1]:
            ate_food = True
            foods.remove(food)
            canvas.delete(food.id)  # hapus hanya makanan yang dimakan
            foods.append(Food())    # spawn makanan baru
            global score
            score += 1
            label.config(text="Score: {}".format(score))
            break

    if not ate_food:
        del snake.coordinates[-1]
        canvas.delete(snake.squares[-1])
        del snake.squares[-1]

    for enemy in enemy_snakes:
        enemy.move()

    for enemy in enemy_snakes:
        if snake.coordinates[0] in enemy.coordinates:
            game_over()
            return

    if check_collisions(snake):
        game_over()
    else:
        window.after(SPEED, next_turn, snake, foods)

def change_direction(new_direction):
    global direction
    if new_direction == 'left' and direction != 'right':
        direction = new_direction
    elif new_direction == 'right' and direction != 'left':
        direction = new_direction
    elif new_direction == 'up' and direction != 'down':
        direction = new_direction
    elif new_direction == 'down' and direction != 'up':
        direction = new_direction

def check_collisions(snake):
    x, y = snake.coordinates[0]

    if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
        return True

    for body_part in snake.coordinates[1:]:
        if x == body_part[0] and y == body_part[1]:
            return True

    return False

def game_over():
    global score, highscore
    canvas.delete(ALL)
    if score > highscore:
        highscore = score
        save_highscore(highscore)
    canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2 - 50,
                     font=('consolas', 50), text="Kok kalah si", fill="red")
    canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2 + 20,
                     font=('consolas', 30), text=f"Score ente: {score}", fill="white")
    canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2 + 70,
                     font=('consolas', 25), text=f"Highscore ente: {highscore}", fill="white")
    
    restart_button = Button(window, text="Main lagi?", font=("consolas", 20), bg="green", fg="white", command=restart_game)
    canvas.create_window(canvas.winfo_width() / 2, canvas.winfo_height() / 2 + 150, window=restart_button)

def restart_game():
    global menu_frame, highscore
    for widget in window.winfo_children():
        widget.destroy()
    
    menu_frame = Frame(window, width=GAME_WIDTH, height=GAME_HEIGHT, bg="blue")
    menu_frame.pack()

    title = Label(menu_frame, text="Snake Game", font=("consolas", 50), bg="black", fg="green")
    title.pack(pady=40)

    high_label = Label(menu_frame, text=f"Your High Score: {highscore}", font=("consolas", 25), bg="black", fg="white")
    high_label.pack(pady=10)

    start_button = Button(menu_frame, text="Start", font=("consolas", 30), bg="green", fg="white", command=start_game)
    start_button.pack(pady=20)

window = Tk()
window.title("Snake Game with High Score")
window.resizable(False, False)

highscore = load_highscore()

menu_frame = Frame(window, width=GAME_WIDTH, height=GAME_HEIGHT, bg="purple")
menu_frame.pack()

title = Label(menu_frame, text="Game ular Kali", font=("consolas", 50), bg="black", fg="green")
title.pack(pady=40)

high_label = Label(menu_frame, text=f"High score ente: {highscore}", font=("consolas", 25), bg="black", fg="white")
high_label.pack(pady=10)

start_button = Button(menu_frame, text="Mulai?", font=("consolas", 30), bg="green", fg="white", command=start_game)
start_button.pack(pady=20)

window.mainloop()
