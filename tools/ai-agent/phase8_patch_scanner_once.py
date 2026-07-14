from __future__ import annotations

from pathlib import Path

path = Path("tools/ai-agent/otbm_item_audit_scan.cpp")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"exact replacement count {count}, expected 1 for: {old[:100]!r}")
    text = text.replace(old, new, 1)


replace_once(
    """struct MechanicPlacement {
    uint16_t itemId = 0;
    int x = -1;
    int y = -1;
    int z = -1;
    int depth = -1;
    std::optional<uint16_t> actionId;
    std::optional<uint16_t> uniqueId;
    std::optional<uint8_t> houseDoorId;
    std::optional<std::array<uint16_t, 3>> teleportDestination;
};
""",
    """struct PhysicalByte {
    size_t offset = 0;
    uint8_t encodedSize = 0;
    uint8_t value = 0;
};

struct MechanicPlacement {
    uint16_t itemId = 0;
    int x = -1;
    int y = -1;
    int z = -1;
    int depth = -1;
    uint32_t tilePlacementIndex = 0;
    std::optional<uint16_t> actionId;
    std::optional<uint16_t> uniqueId;
    std::optional<uint8_t> houseDoorId;
    std::optional<std::array<uint16_t, 3>> teleportDestination;
};

struct PatchAnchor {
    uint16_t itemId = 0;
    int x = -1;
    int y = -1;
    int z = -1;
    int depth = -1;
    uint32_t tilePlacementIndex = 0;
    uint8_t attribute = 0;
    std::vector<uint16_t> value;
    std::vector<PhysicalByte> bytes;
};
""",
)

replace_once(
    """    std::array<uint64_t, 256> unknownAttributeTypes{};
    std::vector<MechanicPlacement> mechanics;
    MapHeaderInfo header;
""",
    """    std::array<uint64_t, 256> unknownAttributeTypes{};
    std::vector<MechanicPlacement> mechanics;
    std::vector<PatchAnchor> patchAnchors;
    MapHeaderInfo header;
""",
)

replace_once(
    """class PropertyReader {
public:
    PropertyReader(const std::vector<uint8_t>& data, size_t position) : data_(data), position_(position) {}

    bool hasMore() const {
        if (position_ >= data_.size()) {
            return false;
        }
        const uint8_t value = data_[position_];
        return value != NODE_START && value != NODE_END;
    }

    uint8_t readByte() {
        requireMore(\"byte\");
        uint8_t value = data_[position_++];
        if (value == NODE_ESCAPE) {
            if (position_ >= data_.size()) {
                throw std::runtime_error(\"Dangling OTBM escape byte\");
            }
            value = data_[position_++];
        } else if (value == NODE_START || value == NODE_END) {
            throw std::runtime_error(\"Unexpected OTBM node marker inside properties\");
        }
        return value;
    }

    uint16_t readU16() {
        const uint16_t low = readByte();
        return static_cast<uint16_t>(low | (static_cast<uint16_t>(readByte()) << 8));
    }

    uint32_t readU32() {
        uint32_t value = 0;
        for (int shift = 0; shift < 32; shift += 8) {
            value |= static_cast<uint32_t>(readByte()) << shift;
        }
        return value;
    }

    void skipBytes(const size_t count) {
        for (size_t index = 0; index < count; ++index) {
            static_cast<void>(readByte());
        }
    }

    void skipString() {
        skipBytes(readU16());
    }

private:
    void requireMore(const char* what) const {
        if (!hasMore()) {
            throw std::runtime_error(std::string(\"Truncated OTBM properties while reading \") + what);
        }
    }

    const std::vector<uint8_t>& data_;
    size_t position_;
};
""",
    """class PropertyReader {
public:
    PropertyReader(const std::vector<uint8_t>& data, size_t position) : data_(data), position_(position) {}

    bool hasMore() const {
        if (position_ >= data_.size()) {
            return false;
        }
        const uint8_t value = data_[position_];
        return value != NODE_START && value != NODE_END;
    }

    PhysicalByte readByteWithSpan() {
        requireMore(\"byte\");
        PhysicalByte decoded;
        decoded.offset = position_;
        uint8_t value = data_[position_++];
        decoded.encodedSize = 1;
        if (value == NODE_ESCAPE) {
            if (position_ >= data_.size()) {
                throw std::runtime_error(\"Dangling OTBM escape byte\");
            }
            value = data_[position_++];
            decoded.encodedSize = 2;
        } else if (value == NODE_START || value == NODE_END) {
            throw std::runtime_error(\"Unexpected OTBM node marker inside properties\");
        }
        decoded.value = value;
        return decoded;
    }

    uint8_t readByte() {
        return readByteWithSpan().value;
    }

    std::vector<PhysicalByte> readBytesWithSpans(const size_t count) {
        std::vector<PhysicalByte> bytes;
        bytes.reserve(count);
        for (size_t index = 0; index < count; ++index) {
            bytes.push_back(readByteWithSpan());
        }
        return bytes;
    }

    uint16_t readU16() {
        const uint16_t low = readByte();
        return static_cast<uint16_t>(low | (static_cast<uint16_t>(readByte()) << 8));
    }

    uint32_t readU32() {
        uint32_t value = 0;
        for (int shift = 0; shift < 32; shift += 8) {
            value |= static_cast<uint32_t>(readByte()) << shift;
        }
        return value;
    }

    void skipBytes(const size_t count) {
        for (size_t index = 0; index < count; ++index) {
            static_cast<void>(readByte());
        }
    }

    void skipString() {
        skipBytes(readU16());
    }

private:
    void requireMore(const char* what) const {
        if (!hasMore()) {
            throw std::runtime_error(std::string(\"Truncated OTBM properties while reading \") + what);
        }
    }

    const std::vector<uint8_t>& data_;
    size_t position_;
};
""",
)

replace_once(
    """void parseItemAttributes(
    PropertyReader& reader,
    ItemStats* stats,
    MechanicPlacement& placement,
    uint64_t* unknownAttributeTails,
    std::array<uint64_t, 256>* unknownAttributeTypes
) {
    while (reader.hasMore()) {
        const uint8_t attribute = reader.readByte();
        if (stats && attribute < stats->attributes.size()) {
            ++stats->attributes[attribute];
        }
        switch (attribute) {
            case ATTR_ACTION_ID:
                placement.actionId = reader.readU16();
                break;
            case ATTR_UNIQUE_ID:
                placement.uniqueId = reader.readU16();
                break;
            case ATTR_TELE_DEST: {
                const uint16_t x = reader.readU16();
                const uint16_t y = reader.readU16();
                const uint16_t z = reader.readByte();
                placement.teleportDestination = std::array<uint16_t, 3>{x, y, z};
                break;
            }
            case ATTR_HOUSEDOOR_ID:
                placement.houseDoorId = reader.readByte();
                break;
            default:
                if (!skipAttributePayload(reader, attribute)) {
                    if (unknownAttributeTails) {
                        ++*unknownAttributeTails;
                    }
                    if (unknownAttributeTypes) {
                        ++(*unknownAttributeTypes)[attribute];
                    }
                    return;
                }
        }
    }
}
""",
    """uint16_t littleEndianU16(const std::vector<PhysicalByte>& bytes, const size_t offset) {
    return static_cast<uint16_t>(bytes[offset].value | (static_cast<uint16_t>(bytes[offset + 1].value) << 8));
}

void appendPatchAnchor(
    const MechanicPlacement& placement,
    const uint8_t attribute,
    std::vector<uint16_t> value,
    std::vector<PhysicalByte> bytes,
    std::vector<PatchAnchor>* anchors
) {
    if (!anchors) {
        return;
    }
    PatchAnchor anchor;
    anchor.itemId = placement.itemId;
    anchor.x = placement.x;
    anchor.y = placement.y;
    anchor.z = placement.z;
    anchor.depth = placement.depth;
    anchor.tilePlacementIndex = placement.tilePlacementIndex;
    anchor.attribute = attribute;
    anchor.value = std::move(value);
    anchor.bytes = std::move(bytes);
    anchors->push_back(std::move(anchor));
}

void parseItemAttributes(
    PropertyReader& reader,
    ItemStats* stats,
    MechanicPlacement& placement,
    uint64_t* unknownAttributeTails,
    std::array<uint64_t, 256>* unknownAttributeTypes,
    std::vector<PatchAnchor>* anchors
) {
    while (reader.hasMore()) {
        const uint8_t attribute = reader.readByte();
        if (stats && attribute < stats->attributes.size()) {
            ++stats->attributes[attribute];
        }
        switch (attribute) {
            case ATTR_ACTION_ID: {
                auto bytes = reader.readBytesWithSpans(2);
                const uint16_t value = littleEndianU16(bytes, 0);
                placement.actionId = value;
                appendPatchAnchor(placement, attribute, {value}, std::move(bytes), anchors);
                break;
            }
            case ATTR_UNIQUE_ID: {
                auto bytes = reader.readBytesWithSpans(2);
                const uint16_t value = littleEndianU16(bytes, 0);
                placement.uniqueId = value;
                appendPatchAnchor(placement, attribute, {value}, std::move(bytes), anchors);
                break;
            }
            case ATTR_TELE_DEST: {
                auto bytes = reader.readBytesWithSpans(5);
                const uint16_t x = littleEndianU16(bytes, 0);
                const uint16_t y = littleEndianU16(bytes, 2);
                const uint16_t z = bytes[4].value;
                placement.teleportDestination = std::array<uint16_t, 3>{x, y, z};
                appendPatchAnchor(placement, attribute, {x, y, z}, std::move(bytes), anchors);
                break;
            }
            case ATTR_HOUSEDOOR_ID: {
                auto bytes = reader.readBytesWithSpans(1);
                const uint8_t value = bytes[0].value;
                placement.houseDoorId = value;
                appendPatchAnchor(placement, attribute, {value}, std::move(bytes), anchors);
                break;
            }
            default:
                if (!skipAttributePayload(reader, attribute)) {
                    if (unknownAttributeTails) {
                        ++*unknownAttributeTails;
                    }
                    if (unknownAttributeTypes) {
                        ++(*unknownAttributeTypes)[attribute];
                    }
                    return;
                }
        }
    }
}
""",
)

replace_once(
    """    std::vector<Context> stack;
    stack.reserve(64);

    size_t position = 4;
""",
    """    std::vector<Context> stack;
    stack.reserve(64);
    std::optional<uint32_t> nextTilePlacementIndex;

    size_t position = 4;
""",
)

replace_once(
    """            context.itemDepth = -1;
            ++result.tileCount;
""",
    """            context.itemDepth = -1;
            nextTilePlacementIndex = 0;
            ++result.tileCount;
""",
)

replace_once(
    """                } else if (attribute == ATTR_ITEM) {
                    const uint16_t itemId = reader.readU16();
                    ItemStats& stats = result.items[itemId];
""",
    """                } else if (attribute == ATTR_ITEM) {
                    const uint16_t itemId = reader.readU16();
                    if (!nextTilePlacementIndex) {
                        throw std::runtime_error(\"Inline item is outside an active tile\");
                    }
                    ++*nextTilePlacementIndex;
                    ItemStats& stats = result.items[itemId];
""",
)

replace_once(
    """            placement.z = parent->tileZ;
            placement.depth = context.itemDepth;
            parseItemAttributes(reader, &stats, placement, &result.unknownAttributeTails, &result.unknownAttributeTypes);
""",
    """            placement.z = parent->tileZ;
            placement.depth = context.itemDepth;
            if (!nextTilePlacementIndex) {
                throw std::runtime_error(\"Item node is outside an active tile\");
            }
            placement.tilePlacementIndex = (*nextTilePlacementIndex)++;
            parseItemAttributes(
                reader,
                &stats,
                placement,
                &result.unknownAttributeTails,
                &result.unknownAttributeTypes,
                &result.patchAnchors
            );
""",
)

replace_once(
    """        if (value == NODE_END) {
            if (stack.empty()) {
                throw std::runtime_error(\"Unexpected OTBM node end\");
            }
            stack.pop_back();
            ++position;
            continue;
        }
""",
    """        if (value == NODE_END) {
            if (stack.empty()) {
                throw std::runtime_error(\"Unexpected OTBM node end\");
            }
            const uint8_t endingType = stack.back().type;
            stack.pop_back();
            if (endingType == OTBM_TILE || endingType == OTBM_HOUSETILE) {
                nextTilePlacementIndex.reset();
            }
            ++position;
            continue;
        }
""",
)

replace_once(
    """            parseItemAttributes(reader, nullptr, parsed, nullptr, nullptr);
""",
    """            parseItemAttributes(reader, nullptr, parsed, nullptr, nullptr, nullptr);
""",
)

marker = """uint64_t checkedAdd(uint64_t left, uint64_t right, const char* label) {
"""
replace_once(
    marker,
    """const char* patchAttributeName(const uint8_t attribute) {
    switch (attribute) {
        case ATTR_ACTION_ID: return \"actionId\";
        case ATTR_UNIQUE_ID: return \"uniqueId\";
        case ATTR_HOUSEDOOR_ID: return \"houseDoorId\";
        case ATTR_TELE_DEST: return \"teleportDestination\";
        default: throw std::runtime_error(\"Unsupported patch-anchor attribute\");
    }
}

void writePatchAnchorReport(
    const std::filesystem::path& mapPath,
    const std::filesystem::path& outputPath,
    const std::vector<uint8_t>& data,
    const ScanData& scan
) {
    std::filesystem::create_directories(outputPath.parent_path().empty() ? std::filesystem::path(\".\") : outputPath.parent_path());
    std::ofstream out(outputPath);
    if (!out) {
        throw std::runtime_error(\"Cannot create patch-anchor report\");
    }
    out << \"{\\n\"
        << \"  \\\"format\\\": \\\"canary-otbm-patch-anchors-native-v1\\\",\\n\"
        << \"  \\\"source\\\": {\\\"path\\\": \\\"\" << jsonEscape(mapPath.filename().string())
        << \"\\\", \\\"size\\\": \" << data.size()
        << \", \\\"otbmVersion\\\": \" << scan.header.version
        << \", \\\"width\\\": \" << scan.header.width
        << \", \\\"height\\\": \" << scan.header.height
        << \", \\\"itemsMajor\\\": \" << scan.header.itemsMajor
        << \", \\\"itemsMinor\\\": \" << scan.header.itemsMinor << \"},\\n\"
        << \"  \\\"anchors\\\": [\\n\";
    for (size_t index = 0; index < scan.patchAnchors.size(); ++index) {
        const PatchAnchor& anchor = scan.patchAnchors[index];
        out << \"    {\\\"position\\\": [\" << anchor.x << \", \" << anchor.y << \", \" << anchor.z << \"]\"
            << \", \\\"tilePlacementIndex\\\": \" << anchor.tilePlacementIndex
            << \", \\\"itemId\\\": \" << anchor.itemId
            << \", \\\"itemDepth\\\": \" << anchor.depth
            << \", \\\"attribute\\\": \\\"\" << patchAttributeName(anchor.attribute) << \"\\\"\"
            << \", \\\"value\\\": \";
        if (anchor.attribute == ATTR_TELE_DEST) {
            out << \"[\" << anchor.value[0] << \", \" << anchor.value[1] << \", \" << anchor.value[2] << \"]\";
        } else {
            out << anchor.value[0];
        }
        out << \", \\\"bytes\\\": [\";
        for (size_t byteIndex = 0; byteIndex < anchor.bytes.size(); ++byteIndex) {
            const PhysicalByte& byte = anchor.bytes[byteIndex];
            if (byteIndex != 0) {
                out << \", \";
            }
            out << \"{\\\"offset\\\": \" << byte.offset
                << \", \\\"encodedSize\\\": \" << static_cast<int>(byte.encodedSize)
                << \", \\\"value\\\": \" << static_cast<int>(byte.value) << \"}\";
        }
        out << \"]}\" << (index + 1 == scan.patchAnchors.size() ? \"\\n\" : \",\\n\");
    }
    out << \"  ]\\n}\\n\";
    if (!out) {
        throw std::runtime_error(\"Cannot finish patch-anchor report\");
    }
}

""" + marker,
)

replace_once(
    """int main(int argc, char** argv) {
    const bool worldIndex = argc == 4 && std::string(argv[1]) == \"--world-index\";
    if ((!worldIndex && argc != 3) || (worldIndex && argc != 4)) {
        std::cerr << \"usage: otbm_item_audit_scan MAP OUTPUT.json\\n\"
                  << \"       otbm_item_audit_scan --world-index MAP OUTPUT.widx\\n\";
        return 2;
    }
    try {
        const std::filesystem::path mapPath = worldIndex ? argv[2] : argv[1];
        const std::filesystem::path outputPath = worldIndex ? argv[3] : argv[2];
        const auto data = readFile(mapPath);
        if (data.size() < 8) {
            throw std::runtime_error(\"OTBM file is too small\");
        }
        const ScanData scan = scanMap(data);
        if (worldIndex) {
            writeWorldIndex(outputPath, data, scan);
        } else {
            writeLegacyReport(mapPath, outputPath, data, scan);
            std::cout << \"tiles=\" << scan.tileCount << \" placements=\" << scan.totalPlacements
                      << \" unique=\" << uniqueItemIds(scan) << \" mechanics=\" << scan.mechanics.size() << \"\\n\";
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << \"error: \" << error.what() << \"\\n\";
        return 1;
    }
}
""",
    """int main(int argc, char** argv) {
    const bool worldIndex = argc == 4 && std::string(argv[1]) == \"--world-index\";
    const bool patchAnchors = argc == 4 && std::string(argv[1]) == \"--patch-anchors\";
    if ((!worldIndex && !patchAnchors && argc != 3) || ((worldIndex || patchAnchors) && argc != 4)) {
        std::cerr << \"usage: otbm_item_audit_scan MAP OUTPUT.json\\n\"
                  << \"       otbm_item_audit_scan --world-index MAP OUTPUT.widx\\n\"
                  << \"       otbm_item_audit_scan --patch-anchors MAP OUTPUT.json\\n\";
        return 2;
    }
    try {
        const bool explicitMode = worldIndex || patchAnchors;
        const std::filesystem::path mapPath = explicitMode ? argv[2] : argv[1];
        const std::filesystem::path outputPath = explicitMode ? argv[3] : argv[2];
        const auto data = readFile(mapPath);
        if (data.size() < 8) {
            throw std::runtime_error(\"OTBM file is too small\");
        }
        const ScanData scan = scanMap(data);
        if (worldIndex) {
            writeWorldIndex(outputPath, data, scan);
        } else if (patchAnchors) {
            writePatchAnchorReport(mapPath, outputPath, data, scan);
            std::cout << \"anchors=\" << scan.patchAnchors.size() << \"\\n\";
        } else {
            writeLegacyReport(mapPath, outputPath, data, scan);
            std::cout << \"tiles=\" << scan.tileCount << \" placements=\" << scan.totalPlacements
                      << \" unique=\" << uniqueItemIds(scan) << \" mechanics=\" << scan.mechanics.size() << \"\\n\";
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << \"error: \" << error.what() << \"\\n\";
        return 1;
    }
}
""",
)

path.write_text(text, encoding="utf-8")
for bootstrap in (
    Path(".github/workflows/phase8-scanner-bootstrap.yml"),
    Path(".github/workflows/phase8-bootstrap-run.yml"),
    Path("tools/ai-agent/phase8_patch_scanner_once.py"),
):
    bootstrap.unlink(missing_ok=True)
