"""Performance benchmarks for ONI Save Parser.

These benchmarks establish baseline performance and help detect regressions.
Run with: pytest tests/benchmark --benchmark-only
"""

from pathlib import Path

import pytest

from oni_save_parser import get_colony_info, get_prefab_counts, load_save_file, save_to_file
from oni_save_parser.parser import BinaryParser, BinaryWriter
from oni_save_parser.save_structure import SaveGame, parse_save_game, unparse_save_game
from oni_save_parser.save_structure.game_objects import (
    GameObject,
    GameObjectGroup,
    Quaternion,
    Vector3,
)
from oni_save_parser.save_structure.header import SaveGameHeader, SaveGameInfo
from oni_save_parser.save_structure.type_templates import TypeInfo, TypeTemplate, TypeTemplateMember


def create_benchmark_save_game(
    num_duplicants: int = 10,
    num_tiles: int = 1000,
    num_buildings: int = 100,
) -> SaveGame:
    """Create a realistic test save game for benchmarking."""
    game_info = SaveGameInfo(
        number_of_cycles=500,
        number_of_duplicants=num_duplicants,
        base_name="Benchmark Colony",
        is_auto_save=False,
        original_save_name="Benchmark Colony Cycle 500",
        save_major_version=7,
        save_minor_version=35,
        cluster_id="vanilla",
        sandbox_enabled=False,
        colony_guid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        dlc_id="EXPANSION1_ID",
    )
    header = SaveGameHeader(
        build_version=555555,
        header_version=1,
        is_compressed=True,
        game_info=game_info,
    )

    # Create type templates (keep simple to avoid template_name issues in benchmarks)
    templates = [
        TypeTemplate(
            name="Klei.SaveFileRoot",
            fields=[
                TypeTemplateMember(name="buildVersion", type=TypeInfo(info=6)),
                TypeTemplateMember(name="worldID", type=TypeInfo(info=12)),
            ],
            properties=[],
        ),
        TypeTemplate(
            name="Game+Settings",
            fields=[
                TypeTemplateMember(name="difficulty", type=TypeInfo(info=6)),
            ],
            properties=[],
        ),
    ]

    world = {"buildVersion": 555555, "worldID": "BenchmarkWorld"}
    settings = {"difficulty": 2}

    # Create game objects
    minion_obj = GameObject(
        position=Vector3(x=100.0, y=200.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=1,
        behaviors=[],
    )

    tile_obj = GameObject(
        position=Vector3(x=50.0, y=100.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=2,
        behaviors=[],
    )

    building_obj = GameObject(
        position=Vector3(x=150.0, y=150.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=3,
        behaviors=[],
    )

    game_objects = [
        GameObjectGroup(prefab_name="Minion", objects=[minion_obj] * num_duplicants),
        GameObjectGroup(prefab_name="Tile", objects=[tile_obj] * num_tiles),
        GameObjectGroup(prefab_name="OxygenDiffuser", objects=[building_obj] * num_buildings),
    ]

    # Create realistic sim data (compressed in real saves)
    sim_data = b"\x00" * 10000

    return SaveGame(
        header=header,
        templates=templates,
        world=world,
        settings=settings,
        sim_data=sim_data,
        version_major=7,
        version_minor=35,
        game_objects=game_objects,
        game_data=b"",
    )


@pytest.fixture(scope="module")
def small_save() -> SaveGame:
    """Small save for quick benchmarks."""
    return create_benchmark_save_game(num_duplicants=5, num_tiles=100, num_buildings=20)


@pytest.fixture(scope="module")
def medium_save() -> SaveGame:
    """Medium save for realistic benchmarks."""
    return create_benchmark_save_game(num_duplicants=10, num_tiles=1000, num_buildings=100)


@pytest.fixture(scope="module")
def large_save() -> SaveGame:
    """Large save for stress testing."""
    return create_benchmark_save_game(num_duplicants=20, num_tiles=5000, num_buildings=500)


@pytest.fixture(scope="module")
def small_save_bytes(small_save: SaveGame) -> bytes:
    """Serialized small save."""
    return unparse_save_game(small_save)


@pytest.fixture(scope="module")
def medium_save_bytes(medium_save: SaveGame) -> bytes:
    """Serialized medium save."""
    return unparse_save_game(medium_save)


@pytest.fixture(scope="module")
def large_save_bytes(large_save: SaveGame) -> bytes:
    """Serialized large save."""
    return unparse_save_game(large_save)


# Parsing Benchmarks


def test_benchmark_parse_small_save(benchmark, small_save_bytes: bytes):
    """Benchmark parsing a small save file."""
    result = benchmark(parse_save_game, small_save_bytes)
    assert result.header.game_info.number_of_duplicants == 5


def test_benchmark_parse_medium_save(benchmark, medium_save_bytes: bytes):
    """Benchmark parsing a medium save file."""
    result = benchmark(parse_save_game, medium_save_bytes)
    assert result.header.game_info.number_of_duplicants == 10


def test_benchmark_parse_large_save(benchmark, large_save_bytes: bytes):
    """Benchmark parsing a large save file."""
    result = benchmark(parse_save_game, large_save_bytes)
    assert result.header.game_info.number_of_duplicants == 20


# Serialization Benchmarks


def test_benchmark_unparse_small_save(benchmark, small_save: SaveGame):
    """Benchmark serializing a small save file."""
    result = benchmark(unparse_save_game, small_save)
    assert len(result) > 0


def test_benchmark_unparse_medium_save(benchmark, medium_save: SaveGame):
    """Benchmark serializing a medium save file."""
    result = benchmark(unparse_save_game, medium_save)
    assert len(result) > 0


def test_benchmark_unparse_large_save(benchmark, large_save: SaveGame):
    """Benchmark serializing a large save file."""
    result = benchmark(unparse_save_game, large_save)
    assert len(result) > 0


# Round-trip Benchmarks


def test_benchmark_round_trip_small_save(benchmark, small_save_bytes: bytes):
    """Benchmark full round-trip (parse + serialize) for small save."""

    def round_trip():
        save = parse_save_game(small_save_bytes)
        return unparse_save_game(save)

    result = benchmark(round_trip)
    assert len(result) > 0


def test_benchmark_round_trip_medium_save(benchmark, medium_save_bytes: bytes):
    """Benchmark full round-trip (parse + serialize) for medium save."""

    def round_trip():
        save = parse_save_game(medium_save_bytes)
        return unparse_save_game(save)

    result = benchmark(round_trip)
    assert len(result) > 0


# API Benchmarks


def test_benchmark_get_colony_info(benchmark, medium_save: SaveGame):
    """Benchmark extracting colony information."""
    result = benchmark(get_colony_info, medium_save)
    assert result["colony_name"] == "Benchmark Colony"


def test_benchmark_get_prefab_counts(benchmark, medium_save: SaveGame):
    """Benchmark counting prefabs."""
    result = benchmark(get_prefab_counts, medium_save)
    assert result["Minion"] == 10


# File I/O Benchmarks


def test_benchmark_file_write(benchmark, tmp_path: Path, medium_save: SaveGame):
    """Benchmark writing save file to disk."""
    save_path = tmp_path / "benchmark.sav"

    def write_file():
        save_to_file(medium_save, save_path)

    benchmark(write_file)
    assert save_path.exists()


def test_benchmark_file_read(benchmark, tmp_path: Path, medium_save: SaveGame):
    """Benchmark reading save file from disk."""
    save_path = tmp_path / "benchmark.sav"
    save_to_file(medium_save, save_path)

    result = benchmark(load_save_file, save_path)
    assert result.header.game_info.number_of_duplicants == 10


# Low-level Parser Benchmarks


def test_benchmark_binary_parser_read(benchmark):
    """Benchmark BinaryParser read operations."""
    data = b"\x00" * 10000

    def read_operations():
        parser = BinaryParser(data)
        for _ in range(1000):
            parser.offset = 0
            parser.read_uint32()
            parser.read_int32()
            parser.read_byte()
            parser.read_single()

    benchmark(read_operations)


def test_benchmark_binary_writer_write(benchmark):
    """Benchmark BinaryWriter write operations."""

    def write_operations():
        writer = BinaryWriter()
        for _ in range(1000):
            writer.write_uint32(12345)
            writer.write_int32(-12345)
            writer.write_byte(255)
            writer.write_single(3.14159)
        return writer.data

    result = benchmark(write_operations)
    assert len(result) > 0
