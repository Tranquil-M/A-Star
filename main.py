import pygame
import math
from queue import PriorityQueue

width: int = 800
height: int = 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("A-Star Algorithm Visualization")

_red = (255, 0, 0)
_green = (0, 255, 0)
_blue = (0, 0, 255)
_yellow = (255, 255, 0)
_white = (255, 255, 255)
_black = (0, 0, 0)
_purple = (128, 0, 128)
_orange = (255, 165, 0)
_grey = (128, 128, 128)
_turquoise = (64, 224, 208)


class Node:
    def __init__(self, row, collumn, width, total_rows) -> None:
        self.row = row
        self.collumn = collumn
        self.x = row * width
        self.y = collumn * width
        self.width = width
        self.color = _white
        self.neighbors = []
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.collumn

    def is_closed(self):
        return self.color == _red

    def is_open(self):
        return self.color == _green

    def is_barrier(self):
        return self.color == _black

    def is_start(self):
        return self.color == _orange

    def is_end(self):
        return self.color == _purple

    def make_start(self):
        self.color = _orange

    def reset(self):
        self.color = _white

    def make_closed(self):
        self.color = _red

    def make_open(self):
        self.color = _green

    def make_barrier(self):
        self.color = _black

    def make_end(self):
        self.color = _purple

    def make_path(self):
        self.color = _turquoise

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if (
            self.row < self.total_rows - 1
            and not grid[self.row + 1][self.collumn].is_barrier()
        ):
            self.neighbors.append(grid[self.row + 1][self.collumn])

        if self.row > 0 and not grid[self.row - 1][self.collumn].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.collumn])

        if (
            self.collumn < self.total_rows - 1
            and not grid[self.row][self.collumn + 1].is_barrier()
        ):
            self.neighbors.append(grid[self.row][self.collumn + 1])

        if (
            self.collumn < self.total_rows - 1
            and not grid[self.row][self.collumn - 1].is_barrier()
        ):
            self.neighbors.append(grid[self.row][self.collumn - 1])

    def __lt__(self, other):
        return False


def heuristic(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = heuristic(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(
                    neighbor.get_pos(), end.get_pos()
                )
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Node(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(screen, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(screen, _grey, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(screen, _grey, (j * gap, 0), (j * gap, width))


def draw(screen, grid, rows, width):
    screen.fill(_white)

    for row in grid:
        for spot in row:
            spot.draw(screen)

    draw_grid(screen, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col


def main(screen, width):
    rows = 50
    grid = make_grid(rows, width)

    start = None
    end = None

    run = True

    while run:
        draw(screen, grid, rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None

                if spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algorithm(lambda: draw(screen, grid, rows, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(rows, width)

    pygame.quit()


if __name__ == "__main__":
    main(screen, width)
