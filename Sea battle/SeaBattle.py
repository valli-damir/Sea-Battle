from random import randint

class BoardException(Exception):
    pass
class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за границы доски "
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку "
class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.direction == 0:
                cur_x += i
            elif self.direction == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots
    def Shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid = False, size = 6):
        self.hid = hid
        self.size = size
        self.field = [ ["O"]*size for _ in range(size) ]
        self.count = 0
        self.busy = []
        self.ships = []
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for size, j in enumerate(self.field):
            res += f"\n{size + 1} | " + " | ".join(j) + " | "
        if self.hid:
            res = res.replace("■", "0")
        return res
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)
    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(dx + d.x, dy + d.y)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен ")
                    return False
                else:
                    print("Корабль ранен ")
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо ")
        return False
    def begin(self):
        self.busy = []
class Player:
    def __init__(self, board, opponent):
        self.board = board
        self.opponent = opponent
    def ask(self):
        raise NotImplementedError()
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.opponent.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ходит компьютер: {d.x+1}, {d.y+1}")
        return d
class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход: ").split()
            if len(coords) != 2:
                print("Необходимо ввести 2 координаты ")
                continue
            x, y = coords
            if not (x.isdigit()) or not (y.isdigit()):
                print("Необходимо ввести 2 числа ")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)

class Game:

    def __init__(self, size = 6):
        self.size = size
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True
        self.computer = AI(computer, player)
        self.player = User(player, computer)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for length in lens:
            while True:
                attempts += 1
                if attempts >2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("Игра морской бой")
        print("х - номер строки, "
              "у - номер столбца")

    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска игрока:")
            print(self.player.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.computer.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит игрок ")
                repeat = self.player.move()
            else:
                print("Ходит компьютер ")
                repeat = self.computer.move()
            if repeat:
                num -=1
            if self.computer.board.count == len(self.computer.board.ships):
                print("-"*20)
                print("Игрок выйграл ")
                break
            if self.player.board.count == len(self.player.board.ships):
                print("-" * 20)
                print("Компьютер выйграл ")
                break
            num += 1

    def Start(self):
        self.greet()
        self.loop()


g = Game()
g.Start()
