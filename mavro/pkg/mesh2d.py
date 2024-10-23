class Mesh2D:
    def __init__(self, max_xy: tuple[int, int] | None = None, background: str | None = None) -> None:
        self.max_x, self.max_y = max_xy or 1, 1
        self.background: str = background or "."
        self.tiles: list[tuple[int, int] | str] = [
            (0, 0), self.background,
            (0, 1), self.background,
            (1, 0), self.background,
            (1, 1), self.background,
        ]
    def __mul__(self, value: int) -> None:
        self.max_x, self.max_y = self.max_x * value, self.max_y * value
    def __matmul__(self, value: tuple[tuple[int, int], str]):
        if value[0] in self.tiles:
            self.tiles.pop(self.tiles.index(value[0]) + 1)
            self.tiles.remove(value[0])
        self.tiles.insert(0, value[0])
        self.tiles.insert(1, value[1])
    def public__render(self) -> str:
        val: str = ""
        for y in range(0, self.max_y):
            for x in range(self.max_x):
                try:
                    val += self.tiles[self.tiles.index((x, y)) + 1]
                except (IndexError, ValueError):
                    val += self.background
            val += "\n"
        return val