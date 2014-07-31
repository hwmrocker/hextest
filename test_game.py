from game import Group, Position, Map


class MockTile(object):

    def __init__(self, color):
        self.color = color
        self.group = Group([self])

    def set_color(self, color):
        self.color = color


def test_group_creation_from_tile():
    t = MockTile("black")
    assert t.group is not None
    assert t.group.color == "black"

    bg = Group(tiles=[t], color="white")
    assert bg.color == "white"
    assert t.color == "white"
    assert t.group.color == "white"


def test_group_merge():
    bg = Group(color="black")
    groups = []
    tiles = []
    for col in ["red", "greem", "blue", "yellow"]:
        tile = MockTile(col)
        group = tile.group
        tiles.append(tile)
        groups.append(group)

    for t, g in zip(tiles, groups):
        assert t.group == g

    groups[0].merge(groups[1])

    for g in groups:
        assert groups[1] not in g.neighbours
    # for t,g in zip(tiles, groups):
        # assert t.group == g


def test_position():
    p = Position(1, 1)
    position_list = list(map(lambda e: e.offset, p.neighbours))
    for offset_tuple in [(1, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1)]:
        assert offset_tuple in position_list
    assert len(p.neighbours) == 6
    p = Position(2, 1)
    position_list = list(map(lambda e: e.offset, p.neighbours))
    for offset_tuple in [(1, 0), (2, 0), (3, 0), (3, 1), (2, 2), (1, 1)]:
        assert offset_tuple in position_list
    assert len(p.neighbours) == 6


def test_map():
    m = Map(filename="foo")
    assert m._is_position_valid(Position(2, 2))
    assert m._is_position_valid(Position(15, 2))
    assert m._is_position_valid(Position(16, 2)) == False
    assert m._is_position_valid(Position(15, 1))
    assert m._is_position_valid(Position(16, 1)) == False
    assert m._is_position_valid(Position(0, 0))
    assert m._is_position_valid(Position(-1, 0)) == False
    assert m._is_position_valid(Position(0, -1)) == False
    assert m._is_position_valid(Position(-1, -1)) == False
    assert m._is_position_valid(Position(0, 11))
    assert m._is_position_valid(Position(0, 12)) == False
    assert m._is_position_valid(Position(15, 12)) == False
    assert m._is_position_valid(Position(15, 11))
