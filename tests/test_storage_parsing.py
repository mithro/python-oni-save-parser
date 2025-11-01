"""Tests for Storage behavior extra_data parsing."""

import pytest

from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.game_objects.behavior_parser import (
    parse_behavior,
)
from oni_save_parser.save_structure.type_templates import (
    TypeInfo,
    TypeTemplate,
    TypeTemplateMember,
)


def test_parse_storage_with_zero_items() -> None:
    """Test parsing Storage behavior with empty extra_data (0 items)."""
    # Create minimal Storage template
    templates = [
        TypeTemplate(
            name="Storage",
            fields=[
                TypeTemplateMember("onlyFetchMarkedItems", TypeInfo(info=3)),  # Boolean
                TypeTemplateMember("shouldSaveItems", TypeInfo(info=3)),  # Boolean
            ],
            properties=[],
        )
    ]

    # Build binary data for Storage behavior with 0 items
    writer = BinaryWriter()
    writer.write_klei_string("Storage")

    # Build behavior data in temporary buffer
    data_writer = BinaryWriter()
    data_writer.write_boolean(False)  # onlyFetchMarkedItems
    data_writer.write_boolean(True)  # shouldSaveItems
    data_writer.write_int32(0)  # Item count = 0

    # Write length and data
    writer.write_int32(len(data_writer.data))
    writer.write_bytes(data_writer.data)

    # Parse
    parser = BinaryParser(writer.data)
    behavior = parse_behavior(parser, templates)

    # Verify
    assert behavior.name == "Storage"
    assert behavior.template_data == {
        "onlyFetchMarkedItems": False,
        "shouldSaveItems": True,
    }
    assert behavior.extra_data == []  # Empty list of stored items
    assert len(behavior.extra_raw) == 0  # All data should be parsed


def test_parse_storage_with_items() -> None:
    """Test parsing Storage behavior with stored items."""
    # Create templates for Storage and stored item (IronOre)
    templates = [
        TypeTemplate(
            name="Storage",
            fields=[
                TypeTemplateMember("onlyFetchMarkedItems", TypeInfo(info=3)),  # Boolean
                TypeTemplateMember("shouldSaveItems", TypeInfo(info=3)),  # Boolean
            ],
            properties=[],
        ),
        TypeTemplate(
            name="PrimaryElement",
            fields=[
                TypeTemplateMember("ElementID", TypeInfo(info=6)),  # Int32
                TypeTemplateMember("Mass", TypeInfo(info=10)),  # Single (float)
                TypeTemplateMember("Temperature", TypeInfo(info=10)),  # Single
            ],
            properties=[],
        ),
    ]

    # Build binary data for Storage with 1 item (IronOre debris)
    writer = BinaryWriter()
    writer.write_klei_string("Storage")

    # Build behavior data in temporary buffer
    data_writer = BinaryWriter()
    data_writer.write_boolean(False)  # onlyFetchMarkedItems
    data_writer.write_boolean(True)  # shouldSaveItems
    data_writer.write_int32(1)  # Item count = 1

    # Item 1: IronOre debris
    data_writer.write_klei_string("IronOre")  # Prefab name

    # GameObject data
    # Position
    data_writer.write_single(10.5)  # x
    data_writer.write_single(20.5)  # y
    data_writer.write_single(0.0)  # z

    # Rotation (quaternion)
    data_writer.write_single(0.0)
    data_writer.write_single(0.0)
    data_writer.write_single(0.0)
    data_writer.write_single(1.0)

    # Scale
    data_writer.write_single(1.0)
    data_writer.write_single(1.0)
    data_writer.write_single(1.0)

    # Folder
    data_writer.write_byte(0)

    # Behaviors count
    data_writer.write_int32(1)

    # Behavior: PrimaryElement (build in temp buffer)
    behavior_writer = BinaryWriter()
    behavior_writer.write_int32(-1369750864)  # ElementID for IronOre
    behavior_writer.write_single(100.0)  # Mass
    behavior_writer.write_single(293.15)  # Temperature

    # Write behavior to data_writer
    data_writer.write_klei_string("PrimaryElement")
    data_writer.write_int32(len(behavior_writer.data))
    data_writer.write_bytes(behavior_writer.data)

    # Write Storage behavior length and data
    writer.write_int32(len(data_writer.data))
    writer.write_bytes(data_writer.data)

    # Parse
    parser = BinaryParser(writer.data)
    behavior = parse_behavior(parser, templates)

    # Verify
    assert behavior.name == "Storage"
    assert behavior.template_data == {
        "onlyFetchMarkedItems": False,
        "shouldSaveItems": True,
    }
    assert behavior.extra_data is not None
    assert len(behavior.extra_data) == 1

    # Check stored item
    item = behavior.extra_data[0]
    assert item["name"] == "IronOre"
    assert item["position"].x == pytest.approx(10.5)
    assert item["position"].y == pytest.approx(20.5)
    assert len(item["behaviors"]) == 1
    assert item["behaviors"][0].name == "PrimaryElement"
    assert item["behaviors"][0].template_data["ElementID"] == -1369750864
    assert item["behaviors"][0].template_data["Mass"] == pytest.approx(100.0)

    assert len(behavior.extra_raw) == 0  # All data parsed
