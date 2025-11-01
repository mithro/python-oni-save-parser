"""Tests for game objects parsing."""

import pytest

from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.game_objects import (
    GameObject,
    GameObjectBehavior,
    GameObjectGroup,
    Quaternion,
    Vector3,
    parse_game_objects,
    unparse_game_objects,
)
from oni_save_parser.save_structure.game_objects.behavior_parser import (
    parse_behavior,
    unparse_behavior,
)
from oni_save_parser.save_structure.game_objects.group_parser import (
    parse_game_object_group,
    unparse_game_object_group,
)
from oni_save_parser.save_structure.game_objects.object_parser import (
    parse_game_object,
    parse_quaternion,
    parse_vector3,
    unparse_game_object,
    unparse_quaternion,
    unparse_vector3,
)
from oni_save_parser.save_structure.type_templates import TypeInfo, TypeTemplate, TypeTemplateMember


def create_test_templates() -> list[TypeTemplate]:
    """Create minimal test type templates."""
    # MinionIdentity template
    minion_template = TypeTemplate(
        name="MinionIdentity",
        fields=[
            TypeTemplateMember(name="name", type=TypeInfo(info=12)),  # String
            TypeTemplateMember(name="age", type=TypeInfo(info=6)),  # Int32
        ],
        properties=[],
    )

    # Health template
    health_template = TypeTemplate(
        name="Health",
        fields=[
            TypeTemplateMember(name="hitpoints", type=TypeInfo(info=10)),  # Single (float)
            TypeTemplateMember(name="maxHitpoints", type=TypeInfo(info=10)),  # Single
        ],
        properties=[],
    )

    return [minion_template, health_template]


def test_parse_vector3():
    """Should parse Vector3."""
    writer = BinaryWriter()
    writer.write_single(1.0)
    writer.write_single(2.0)
    writer.write_single(3.0)

    parser = BinaryParser(writer.data)
    vector = parse_vector3(parser)

    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0


def test_parse_quaternion():
    """Should parse Quaternion."""
    writer = BinaryWriter()
    writer.write_single(0.0)
    writer.write_single(0.0)
    writer.write_single(0.0)
    writer.write_single(1.0)

    parser = BinaryParser(writer.data)
    quat = parse_quaternion(parser)

    assert quat.x == 0.0
    assert quat.y == 0.0
    assert quat.z == 0.0
    assert quat.w == 1.0


def test_round_trip_vector3():
    """Should round-trip Vector3."""
    original = Vector3(x=1.5, y=2.5, z=3.5)

    writer = BinaryWriter()
    unparse_vector3(writer, original)

    parser = BinaryParser(writer.data)
    parsed = parse_vector3(parser)

    assert parsed.x == original.x
    assert parsed.y == original.y
    assert parsed.z == original.z


def test_round_trip_quaternion():
    """Should round-trip Quaternion."""
    original = Quaternion(x=0.1, y=0.2, z=0.3, w=0.4)

    writer = BinaryWriter()
    unparse_quaternion(writer, original)

    parser = BinaryParser(writer.data)
    parsed = parse_quaternion(parser)

    # Use approximate comparison for single-precision floats
    assert parsed.x == pytest.approx(original.x, rel=1e-6)
    assert parsed.y == pytest.approx(original.y, rel=1e-6)
    assert parsed.z == pytest.approx(original.z, rel=1e-6)
    assert parsed.w == pytest.approx(original.w, rel=1e-6)


def test_parse_behavior_simple():
    """Should parse simple behavior with template data."""
    templates = create_test_templates()

    writer = BinaryWriter()
    writer.write_klei_string("MinionIdentity")

    # Build behavior data
    data_writer = BinaryWriter()
    data_writer.write_klei_string("Meep")  # name
    data_writer.write_int32(50)  # age

    writer.write_int32(len(data_writer.data))  # data length
    writer.write_bytes(data_writer.data)

    parser = BinaryParser(writer.data)
    behavior = parse_behavior(parser, templates)

    assert behavior.name == "MinionIdentity"
    assert behavior.template_data is not None
    assert behavior.template_data["name"] == "Meep"
    assert behavior.template_data["age"] == 50
    assert behavior.extra_data is None
    assert behavior.extra_raw == b""


def test_parse_behavior_with_extra_raw():
    """Should parse behavior with extra raw data."""
    templates = create_test_templates()

    writer = BinaryWriter()
    writer.write_klei_string("Health")

    # Build behavior data with extra bytes
    data_writer = BinaryWriter()
    data_writer.write_single(100.0)  # hitpoints
    data_writer.write_single(100.0)  # maxHitpoints
    data_writer.write_bytes(b"\x01\x02\x03")  # extra raw

    writer.write_int32(len(data_writer.data))
    writer.write_bytes(data_writer.data)

    parser = BinaryParser(writer.data)
    behavior = parse_behavior(parser, templates)

    assert behavior.name == "Health"
    assert behavior.template_data is not None
    assert behavior.template_data["hitpoints"] == 100.0
    assert behavior.extra_raw == b"\x01\x02\x03"


def test_parse_behavior_template_not_found():
    """Should handle behavior with template not found."""
    templates = create_test_templates()

    writer = BinaryWriter()
    writer.write_klei_string("UnknownBehavior")
    writer.write_int32(10)  # data length
    writer.write_bytes(b"\x00" * 10)  # dummy data

    parser = BinaryParser(writer.data)
    behavior = parse_behavior(parser, templates)

    assert behavior.name == "UnknownBehavior"
    assert behavior.template_data is None
    assert len(behavior.extra_raw) == 10


def test_round_trip_behavior():
    """Should round-trip behavior."""
    templates = create_test_templates()
    original = GameObjectBehavior(
        name="MinionIdentity",
        template_data={"name": "Meep", "age": 50},
        extra_data=None,
        extra_raw=b"",
    )

    writer = BinaryWriter()
    unparse_behavior(writer, templates, original)

    parser = BinaryParser(writer.data)
    parsed = parse_behavior(parser, templates)

    assert parsed.name == original.name
    assert parsed.template_data == original.template_data
    assert parsed.extra_raw == original.extra_raw


def test_parse_game_object():
    """Should parse game object."""
    templates = create_test_templates()

    writer = BinaryWriter()
    # Position
    writer.write_single(10.0)
    writer.write_single(20.0)
    writer.write_single(30.0)
    # Rotation
    writer.write_single(0.0)
    writer.write_single(0.0)
    writer.write_single(0.0)
    writer.write_single(1.0)
    # Scale
    writer.write_single(1.0)
    writer.write_single(1.0)
    writer.write_single(1.0)
    # Folder
    writer.write_byte(5)
    # Behavior count
    writer.write_int32(0)

    parser = BinaryParser(writer.data)
    obj = parse_game_object(parser, templates)

    assert obj.position.x == 10.0
    assert obj.position.y == 20.0
    assert obj.position.z == 30.0
    assert obj.rotation.w == 1.0
    assert obj.scale.x == 1.0
    assert obj.folder == 5
    assert len(obj.behaviors) == 0


def test_parse_game_object_with_behaviors():
    """Should parse game object with behaviors."""
    templates = create_test_templates()

    writer = BinaryWriter()
    # Transform
    for _ in range(3):  # position
        writer.write_single(0.0)
    for _ in range(4):  # rotation
        writer.write_single(0.0)
    for _ in range(3):  # scale
        writer.write_single(1.0)
    writer.write_byte(0)  # folder

    # 2 behaviors
    writer.write_int32(2)

    # Behavior 1: MinionIdentity
    writer.write_klei_string("MinionIdentity")
    data1 = BinaryWriter()
    data1.write_klei_string("Meep")
    data1.write_int32(50)
    writer.write_int32(len(data1.data))
    writer.write_bytes(data1.data)

    # Behavior 2: Health
    writer.write_klei_string("Health")
    data2 = BinaryWriter()
    data2.write_single(100.0)
    data2.write_single(100.0)
    writer.write_int32(len(data2.data))
    writer.write_bytes(data2.data)

    parser = BinaryParser(writer.data)
    obj = parse_game_object(parser, templates)

    assert len(obj.behaviors) == 2
    assert obj.behaviors[0].name == "MinionIdentity"
    assert obj.behaviors[1].name == "Health"


def test_round_trip_game_object():
    """Should round-trip game object."""
    templates = create_test_templates()
    original = GameObject(
        position=Vector3(x=1.0, y=2.0, z=3.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=5,
        behaviors=[
            GameObjectBehavior(
                name="MinionIdentity",
                template_data={"name": "Meep", "age": 50},
                extra_data=None,
                extra_raw=b"",
            )
        ],
    )

    writer = BinaryWriter()
    unparse_game_object(writer, templates, original)

    parser = BinaryParser(writer.data)
    parsed = parse_game_object(parser, templates)

    assert parsed.position.x == original.position.x
    assert parsed.folder == original.folder
    assert len(parsed.behaviors) == len(original.behaviors)


def test_parse_game_object_group():
    """Should parse game object group."""
    templates = create_test_templates()

    writer = BinaryWriter()
    writer.write_klei_string("Minion")
    writer.write_int32(1)  # instance count

    # Build group data
    data = BinaryWriter()
    # One game object
    for _ in range(3):
        data.write_single(0.0)  # position
    for _ in range(4):
        data.write_single(0.0)  # rotation
    for _ in range(3):
        data.write_single(1.0)  # scale
    data.write_byte(0)  # folder
    data.write_int32(0)  # behavior count

    writer.write_int32(len(data.data))
    writer.write_bytes(data.data)

    parser = BinaryParser(writer.data)
    group = parse_game_object_group(parser, templates)

    assert group.prefab_name == "Minion"
    assert len(group.objects) == 1


def test_parse_game_object_group_multiple_objects():
    """Should parse game object group with multiple objects."""
    templates = create_test_templates()

    writer = BinaryWriter()
    writer.write_klei_string("Tile")
    writer.write_int32(3)  # instance count

    # Build group data with 3 objects
    data = BinaryWriter()
    for _ in range(3):  # 3 objects
        for _ in range(3):
            data.write_single(0.0)  # position
        for _ in range(4):
            data.write_single(0.0)  # rotation
        for _ in range(3):
            data.write_single(1.0)  # scale
        data.write_byte(0)  # folder
        data.write_int32(0)  # behavior count

    writer.write_int32(len(data.data))
    writer.write_bytes(data.data)

    parser = BinaryParser(writer.data)
    group = parse_game_object_group(parser, templates)

    assert group.prefab_name == "Tile"
    assert len(group.objects) == 3


def test_round_trip_game_object_group():
    """Should round-trip game object group."""
    templates = create_test_templates()
    original = GameObjectGroup(
        prefab_name="Minion",
        objects=[
            GameObject(
                position=Vector3(x=1.0, y=2.0, z=3.0),
                rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
                scale=Vector3(x=1.0, y=1.0, z=1.0),
                folder=0,
                behaviors=[],
            )
        ],
    )

    writer = BinaryWriter()
    unparse_game_object_group(writer, templates, original)

    parser = BinaryParser(writer.data)
    parsed = parse_game_object_group(parser, templates)

    assert parsed.prefab_name == original.prefab_name
    assert len(parsed.objects) == len(original.objects)


def test_parse_game_objects():
    """Should parse game objects (top level)."""
    templates = create_test_templates()

    writer = BinaryWriter()
    writer.write_int32(2)  # 2 groups

    # Group 1: Minion
    writer.write_klei_string("Minion")
    writer.write_int32(1)
    data1 = BinaryWriter()
    for _ in range(3):
        data1.write_single(0.0)  # position
    for _ in range(4):
        data1.write_single(0.0)  # rotation
    for _ in range(3):
        data1.write_single(1.0)  # scale
    data1.write_byte(0)
    data1.write_int32(0)
    writer.write_int32(len(data1.data))
    writer.write_bytes(data1.data)

    # Group 2: Tile
    writer.write_klei_string("Tile")
    writer.write_int32(1)
    data2 = BinaryWriter()
    for _ in range(3):
        data2.write_single(0.0)
    for _ in range(4):
        data2.write_single(0.0)
    for _ in range(3):
        data2.write_single(1.0)
    data2.write_byte(0)
    data2.write_int32(0)
    writer.write_int32(len(data2.data))
    writer.write_bytes(data2.data)

    parser = BinaryParser(writer.data)
    groups = parse_game_objects(parser, templates)

    assert len(groups) == 2
    assert groups[0].prefab_name == "Minion"
    assert groups[1].prefab_name == "Tile"


def test_round_trip_game_objects():
    """Should round-trip game objects."""
    templates = create_test_templates()
    original = [
        GameObjectGroup(
            prefab_name="Minion",
            objects=[
                GameObject(
                    position=Vector3(x=1.0, y=2.0, z=3.0),
                    rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
                    scale=Vector3(x=1.0, y=1.0, z=1.0),
                    folder=0,
                    behaviors=[],
                )
            ],
        )
    ]

    writer = BinaryWriter()
    unparse_game_objects(writer, templates, original)

    parser = BinaryParser(writer.data)
    parsed = parse_game_objects(parser, templates)

    assert len(parsed) == len(original)
    assert parsed[0].prefab_name == original[0].prefab_name


def test_parse_game_object_invalid_behavior_count():
    """Should raise error on invalid behavior count."""
    templates = create_test_templates()

    writer = BinaryWriter()
    for _ in range(3):
        writer.write_single(0.0)  # position
    for _ in range(4):
        writer.write_single(0.0)  # rotation
    for _ in range(3):
        writer.write_single(1.0)  # scale
    writer.write_byte(0)  # folder
    writer.write_int32(-1)  # invalid behavior count

    parser = BinaryParser(writer.data)

    with pytest.raises(CorruptionError, match="Invalid behavior count"):
        parse_game_object(parser, templates)


def test_parse_game_object_group_invalid_instance_count():
    """Should raise error on invalid instance count."""
    templates = create_test_templates()

    writer = BinaryWriter()
    writer.write_klei_string("Minion")
    writer.write_int32(-1)  # invalid instance count

    parser = BinaryParser(writer.data)

    with pytest.raises(CorruptionError, match="Invalid instance count"):
        parse_game_object_group(parser, templates)


def test_parse_game_objects_invalid_group_count():
    """Should raise error on invalid group count."""
    templates = create_test_templates()

    writer = BinaryWriter()
    writer.write_int32(-1)  # invalid group count

    parser = BinaryParser(writer.data)

    with pytest.raises(CorruptionError, match="Invalid game object group count"):
        parse_game_objects(parser, templates)
