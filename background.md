# Oxygen Not Included Save File Format - Technical Background

## Overview

**Oxygen Not Included (ONI)** is a space-colony simulation game developed by Klei Entertainment. The game uses a custom binary save file format with the `.sav` extension that stores all colony data including duplicant statistics, building states, world configuration, and gameplay progression.

This document provides comprehensive technical information about the ONI save file format, existing parsing tools, and the underlying serialization system.

## Game Information

- **Developer:** Klei Entertainment
- **Engine:** Unity
- **Platform:** .NET/C# (Unity runtime)
- **Current Save Version:** 7.31 (as of latest stable release)
- **Save File Extension:** `.sav`

## Save File Structure

### High-Level Format

ONI save files follow a hierarchical binary structure:

```
[Header]
[Type Templates]
[Compressed or Uncompressed Body]
  ├── [World Data]
  ├── [Settings]
  ├── [Simulation Data]
  ├── [KSAV Marker + Version]
  ├── [Game Objects]
  └── [Game Data]
```

### Header Structure

The header contains metadata about the save file:

```
Offset | Size | Type    | Description
-------|------|---------|---------------------------
0x00   | 4    | UInt32  | Build Version
0x04   | 4    | UInt32  | Header Size (bytes)
0x08   | 4    | UInt32  | Header Version
0x0C   | 4    | UInt32  | Compression Flag (if header version >= 1)
0x10   | N    | JSON    | Game Info (UTF-8 encoded JSON)
```

**Game Info JSON** contains:
- `saveMajorVersion`: Major version number
- `saveMinorVersion`: Minor version number
- `dlcId`: DLC identifier (e.g., "EXPANSION1_ID" for Spaced Out DLC, or empty for base game)
- Other metadata about the save

### Compression

Starting with header version 1, save files support optional zlib compression:
- If `isCompressed` flag is true, the body after the header and type templates is compressed with zlib
- Compression uses standard zlib deflate algorithm
- The original TypeScript parser uses the `pako` library for decompression
- Approximately 95% of the save data can be zlib-compressed

### Type Templates Section

Before the main body, save files include a **Type Templates** section that describes the serialization schema:

```
[Int32: Template Count]
For each template:
  [KleiString: Type Name]
  [Int32: Field Count]
  [Int32: Property Count]
  For each field:
    [KleiString: Field Name]
    [TypeInfo: Field Type Information]
  For each property:
    [KleiString: Property Name]
    [TypeInfo: Property Type Information]
```

**Type Templates** are critical for parsing because they:
1. Define the structure of serialized .NET classes
2. List fields and properties in their serialization order
3. Specify data types for each member
4. Enable proper deserialization without hardcoded schemas

### Save Body Structure

After decompression (if applicable), the body contains:

1. **World Marker**: KleiString "world"
2. **World Data**: Binary world/map data (format not fully documented)
3. **Settings**: Game settings and configuration
4. **Simulation Data Length**: Int32
5. **Simulation Data**: Raw binary simulation state
6. **KSAV Marker**: 4-byte ASCII string "KSAV"
7. **Version Numbers**: Int32 major, Int32 minor
8. **Game Objects**: Serialized game entities (duplicants, buildings, etc.)
9. **Game Data**: Additional game state information

## KSerialization System

**KSerialization** is Klei Entertainment's custom serialization framework used in Oxygen Not Included. It's implemented in the `KSerialization` namespace within the game's Assembly-CSharp.dll.

### Key Components

1. **DeserializationTemplate**: Describes how to serialize/deserialize .NET classes
2. **SerializationTypeInfo**: Byte-encoded type information with flags
3. **TypeInfo**: Complete type descriptor including generic type parameters

### Serialization Type Codes

The system supports these primitive and complex types:

| Code | Type         | Description |
|------|--------------|-------------|
| 0    | UserDefined  | Custom class types |
| 1    | SByte        | Signed 8-bit integer |
| 2    | Byte         | Unsigned 8-bit integer |
| 3    | Boolean      | True/false value |
| 4    | Int16        | Signed 16-bit integer |
| 5    | UInt16       | Unsigned 16-bit integer |
| 6    | Int32        | Signed 32-bit integer |
| 7    | UInt32       | Unsigned 32-bit integer |
| 8    | Int64        | Signed 64-bit integer |
| 9    | UInt64       | Unsigned 64-bit integer |
| 10   | Single       | 32-bit floating point |
| 11   | Double       | 64-bit floating point |
| 12   | String       | UTF-8 string |
| 13   | Enumeration  | Enum type |
| 14   | Vector2I     | 2D integer vector |
| 15   | Vector2      | 2D float vector |
| 16   | Vector3      | 3D float vector |
| 17   | Array        | One-dimensional array |
| 18   | Pair         | Key-value pair |
| 19   | Dictionary   | Hash table/dictionary |
| 20   | List         | Dynamic list |
| 21   | HashSet      | Unique value set |
| 22   | Queue        | FIFO queue |
| 23   | Colour       | Color/RGBA value |

### Type Flags

Type information uses bit flags:
- **VALUE_MASK (0x3F)**: Masks the type code
- **IS_VALUE_TYPE (0x40)**: Indicates value type vs reference type
- **IS_GENERIC_TYPE (0x80)**: Indicates generic type with parameters

### Generic Types

These types support generic type parameters:
- Pair<TKey, TValue>
- Dictionary<TKey, TValue>
- List<T>
- HashSet<T>
- Queue<T>
- UserDefined (custom generic classes)

## Data Structures

### KleiString Format

ONI uses a custom string encoding called "KleiString":
```
[Int32: Byte Length]
[UTF-8 Bytes: String Content]
```

### HashedString

The game uses SDBM hashing for string identifiers:
- Algorithm: SDBM hash (lowercase input)
- Output: Signed 32-bit integer
- Used for element names, traits, behaviors, etc.

**Hash Function:**
```javascript
function getSDBM32LowerHash(str) {
  str = str.toLowerCase();
  let num = 0;
  for (let i = 0; i < str.length; i++) {
    num = str.charCodeAt(i) + (num << 6) + (num << 16) - num;
  }
  return int32(num); // Cast to signed 32-bit
}
```

### Game Objects

Game objects are organized into groups by type:
- Each group has a name (e.g., "Minion", "ResearchCenter", "OxygenNotIncluded.Edible")
- Contains arrays of game object instances
- Each instance includes:
  - Position (Vector3)
  - Rotation (Quaternion)
  - Scale (Vector3)
  - **Behaviors**: Serialized components/behaviors attached to the object
  - **Extra Data**: Additional serialized data

### Behaviors

Behaviors are the game's component system:
- Each behavior has a template name (C# class name)
- Contains serialized field/property data
- Common behaviors include:
  - `MinionIdentity`: Duplicant information
  - `MinionResume`: Skills and experience
  - `Traits`: Duplicant traits
  - `Health`: Health state
  - `PrimaryElement`: Material composition
  - `Storage`: Stored items
  - `KPrefabID`: Entity identifier

## Save File Versions

The library tracks save file versions to ensure compatibility:

### Version History (Recent)

| Version | Update Name | Notes |
|---------|-------------|-------|
| 7.31    | Latest      | Current version supported |
| 7.25    | Breath of Fresh Air | DLC update |
| 7.23    | -           | DLC version |
| 7.22    | -           | Base game |
| 7.17    | Automation Innovation | Base game update |
| 7.16    | -           | DLC version |
| 7.15    | -           | Radiation Protocol (RP) |
| 7.12    | -           | Version update |
| 7.11    | -           | Launch Update (LU) |

**Version Checking:**
- Major version must match exactly
- Minor version can vary depending on parser strictness settings
- Older versions are generally not supported
- Version is stored both in header and in body after KSAV marker

## Existing Libraries and Tools

### 1. oni-save-parser (JavaScript/TypeScript)

**Repository:** https://github.com/RoboPhred/oni-save-parser

**Language:** TypeScript/JavaScript
**Platform:** Node.js and Web (webpack/rollup)
**License:** MIT
**Status:** Active, version 14.0.1
**Supported Save Version:** 7.31

**Features:**
- Full parse and write support
- Idempotent load/save cycle (bit-for-bit preservation)
- TypeScript type definitions
- Instruction-based "trampoline" parser for pauseable operations
- Progress reporting capability
- Support for both Node.js and browser environments

**API:**
```javascript
const saveGame = parseOniSave(arrayBuffer);
const newBuffer = writeOniSave(saveGame);
```

**Dependencies:**
- `pako`: zlib compression/decompression
- `long`: 64-bit integer support
- `text-encoding`: UTF-8 encoding/decoding
- `jsonschema`: JSON validation

**Design Philosophy:**
- **Idempotent operations**: Load then save produces identical output
- **Ordered data**: Uses arrays of tuples instead of objects to preserve order
- **Generator-based parsing**: Yields instructions for pauseable/testable parsing
- **Round-trip testing**: Validates parser by comparing instruction sequences

### 2. Duplicity (Web-based Save Editor)

**URL:** https://robophred.github.io/oni-duplicity/
**Repository:** https://github.com/RoboPhred/oni-duplicity

**Description:** A web-hosted, locally-running save editor for ONI
**Features:**
- Edit duplicant stats and attributes
- Modify building properties
- Change game settings
- All edits performed locally (no server upload)
- Uses oni-save-parser library

### 3. OniSaveParser (C#/.NET)

**Repository:** https://github.com/SheepReaper/OniSaveParser

**Language:** C#
**Platform:** .NET Standard
**Status:** Work in progress
**Supported Save Version:** 7.11

**Features:**
- Deserialization only (no write support)
- Based on RoboPhred's parser
- Supports multiple .NET platforms

**API:**
```csharp
using (var deserializer = new Deserializer(saveFileLocation)) {
    GameSave gameSave = deserializer.GameSave;
}
```

**Note:** Serialization (writing) is not implemented in this version.

### 4. oni-save-parser (Kotlin/WASM)

**Repository:** https://github.com/StefanOltmann/oni-save-parser
**Status:** No longer maintained

**Description:** A Kotlin port of the original parser with WASM support

## Technical Challenges

### 1. World Data Format

The raw world/map data format is **not fully understood**:
- Contains terrain information
- Stores cell-by-cell world state
- Format is preserved but not parsed by current libraries
- Creating new saves from scratch is not possible

### 2. Simulation Data

The simulation data section contains binary state:
- Physics simulation state
- Thermal simulation state
- Fluid dynamics state
- Not documented and preserved as-is

### 3. Element Ordering

Save file parsing requires maintaining exact element ordering:
- .NET dictionaries and collections are ordered in the save
- Reordering can potentially break saves
- Parser uses ordered arrays instead of objects/Maps
- Critical for ensuring idempotent load/save cycles

### 4. Version Compatibility

ONI frequently updates with new content:
- New behaviors and game objects
- Template changes
- Version lock prevents loading incompatible saves
- Parsers must be updated with each major game update

### 5. Unity Serialization Quirks

Since ONI runs on Unity:
- Cannot use standard .NET BinaryFormatter
- Unity's Vector3 serialization differs from .NET
- Some Unity types require special handling
- KSerialization abstracts these differences

## Reverse Engineering Approach

To understand the save format, developers have used:

1. **Decompilation Tools:**
   - ILSpy
   - dnSpy
   - dotPeek
   - Target: `OxygenNotIncluded_Data/Managed/Assembly-CSharp.dll`

2. **Binary Analysis:**
   - 010 Editor with custom templates
   - Hex editors
   - Byte-by-byte comparison of saves

3. **Test Methodology:**
   - Load official saves
   - Make small in-game changes
   - Compare binary differences
   - Validate round-trip parsing

4. **Community Knowledge:**
   - Klei Entertainment Forums
   - ONI modding community
   - GitHub repositories and examples

## Implementation Notes

### Parser Design

The oni-save-parser library uses a generator-based approach:

```typescript
export function* parseSaveGame(options): ParseIterator<SaveGame> {
  const header: SaveGameHeader = yield* parseHeader();
  const templates: TypeTemplates = yield* parseTemplates();

  let body: SaveGameBody;
  if (header.isCompressed) {
    body = yield readCompressed(parseSaveBody(context));
  } else {
    body = yield* parseSaveBody(context);
  }

  return { header, templates, ...body };
}
```

**Benefits:**
- Pauseable/resumable parsing
- Progress tracking
- Error context preservation
- Testable with mock implementations

### Template-Based Parsing

Instead of hardcoding schemas, the parser:
1. Reads type templates from the save file
2. Uses templates to dynamically parse data
3. Adapts to new game versions automatically (within limits)
4. Validates .NET identifier names

### Data Validation

The parser includes validation:
- .NET identifier name validation (fields, properties, types)
- JSON schema validation for headers
- Version compatibility checking
- Type consistency verification

## Python Implementation Notes

Currently, **no mature Python implementation exists**. Developers interested in creating a Python parser should consider:

### Required Libraries

- **Compression:** `zlib` (standard library)
- **Binary I/O:** `struct` (standard library)
- **64-bit integers:** Native Python int (arbitrary precision)
- **String encoding:** `codecs` or `bytes.decode('utf-8')`

### Recommended Approach

1. **Port the TypeScript parser** as the reference implementation is well-documented
2. **Use generator functions** to match the iterator-based design
3. **Maintain ordering** with lists and OrderedDict
4. **Type hints** for better IDE support and documentation

### Example Structure

```python
from typing import Iterator, Any
import zlib
import struct

class SaveParser:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def read_uint32(self) -> int:
        value = struct.unpack_from('<I', self.data, self.offset)[0]
        self.offset += 4
        return value

    def read_klei_string(self) -> str:
        length = self.read_uint32()
        value = self.data[self.offset:self.offset+length].decode('utf-8')
        self.offset += length
        return value

    def parse_header(self) -> dict:
        build_version = self.read_uint32()
        header_size = self.read_uint32()
        header_version = self.read_uint32()
        # ... continue parsing
```

## Use Cases

### 1. Save Editing

- Modify duplicant attributes
- Change building states
- Adjust resources
- Alter game settings

### 2. Save Analysis

- Extract statistics
- Generate reports
- Analyze colony performance
- Track progression

### 3. Modding Support

- Create mod-compatible saves
- Test mod functionality
- Debug mod interactions
- Validate mod data

### 4. Research and Tools

- Colony planners
- Resource calculators
- Genetic trait analysis
- Save file conversion

## Resources and References

### Official

- **Game:** https://www.klei.com/games/oxygen-not-included
- **Support:** https://support.klei.com/hc/en-us/sections/360006123791-Oxygen-Not-Included
- **Forums:** https://forums.kleientertainment.com/forums/forum/118-oxygen-not-included/

### Community

- **ONI Wiki:** https://oxygennotincluded.wiki.gg/
- **Modding Guide:** https://github.com/Cairath/Oxygen-Not-Included-Modding
- **Forums - Mods & Tools:** https://forums.kleientertainment.com/forums/forum/204-oxygen-not-included-mods-and-tools/

### Libraries and Tools

- **oni-save-parser (JS/TS):** https://github.com/RoboPhred/oni-save-parser
- **Duplicity (Web Editor):** https://github.com/RoboPhred/oni-duplicity
- **OniSaveParser (C#):** https://github.com/SheepReaper/OniSaveParser
- **npm Package:** https://www.npmjs.com/package/oni-save-parser

### Technical Discussions

- **Save File Structure:** https://forums.kleientertainment.com/forums/topic/84638-savefiles-structure/
- **Serialization in ONI:** https://forums.kleientertainment.com/forums/topic/116722-serialization-of-object-state-in-oni/
- **Modding Guide:** https://forums.kleientertainment.com/forums/topic/115346-unofficial-modding-guide/

## Limitations and Unknowns

### Not Yet Understood

1. **Complete world data format** - Terrain and cell data structure
2. **Simulation state format** - Physics/thermal simulation binary format
3. **Some specialized behaviors** - Certain esoteric game objects
4. **Create from scratch** - Cannot generate new worlds programmatically

### Parser Limitations

1. **Version lock** - Must match supported versions
2. **Read-only world data** - World data preserved but not editable
3. **No validation** - Cannot verify save file integrity beyond parsing
4. **Performance** - Large saves can be slow to parse

## Future Directions

Potential areas for development:

1. **Python implementation** - Native Python parser for broader ecosystem integration
2. **World format documentation** - Reverse engineer terrain/cell data
3. **Save generator** - Create saves from scratch
4. **Validation tools** - Detect corrupted or invalid saves
5. **Conversion tools** - Convert between save versions
6. **Analysis frameworks** - Statistical analysis and visualization
7. **Diff tools** - Compare saves to track changes

## Conclusion

The Oxygen Not Included save file format is a sophisticated binary format using Klei's custom KSerialization system. While significant progress has been made in parsing and modifying saves, some aspects remain undocumented. The existing TypeScript/JavaScript library (oni-save-parser) provides a robust, well-tested reference implementation that maintains save file integrity through idempotent operations.

Developers looking to work with ONI saves should start with the oni-save-parser library and its comprehensive TypeScript type definitions. The generator-based parsing approach and template-driven deserialization provide a flexible foundation that adapts to game updates.

## Document Version

- **Created:** 2025-10-29
- **Last Updated:** 2025-10-29
- **ONI Save Version Covered:** 7.31
- **Primary Sources:** oni-save-parser repository, Klei forums, community research
