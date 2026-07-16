#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr uint8_t NODE_ESCAPE = 0xFD;
constexpr uint8_t NODE_START = 0xFE;
constexpr uint8_t NODE_END = 0xFF;
constexpr uint8_t OTBM_MAP_DATA = 2;
constexpr uint8_t OTBM_TILE_AREA = 4;
constexpr uint8_t OTBM_TILE = 5;
constexpr uint8_t OTBM_ITEM = 6;
constexpr uint8_t OTBM_HOUSETILE = 14;

constexpr uint8_t ATTR_TILE_FLAGS = 3;
constexpr uint8_t ATTR_ACTION_ID = 4;
constexpr uint8_t ATTR_UNIQUE_ID = 5;
constexpr uint8_t ATTR_TEXT = 6;
constexpr uint8_t ATTR_DESC = 7;
constexpr uint8_t ATTR_TELE_DEST = 8;
constexpr uint8_t ATTR_ITEM = 9;
constexpr uint8_t ATTR_DEPOT_ID = 10;
constexpr uint8_t ATTR_RUNE_CHARGES = 12;
constexpr uint8_t ATTR_HOUSEDOOR_ID = 14;
constexpr uint8_t ATTR_COUNT = 15;
constexpr uint8_t ATTR_DURATION = 16;
constexpr uint8_t ATTR_DECAYING_STATE = 17;
constexpr uint8_t ATTR_WRITTEN_DATE = 18;
constexpr uint8_t ATTR_WRITTEN_BY = 19;
constexpr uint8_t ATTR_SLEEPER_GUID = 20;
constexpr uint8_t ATTR_SLEEP_START = 21;
constexpr uint8_t ATTR_CHARGES = 22;
constexpr size_t ATTRIBUTE_LIMIT = 32;

constexpr std::array<char, 8> WORLD_INDEX_MAGIC{'O', 'T', 'S', 'W', 'I', 'D', 'X', '1'};
constexpr uint32_t WORLD_INDEX_VERSION = 1;
constexpr uint32_t WORLD_INDEX_HEADER_SIZE = 256;
constexpr uint32_t ITEM_DIRECTORY_COUNT = 65536;
constexpr uint32_t AREA_KEY_COUNT = 1U << 20U;
constexpr uint32_t MECHANIC_ACTION = 1U << 0U;
constexpr uint32_t MECHANIC_UNIQUE = 1U << 1U;
constexpr uint32_t MECHANIC_HOUSE_DOOR = 1U << 2U;
constexpr uint32_t MECHANIC_TELEPORT = 1U << 3U;
constexpr uint32_t NO_MECHANIC = std::numeric_limits<uint32_t>::max();

struct Context {
    uint8_t type = 0;
    int areaX = -1;
    int areaY = -1;
    int areaZ = -1;
    int tileX = -1;
    int tileY = -1;
    int tileZ = -1;
    int itemDepth = -1;
};

struct ItemStats {
    uint64_t placements = 0;
    uint64_t inlinePlacements = 0;
    uint64_t nodePlacements = 0;
    std::array<uint64_t, ATTRIBUTE_LIMIT> attributes{};
};

struct PhysicalByte {
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

struct MapHeaderInfo {
    uint32_t version = 0;
    uint16_t width = 0;
    uint16_t height = 0;
    uint32_t itemsMajor = 0;
    uint32_t itemsMinor = 0;
};

struct ScanData {
    explicit ScanData() : items(ITEM_DIRECTORY_COUNT), areaTileCounts(AREA_KEY_COUNT) {}

    std::vector<ItemStats> items;
    std::vector<uint32_t> areaTileCounts;
    std::array<uint64_t, 256> unknownAttributeTypes{};
    std::vector<MechanicPlacement> mechanics;
    std::vector<PatchAnchor> patchAnchors;
    MapHeaderInfo header;
    uint64_t rawAreaCount = 0;
    uint64_t tileCount = 0;
    uint64_t totalPlacements = 0;
    uint64_t inlinePlacements = 0;
    uint64_t nodePlacements = 0;
    uint64_t unknownAttributeTails = 0;
    int maxItemDepth = -1;
};

struct PlacementBuffer {
    uint16_t itemId = 0;
    int depth = -1;
    bool node = false;
    std::optional<uint16_t> actionId;
    std::optional<uint16_t> uniqueId;
    std::optional<uint8_t> houseDoorId;
    std::optional<std::array<uint16_t, 3>> teleportDestination;
};

struct TileBuffer {
    uint16_t x = 0;
    uint16_t y = 0;
    uint8_t z = 0;
    uint8_t kind = 0;
    uint32_t houseId = 0;
    uint32_t flags = 0;
    std::vector<PlacementBuffer> placements;
};

struct AreaBuffer {
    uint16_t baseX = 0;
    uint16_t baseY = 0;
    uint8_t z = 0;
    std::vector<TileBuffer> tiles;
};

#pragma pack(push, 1)
struct ItemDirectoryEntry {
    uint64_t postingsStart = 0;
    uint64_t count = 0;
};

struct AreaRecordBinary {
    uint16_t baseX = 0;
    uint16_t baseY = 0;
    uint8_t z = 0;
    uint8_t reserved = 0;
    uint16_t reserved2 = 0;
    uint32_t postingsStart = 0;
    uint32_t tileCount = 0;
};

struct TileRecordBinary {
    uint16_t x = 0;
    uint16_t y = 0;
    uint8_t z = 0;
    uint8_t kind = 0;
    uint32_t houseId = 0;
    uint32_t flags = 0;
    uint32_t placementStart = 0;
    uint32_t placementCount = 0;
};

struct PlacementRecordBinary {
    uint16_t itemId = 0;
    uint16_t meta = 0;
    uint32_t mechanicIndex = NO_MECHANIC;
    uint32_t tileIndex = 0;
};

struct MechanicRecordBinary {
    uint16_t flags = 0;
    uint16_t actionId = 0;
    uint16_t uniqueId = 0;
    uint16_t houseDoorId = 0;
    uint16_t teleX = 0;
    uint16_t teleY = 0;
    uint16_t teleZ = 0;
    uint32_t placementOrdinal = 0;
};
#pragma pack(pop)

static_assert(sizeof(ItemDirectoryEntry) == 16);
static_assert(sizeof(AreaRecordBinary) == 16);
static_assert(sizeof(TileRecordBinary) == 22);
static_assert(sizeof(PlacementRecordBinary) == 12);
static_assert(sizeof(MechanicRecordBinary) == 18);

class PropertyReader {
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
        requireMore("byte");
        PhysicalByte decoded;
        decoded.offset = position_;
        uint8_t value = data_[position_++];
        decoded.encodedSize = 1;
        if (value == NODE_ESCAPE) {
            if (position_ >= data_.size()) {
                throw std::runtime_error("Dangling OTBM escape byte");
            }
            value = data_[position_++];
            decoded.encodedSize = 2;
        } else if (value == NODE_START || value == NODE_END) {
            throw std::runtime_error("Unexpected OTBM node marker inside properties");
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
            throw std::runtime_error(std::string("Truncated OTBM properties while reading ") + what);
        }
    }

    const std::vector<uint8_t>& data_;
    size_t position_;
};

std::vector<uint8_t> readFile(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("Cannot open input map: " + path.string());
    }
    input.seekg(0, std::ios::end);
    const auto size = input.tellg();
    if (size < 0) {
        throw std::runtime_error("Cannot determine map size");
    }
    input.seekg(0, std::ios::beg);
    std::vector<uint8_t> data(static_cast<size_t>(size));
    input.read(reinterpret_cast<char*>(data.data()), size);
    if (!input) {
        throw std::runtime_error("Cannot read input map");
    }
    return data;
}

bool skipAttributePayload(PropertyReader& reader, const uint8_t attribute) {
    switch (attribute) {
        case ATTR_ACTION_ID:
        case ATTR_UNIQUE_ID:
        case ATTR_DEPOT_ID:
        case ATTR_CHARGES:
            reader.skipBytes(2);
            return true;
        case ATTR_TELE_DEST:
            reader.skipBytes(5);
            return true;
        case ATTR_RUNE_CHARGES:
        case ATTR_HOUSEDOOR_ID:
        case ATTR_COUNT:
        case ATTR_DECAYING_STATE:
            reader.skipBytes(1);
            return true;
        case ATTR_DURATION:
        case ATTR_WRITTEN_DATE:
        case ATTR_SLEEPER_GUID:
        case ATTR_SLEEP_START:
            reader.skipBytes(4);
            return true;
        case ATTR_TEXT:
        case ATTR_DESC:
        case ATTR_WRITTEN_BY:
            reader.skipString();
            return true;
        default:
            return false;
    }
}

std::string jsonEscape(const std::string& value) {
    std::ostringstream stream;
    for (const unsigned char character : value) {
        switch (character) {
            case '\\': stream << "\\\\"; break;
            case '"': stream << "\\\""; break;
            case '\b': stream << "\\b"; break;
            case '\f': stream << "\\f"; break;
            case '\n': stream << "\\n"; break;
            case '\r': stream << "\\r"; break;
            case '\t': stream << "\\t"; break;
            default:
                if (character < 0x20) {
                    stream << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                           << static_cast<int>(character) << std::dec << std::setfill(' ');
                } else {
                    stream << static_cast<char>(character);
                }
        }
    }
    return stream.str();
}

uint16_t littleEndianU16(const std::vector<PhysicalByte>& bytes, const size_t offset) {
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

bool hasMechanic(const MechanicPlacement& placement) {
    return placement.actionId.has_value() || placement.uniqueId.has_value()
        || placement.teleportDestination.has_value() || placement.houseDoorId.has_value();
}

MapHeaderInfo parseMapHeader(const std::vector<uint8_t>& data) {
    if (data.size() < 8 || data[4] != NODE_START) {
        throw std::runtime_error("Missing OTBM root node");
    }
    PropertyReader reader(data, 6);
    MapHeaderInfo header;
    header.version = reader.readU32();
    header.width = reader.readU16();
    header.height = reader.readU16();
    header.itemsMajor = reader.readU32();
    header.itemsMinor = reader.readU32();
    return header;
}

uint32_t areaKey(const int baseX, const int baseY, const int z) {
    if (baseX < 0 || baseX > 0xFFFF || baseY < 0 || baseY > 0xFFFF || z < 0 || z > 15) {
        throw std::runtime_error("Tile-area coordinates are outside the OTBM range");
    }
    return (static_cast<uint32_t>(z) << 16U)
        | (static_cast<uint32_t>(baseY >> 8) << 8U)
        | static_cast<uint32_t>(baseX >> 8);
}

size_t uniqueAreaCount(const ScanData& scan) {
    return static_cast<size_t>(std::count_if(scan.areaTileCounts.begin(), scan.areaTileCounts.end(), [](const uint32_t count) {
        return count > 0;
    }));
}

ScanData scanMap(const std::vector<uint8_t>& data) {
    ScanData result;
    result.header = parseMapHeader(data);
    result.mechanics.reserve(4096);
    std::vector<Context> stack;
    stack.reserve(64);
    std::optional<uint32_t> nextTilePlacementIndex;

    size_t position = 4;
    while (position < data.size()) {
        const uint8_t value = data[position];
        if (value == NODE_ESCAPE) {
            if (position + 1 >= data.size()) {
                throw std::runtime_error("Dangling OTBM escape byte");
            }
            position += 2;
            continue;
        }
        if (value == NODE_START) {
            if (position + 1 >= data.size()) {
                throw std::runtime_error("OTBM node has no type");
            }
            const uint8_t nodeType = data[position + 1];
            const Context* parent = stack.empty() ? nullptr : &stack.back();
            Context context;
            context.type = nodeType;
            if (parent) {
                context.areaX = parent->areaX;
                context.areaY = parent->areaY;
                context.areaZ = parent->areaZ;
                context.tileX = parent->tileX;
                context.tileY = parent->tileY;
                context.tileZ = parent->tileZ;
                context.itemDepth = parent->itemDepth;
            }

            if (nodeType == OTBM_TILE_AREA && parent && parent->type == OTBM_MAP_DATA) {
                PropertyReader reader(data, position + 2);
                context.areaX = reader.readU16();
                context.areaY = reader.readU16();
                context.areaZ = reader.readByte();
                ++result.rawAreaCount;
            } else if ((nodeType == OTBM_TILE || nodeType == OTBM_HOUSETILE) && parent && parent->type == OTBM_TILE_AREA) {
                PropertyReader reader(data, position + 2);
                context.tileX = parent->areaX + reader.readByte();
                context.tileY = parent->areaY + reader.readByte();
                context.tileZ = parent->areaZ;
                context.itemDepth = -1;
                nextTilePlacementIndex = 0;
                ++result.tileCount;
                const uint32_t key = areaKey(parent->areaX, parent->areaY, parent->areaZ);
                if (result.areaTileCounts[key] == std::numeric_limits<uint32_t>::max()) {
                    throw std::runtime_error("Tile-area count exceeds the world-index v1 limit");
                }
                ++result.areaTileCounts[key];
                if (nodeType == OTBM_HOUSETILE) {
                    static_cast<void>(reader.readU32());
                }
                while (reader.hasMore()) {
                    const uint8_t attribute = reader.readByte();
                    if (attribute == ATTR_TILE_FLAGS) {
                        static_cast<void>(reader.readU32());
                    } else if (attribute == ATTR_ITEM) {
                        const uint16_t itemId = reader.readU16();
                        if (!nextTilePlacementIndex) {
                            throw std::runtime_error("Inline item is outside an active tile");
                        }
                        ++*nextTilePlacementIndex;
                        ItemStats& stats = result.items[itemId];
                        ++stats.placements;
                        ++stats.inlinePlacements;
                        ++result.inlinePlacements;
                        ++result.totalPlacements;
                    } else {
                        throw std::runtime_error("Unsupported tile attribute " + std::to_string(attribute));
                    }
                }
            } else if (nodeType == OTBM_ITEM) {
                if (!parent || parent->tileX < 0 || parent->tileY < 0 || parent->tileZ < 0) {
                    throw std::runtime_error("Item node is outside a tile");
                }
                PropertyReader reader(data, position + 2);
                const uint16_t itemId = reader.readU16();
                context.itemDepth = parent->type == OTBM_ITEM ? parent->itemDepth + 1 : 0;
                result.maxItemDepth = std::max(result.maxItemDepth, context.itemDepth);
                ItemStats& stats = result.items[itemId];
                ++stats.placements;
                ++stats.nodePlacements;
                ++result.nodePlacements;
                ++result.totalPlacements;
                MechanicPlacement placement;
                placement.itemId = itemId;
                placement.x = parent->tileX;
                placement.y = parent->tileY;
                placement.z = parent->tileZ;
                placement.depth = context.itemDepth;
                if (!nextTilePlacementIndex) {
                    throw std::runtime_error("Item node is outside an active tile");
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
                if (hasMechanic(placement)) {
                    result.mechanics.push_back(placement);
                }
            }
            stack.push_back(context);
            position += 2;
            continue;
        }
        if (value == NODE_END) {
            if (stack.empty()) {
                throw std::runtime_error("Unexpected OTBM node end");
            }
            const uint8_t endingType = stack.back().type;
            stack.pop_back();
            if (endingType == OTBM_TILE || endingType == OTBM_HOUSETILE) {
                nextTilePlacementIndex.reset();
            }
            ++position;
            continue;
        }
        ++position;
    }
    if (!stack.empty()) {
        throw std::runtime_error("OTBM contains unterminated nodes");
    }
    return result;
}

size_t uniqueItemIds(const ScanData& scan) {
    return static_cast<size_t>(std::count_if(scan.items.begin(), scan.items.end(), [](const ItemStats& item) {
        return item.placements > 0;
    }));
}

void writeLegacyReport(
    const std::filesystem::path& mapPath,
    const std::filesystem::path& outputPath,
    const std::vector<uint8_t>& data,
    const ScanData& scan
) {
    std::filesystem::create_directories(outputPath.parent_path().empty() ? std::filesystem::path(".") : outputPath.parent_path());
    std::ofstream out(outputPath);
    if (!out) {
        throw std::runtime_error("Cannot create output report");
    }
    out << "{\n"
        << "  \"format\": \"canary-otbm-item-scan-v1\",\n"
        << "  \"source\": {\"path\": \"" << jsonEscape(mapPath.filename().string()) << "\", \"size\": " << data.size() << "},\n"
        << "  \"tileCount\": " << scan.tileCount << ",\n"
        << "  \"totalPlacements\": " << scan.totalPlacements << ",\n"
        << "  \"inlinePlacements\": " << scan.inlinePlacements << ",\n"
        << "  \"itemNodePlacements\": " << scan.nodePlacements << ",\n"
        << "  \"uniqueItemIds\": " << uniqueItemIds(scan) << ",\n"
        << "  \"unknownAttributeTails\": " << scan.unknownAttributeTails << ",\n"
        << "  \"unknownAttributeTypes\": {";
    bool firstUnknown = true;
    for (size_t type = 0; type < scan.unknownAttributeTypes.size(); ++type) {
        if (scan.unknownAttributeTypes[type] == 0) {
            continue;
        }
        if (!firstUnknown) {
            out << ", ";
        }
        firstUnknown = false;
        out << "\"" << type << "\": " << scan.unknownAttributeTypes[type];
    }
    out << "},\n  \"items\": [\n";
    bool firstItem = true;
    for (size_t itemId = 0; itemId < scan.items.size(); ++itemId) {
        const ItemStats& stats = scan.items[itemId];
        if (stats.placements == 0) {
            continue;
        }
        if (!firstItem) {
            out << ",\n";
        }
        firstItem = false;
        out << "    {\"id\": " << itemId
            << ", \"placements\": " << stats.placements
            << ", \"inlinePlacements\": " << stats.inlinePlacements
            << ", \"itemNodePlacements\": " << stats.nodePlacements
            << ", \"attributes\": {";
        bool firstAttribute = true;
        for (size_t attribute = 0; attribute < stats.attributes.size(); ++attribute) {
            if (stats.attributes[attribute] == 0) {
                continue;
            }
            if (!firstAttribute) {
                out << ", ";
            }
            firstAttribute = false;
            out << "\"" << attribute << "\": " << stats.attributes[attribute];
        }
        out << "}}";
    }
    out << "\n  ],\n  \"mechanicPlacements\": [\n";
    for (size_t index = 0; index < scan.mechanics.size(); ++index) {
        const auto& placement = scan.mechanics[index];
        out << "    {\"itemId\": " << placement.itemId
            << ", \"position\": [" << placement.x << ", " << placement.y << ", " << placement.z << "]"
            << ", \"itemDepth\": " << placement.depth;
        if (placement.actionId) {
            out << ", \"actionId\": " << *placement.actionId;
        }
        if (placement.uniqueId) {
            out << ", \"uniqueId\": " << *placement.uniqueId;
        }
        if (placement.houseDoorId) {
            out << ", \"houseDoorId\": " << static_cast<int>(*placement.houseDoorId);
        }
        if (placement.teleportDestination) {
            out << ", \"teleportDestination\": ["
                << (*placement.teleportDestination)[0] << ", "
                << (*placement.teleportDestination)[1] << ", "
                << (*placement.teleportDestination)[2] << "]";
        }
        out << "}" << (index + 1 == scan.mechanics.size() ? "\n" : ",\n");
    }
    out << "  ]\n}\n";
    if (!out) {
        throw std::runtime_error("Cannot finish output report");
    }
}

const char* patchAttributeName(const uint8_t attribute) {
    switch (attribute) {
        case ATTR_ACTION_ID: return "actionId";
        case ATTR_UNIQUE_ID: return "uniqueId";
        case ATTR_HOUSEDOOR_ID: return "houseDoorId";
        case ATTR_TELE_DEST: return "teleportDestination";
        default: throw std::runtime_error("Unsupported patch-anchor attribute");
    }
}

void writePatchAnchorReport(
    const std::filesystem::path& mapPath,
    const std::filesystem::path& outputPath,
    const std::vector<uint8_t>& data,
    const ScanData& scan
) {
    std::filesystem::create_directories(outputPath.parent_path().empty() ? std::filesystem::path(".") : outputPath.parent_path());
    std::ofstream out(outputPath);
    if (!out) {
        throw std::runtime_error("Cannot create patch-anchor report");
    }
    out << "{\n"
        << "  \"format\": \"canary-otbm-patch-anchors-native-v1\",\n"
        << "  \"source\": {\"path\": \"" << jsonEscape(mapPath.filename().string())
        << "\", \"size\": " << data.size()
        << ", \"otbmVersion\": " << scan.header.version
        << ", \"width\": " << scan.header.width
        << ", \"height\": " << scan.header.height
        << ", \"itemsMajor\": " << scan.header.itemsMajor
        << ", \"itemsMinor\": " << scan.header.itemsMinor << "},\n"
        << "  \"anchors\": [\n";
    for (size_t index = 0; index < scan.patchAnchors.size(); ++index) {
        const PatchAnchor& anchor = scan.patchAnchors[index];
        out << "    {\"position\": [" << anchor.x << ", " << anchor.y << ", " << anchor.z << "]"
            << ", \"tilePlacementIndex\": " << anchor.tilePlacementIndex
            << ", \"itemId\": " << anchor.itemId
            << ", \"itemDepth\": " << anchor.depth
            << ", \"attribute\": \"" << patchAttributeName(anchor.attribute) << "\""
            << ", \"value\": ";
        if (anchor.attribute == ATTR_TELE_DEST) {
            out << "[" << anchor.value[0] << ", " << anchor.value[1] << ", " << anchor.value[2] << "]";
        } else {
            out << anchor.value[0];
        }
        out << ", \"bytes\": [";
        for (size_t byteIndex = 0; byteIndex < anchor.bytes.size(); ++byteIndex) {
            const PhysicalByte& byte = anchor.bytes[byteIndex];
            if (byteIndex != 0) {
                out << ", ";
            }
            out << "{\"offset\": " << byte.offset
                << ", \"encodedSize\": " << static_cast<int>(byte.encodedSize)
                << ", \"value\": " << static_cast<int>(byte.value) << "}";
        }
        out << "]}" << (index + 1 == scan.patchAnchors.size() ? "\n" : ",\n");
    }
    out << "  ]\n}\n";
    if (!out) {
        throw std::runtime_error("Cannot finish patch-anchor report");
    }
}

uint64_t checkedAdd(uint64_t left, uint64_t right, const char* label) {
    if (right > std::numeric_limits<uint64_t>::max() - left) {
        throw std::runtime_error(std::string("World-index size overflow in ") + label);
    }
    return left + right;
}

uint64_t checkedMultiply(uint64_t left, uint64_t right, const char* label) {
    if (left != 0 && right > std::numeric_limits<uint64_t>::max() / left) {
        throw std::runtime_error(std::string("World-index size overflow in ") + label);
    }
    return left * right;
}

template <typename T>
void writeVectorAt(std::fstream& file, uint64_t offset, const std::vector<T>& values) {
    if (values.empty()) {
        return;
    }
    file.seekp(static_cast<std::streamoff>(offset));
    file.write(reinterpret_cast<const char*>(values.data()), static_cast<std::streamsize>(values.size() * sizeof(T)));
    if (!file) {
        throw std::runtime_error("Cannot write world-index section");
    }
}

template <typename T, size_t N>
void putLittleEndian(std::array<uint8_t, N>& buffer, size_t offset, T value) {
    for (size_t index = 0; index < sizeof(T); ++index) {
        buffer[offset + index] = static_cast<uint8_t>((static_cast<uint64_t>(value) >> (index * 8U)) & 0xFFU);
    }
}

uint16_t placementMeta(const PlacementBuffer& placement) {
    if (!placement.node) {
        return 0;
    }
    if (placement.depth < 0 || placement.depth > 0x7FFF) {
        throw std::runtime_error("Item nesting depth does not fit the world-index format");
    }
    return static_cast<uint16_t>(0x8000U | static_cast<uint16_t>(placement.depth));
}

MechanicRecordBinary mechanicRecord(const PlacementBuffer& placement, uint32_t placementOrdinal) {
    MechanicRecordBinary record;
    record.placementOrdinal = placementOrdinal;
    if (placement.actionId) {
        record.flags |= MECHANIC_ACTION;
        record.actionId = *placement.actionId;
    }
    if (placement.uniqueId) {
        record.flags |= MECHANIC_UNIQUE;
        record.uniqueId = *placement.uniqueId;
    }
    if (placement.houseDoorId) {
        record.flags |= MECHANIC_HOUSE_DOOR;
        record.houseDoorId = *placement.houseDoorId;
    }
    if (placement.teleportDestination) {
        record.flags |= MECHANIC_TELEPORT;
        record.teleX = (*placement.teleportDestination)[0];
        record.teleY = (*placement.teleportDestination)[1];
        record.teleZ = (*placement.teleportDestination)[2];
    }
    return record;
}

bool placementHasMechanic(const PlacementBuffer& placement) {
    return placement.actionId || placement.uniqueId || placement.houseDoorId || placement.teleportDestination;
}

struct WorldLayout {
    uint64_t itemDirectoryOffset = WORLD_INDEX_HEADER_SIZE;
    uint64_t areaDirectoryOffset = 0;
    uint64_t areaPostingsOffset = 0;
    uint64_t tileOffset = 0;
    uint64_t placementOffset = 0;
    uint64_t mechanicOffset = 0;
    uint64_t itemPostingsOffset = 0;
    uint64_t fileSize = 0;
};

WorldLayout worldLayout(const ScanData& scan) {
    const uint64_t uniqueAreas = uniqueAreaCount(scan);
    WorldLayout layout;
    layout.areaDirectoryOffset = checkedAdd(
        layout.itemDirectoryOffset,
        checkedMultiply(ITEM_DIRECTORY_COUNT, sizeof(ItemDirectoryEntry), "item directory"),
        "area directory offset"
    );
    layout.areaPostingsOffset = checkedAdd(
        layout.areaDirectoryOffset,
        checkedMultiply(uniqueAreas, sizeof(AreaRecordBinary), "area directory"),
        "area postings offset"
    );
    layout.tileOffset = checkedAdd(
        layout.areaPostingsOffset,
        checkedMultiply(scan.tileCount, sizeof(uint32_t), "area postings"),
        "tile offset"
    );
    layout.placementOffset = checkedAdd(
        layout.tileOffset,
        checkedMultiply(scan.tileCount, sizeof(TileRecordBinary), "tile records"),
        "placement offset"
    );
    layout.mechanicOffset = checkedAdd(
        layout.placementOffset,
        checkedMultiply(scan.totalPlacements, sizeof(PlacementRecordBinary), "placement records"),
        "mechanic offset"
    );
    layout.itemPostingsOffset = checkedAdd(
        layout.mechanicOffset,
        checkedMultiply(scan.mechanics.size(), sizeof(MechanicRecordBinary), "mechanic records"),
        "item postings offset"
    );
    layout.fileSize = checkedAdd(
        layout.itemPostingsOffset,
        checkedMultiply(scan.totalPlacements, sizeof(uint32_t), "item postings"),
        "file size"
    );
    return layout;
}

void writeWorldIndex(
    const std::filesystem::path& outputPath,
    const std::vector<uint8_t>& data,
    const ScanData& scan
) {
    if (std::endian::native != std::endian::little) {
        throw std::runtime_error("World-index writer currently requires a little-endian host");
    }
    if (scan.tileCount > std::numeric_limits<uint32_t>::max()
        || scan.totalPlacements > std::numeric_limits<uint32_t>::max()
        || scan.mechanics.size() > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("Map exceeds the world-index v1 32-bit record limits");
    }
    if (scan.maxItemDepth > 0x7FFF) {
        throw std::runtime_error("Map item nesting exceeds the world-index v1 depth limit");
    }
    if (outputPath.empty()) {
        throw std::runtime_error("World-index output path is empty");
    }
    if (std::filesystem::is_symlink(outputPath)) {
        throw std::runtime_error("World-index output must not be a symlink");
    }
    if (std::filesystem::exists(outputPath)) {
        throw std::runtime_error("World-index output already exists");
    }
    std::filesystem::create_directories(outputPath.parent_path().empty() ? std::filesystem::path(".") : outputPath.parent_path());
    const auto temporaryPath = outputPath.parent_path() / (outputPath.filename().string() + ".tmp");
    if (std::filesystem::is_symlink(temporaryPath)) {
        throw std::runtime_error("World-index temporary output must not be a symlink");
    }
    std::filesystem::remove(temporaryPath);

    const WorldLayout layout = worldLayout(scan);
    std::fstream file(temporaryPath, std::ios::binary | std::ios::in | std::ios::out | std::ios::trunc);
    if (!file) {
        throw std::runtime_error("Cannot create world-index output");
    }
    if (layout.fileSize == 0 || layout.fileSize > static_cast<uint64_t>(std::numeric_limits<std::streamoff>::max())) {
        throw std::runtime_error("World-index output size is unsupported");
    }
    file.seekp(static_cast<std::streamoff>(layout.fileSize - 1));
    file.put('\0');
    file.flush();
    if (!file) {
        throw std::runtime_error("Cannot preallocate world-index output");
    }

    std::vector<ItemDirectoryEntry> itemDirectory(ITEM_DIRECTORY_COUNT);
    uint64_t postingCursor = 0;
    for (size_t itemId = 0; itemId < scan.items.size(); ++itemId) {
        itemDirectory[itemId].postingsStart = postingCursor;
        itemDirectory[itemId].count = scan.items[itemId].placements;
        postingCursor += scan.items[itemId].placements;
    }
    if (postingCursor != scan.totalPlacements) {
        throw std::runtime_error("Item placement totals do not match the scan summary");
    }
    std::vector<uint64_t> itemWriteCursor(ITEM_DIRECTORY_COUNT);
    for (size_t itemId = 0; itemId < itemDirectory.size(); ++itemId) {
        itemWriteCursor[itemId] = itemDirectory[itemId].postingsStart;
    }
    std::vector<uint32_t> itemPostings(static_cast<size_t>(scan.totalPlacements));
    std::vector<AreaRecordBinary> areaDirectory;
    areaDirectory.reserve(uniqueAreaCount(scan));
    std::vector<uint64_t> areaWriteCursor(AREA_KEY_COUNT);
    uint64_t areaPostingCursor = 0;
    for (uint32_t key = 0; key < AREA_KEY_COUNT; ++key) {
        const uint32_t count = scan.areaTileCounts[key];
        if (count == 0) {
            continue;
        }
        AreaRecordBinary areaRecord;
        areaRecord.baseX = static_cast<uint16_t>((key & 0xFFU) << 8U);
        areaRecord.baseY = static_cast<uint16_t>(((key >> 8U) & 0xFFU) << 8U);
        areaRecord.z = static_cast<uint8_t>((key >> 16U) & 0x0FU);
        areaRecord.postingsStart = static_cast<uint32_t>(areaPostingCursor);
        areaRecord.tileCount = count;
        areaDirectory.push_back(areaRecord);
        areaWriteCursor[key] = areaPostingCursor;
        areaPostingCursor += count;
    }
    if (areaPostingCursor != scan.tileCount) {
        throw std::runtime_error("Tile-area postings do not match the scan summary");
    }
    std::vector<uint32_t> areaPostings(static_cast<size_t>(scan.tileCount));
    std::vector<uint16_t> tilePositionKeys(static_cast<size_t>(scan.tileCount));

    uint32_t tileWritten = 0;
    uint32_t placementWritten = 0;
    uint32_t mechanicWritten = 0;
    std::optional<AreaBuffer> currentArea;
    std::optional<TileBuffer> currentTile;
    std::vector<Context> stack;
    stack.reserve(64);

    auto flushArea = [&]() {
        if (!currentArea) {
            throw std::runtime_error("Internal world-index area state is missing");
        }
        std::sort(currentArea->tiles.begin(), currentArea->tiles.end(), [](const TileBuffer& left, const TileBuffer& right) {
            if (left.y != right.y) {
                return left.y < right.y;
            }
            return left.x < right.x;
        });
        for (size_t index = 1; index < currentArea->tiles.size(); ++index) {
            const auto& previous = currentArea->tiles[index - 1];
            const auto& current = currentArea->tiles[index];
            if (previous.x == current.x && previous.y == current.y && previous.z == current.z) {
                throw std::runtime_error("Duplicate tile position in one tile-area node");
            }
        }
        std::vector<TileRecordBinary> tileRecords;
        std::vector<PlacementRecordBinary> placementRecords;
        std::vector<MechanicRecordBinary> mechanicRecords;
        tileRecords.reserve(currentArea->tiles.size());
        size_t areaPlacements = 0;
        for (const auto& tile : currentArea->tiles) {
            areaPlacements += tile.placements.size();
        }
        placementRecords.reserve(areaPlacements);
        mechanicRecords.reserve(std::min(areaPlacements, static_cast<size_t>(scan.mechanics.size())));

        const uint32_t key = areaKey(currentArea->baseX, currentArea->baseY, currentArea->z);
        for (const auto& tile : currentArea->tiles) {
            const uint32_t tileIndex = tileWritten + static_cast<uint32_t>(tileRecords.size());
            const uint64_t areaPostingIndex = areaWriteCursor[key]++;
            if (areaPostingIndex >= areaPostings.size()) {
                throw std::runtime_error("Tile-area postings overflow while writing world index");
            }
            areaPostings[static_cast<size_t>(areaPostingIndex)] = tileIndex;
            tilePositionKeys[tileIndex] = static_cast<uint16_t>(
                (static_cast<uint16_t>(tile.y & 0xFFU) << 8U) | static_cast<uint16_t>(tile.x & 0xFFU)
            );

            TileRecordBinary tileRecord;
            tileRecord.x = tile.x;
            tileRecord.y = tile.y;
            tileRecord.z = tile.z;
            tileRecord.kind = tile.kind;
            tileRecord.houseId = tile.houseId;
            tileRecord.flags = tile.flags;
            tileRecord.placementStart = placementWritten + static_cast<uint32_t>(placementRecords.size());
            tileRecord.placementCount = static_cast<uint32_t>(tile.placements.size());

            for (const auto& placement : tile.placements) {
                const uint32_t placementOrdinal = placementWritten + static_cast<uint32_t>(placementRecords.size());
                PlacementRecordBinary record;
                record.itemId = placement.itemId;
                record.meta = placementMeta(placement);
                record.tileIndex = tileIndex;
                if (placementHasMechanic(placement)) {
                    record.mechanicIndex = mechanicWritten + static_cast<uint32_t>(mechanicRecords.size());
                    mechanicRecords.push_back(mechanicRecord(placement, placementOrdinal));
                }
                placementRecords.push_back(record);
                const uint64_t postingIndex = itemWriteCursor[placement.itemId]++;
                if (postingIndex >= itemPostings.size()) {
                    throw std::runtime_error("Item postings overflow while writing world index");
                }
                itemPostings[static_cast<size_t>(postingIndex)] = placementOrdinal;
            }
            tileRecords.push_back(tileRecord);
        }

        writeVectorAt(file, layout.tileOffset + static_cast<uint64_t>(tileWritten) * sizeof(TileRecordBinary), tileRecords);
        writeVectorAt(file, layout.placementOffset + static_cast<uint64_t>(placementWritten) * sizeof(PlacementRecordBinary), placementRecords);
        writeVectorAt(file, layout.mechanicOffset + static_cast<uint64_t>(mechanicWritten) * sizeof(MechanicRecordBinary), mechanicRecords);

        tileWritten += static_cast<uint32_t>(tileRecords.size());
        placementWritten += static_cast<uint32_t>(placementRecords.size());
        mechanicWritten += static_cast<uint32_t>(mechanicRecords.size());
        currentArea.reset();
    };

    size_t position = 4;
    while (position < data.size()) {
        const uint8_t value = data[position];
        if (value == NODE_ESCAPE) {
            position += 2;
            continue;
        }
        if (value == NODE_START) {
            const uint8_t nodeType = data[position + 1];
            const Context* parent = stack.empty() ? nullptr : &stack.back();
            Context context;
            context.type = nodeType;
            if (parent) {
                context.areaX = parent->areaX;
                context.areaY = parent->areaY;
                context.areaZ = parent->areaZ;
                context.tileX = parent->tileX;
                context.tileY = parent->tileY;
                context.tileZ = parent->tileZ;
                context.itemDepth = parent->itemDepth;
            }

            if (nodeType == OTBM_TILE_AREA && parent && parent->type == OTBM_MAP_DATA) {
                if (currentArea) {
                    throw std::runtime_error("Nested tile areas are unsupported");
                }
                PropertyReader reader(data, position + 2);
                context.areaX = reader.readU16();
                context.areaY = reader.readU16();
                context.areaZ = reader.readByte();
                currentArea.emplace();
                currentArea->baseX = static_cast<uint16_t>(context.areaX);
                currentArea->baseY = static_cast<uint16_t>(context.areaY);
                currentArea->z = static_cast<uint8_t>(context.areaZ);
            } else if ((nodeType == OTBM_TILE || nodeType == OTBM_HOUSETILE) && parent && parent->type == OTBM_TILE_AREA) {
                if (!currentArea || currentTile) {
                    throw std::runtime_error("Invalid tile state while writing world index");
                }
                PropertyReader reader(data, position + 2);
                context.tileX = parent->areaX + reader.readByte();
                context.tileY = parent->areaY + reader.readByte();
                context.tileZ = parent->areaZ;
                context.itemDepth = -1;
                currentTile.emplace();
                currentTile->x = static_cast<uint16_t>(context.tileX);
                currentTile->y = static_cast<uint16_t>(context.tileY);
                currentTile->z = static_cast<uint8_t>(context.tileZ);
                currentTile->kind = nodeType == OTBM_HOUSETILE ? 1 : 0;
                if (nodeType == OTBM_HOUSETILE) {
                    currentTile->houseId = reader.readU32();
                }
                while (reader.hasMore()) {
                    const uint8_t attribute = reader.readByte();
                    if (attribute == ATTR_TILE_FLAGS) {
                        currentTile->flags = reader.readU32();
                    } else if (attribute == ATTR_ITEM) {
                        PlacementBuffer inlinePlacement;
                        inlinePlacement.itemId = reader.readU16();
                        inlinePlacement.depth = -1;
                        inlinePlacement.node = false;
                        currentTile->placements.push_back(inlinePlacement);
                    } else {
                        throw std::runtime_error("Unsupported tile attribute " + std::to_string(attribute));
                    }
                }
            } else if (nodeType == OTBM_ITEM) {
                if (!parent || !currentTile) {
                    throw std::runtime_error("Item node is outside a tile while writing world index");
                }
                PropertyReader reader(data, position + 2);
                PlacementBuffer placement;
                placement.itemId = reader.readU16();
                placement.depth = parent->type == OTBM_ITEM ? parent->itemDepth + 1 : 0;
                placement.node = true;
                context.itemDepth = placement.depth;
                MechanicPlacement parsed;
                parseItemAttributes(reader, nullptr, parsed, nullptr, nullptr, nullptr);
                placement.actionId = parsed.actionId;
                placement.uniqueId = parsed.uniqueId;
                placement.houseDoorId = parsed.houseDoorId;
                placement.teleportDestination = parsed.teleportDestination;
                currentTile->placements.push_back(placement);
            }
            stack.push_back(context);
            position += 2;
            continue;
        }
        if (value == NODE_END) {
            if (stack.empty()) {
                throw std::runtime_error("Unexpected OTBM node end while writing world index");
            }
            const uint8_t endingType = stack.back().type;
            if (endingType == OTBM_TILE || endingType == OTBM_HOUSETILE) {
                if (!currentArea || !currentTile) {
                    throw std::runtime_error("Missing tile buffer at tile end");
                }
                currentArea->tiles.push_back(std::move(*currentTile));
                currentTile.reset();
            } else if (endingType == OTBM_TILE_AREA) {
                if (currentTile) {
                    throw std::runtime_error("Tile area ended with an open tile");
                }
                flushArea();
            }
            stack.pop_back();
            ++position;
            continue;
        }
        ++position;
    }

    if (currentArea || currentTile || !stack.empty()) {
        throw std::runtime_error("Incomplete world-index parse state");
    }
    if (tileWritten != scan.tileCount || placementWritten != scan.totalPlacements || mechanicWritten != scan.mechanics.size()) {
        throw std::runtime_error("World-index second-pass counts do not match the first-pass scan");
    }
    if (areaDirectory.size() != uniqueAreaCount(scan)) {
        throw std::runtime_error("World-index unique area count does not match the scan summary");
    }
    for (size_t itemId = 0; itemId < itemDirectory.size(); ++itemId) {
        if (itemWriteCursor[itemId] != itemDirectory[itemId].postingsStart + itemDirectory[itemId].count) {
            throw std::runtime_error("World-index item postings are incomplete");
        }
    }
    for (const auto& area : areaDirectory) {
        const uint32_t key = areaKey(area.baseX, area.baseY, area.z);
        if (areaWriteCursor[key] != static_cast<uint64_t>(area.postingsStart) + area.tileCount) {
            throw std::runtime_error("World-index tile-area postings are incomplete");
        }
        auto begin = areaPostings.begin() + area.postingsStart;
        auto end = begin + area.tileCount;
        std::sort(begin, end, [&](const uint32_t left, const uint32_t right) {
            if (tilePositionKeys[left] != tilePositionKeys[right]) {
                return tilePositionKeys[left] < tilePositionKeys[right];
            }
            return left < right;
        });
        for (auto iterator = begin + 1; iterator != end; ++iterator) {
            if (tilePositionKeys[*iterator] == tilePositionKeys[*(iterator - 1)]) {
                throw std::runtime_error("Duplicate tile position across tile-area nodes");
            }
        }
    }

    writeVectorAt(file, layout.itemDirectoryOffset, itemDirectory);
    writeVectorAt(file, layout.areaDirectoryOffset, areaDirectory);
    writeVectorAt(file, layout.areaPostingsOffset, areaPostings);
    writeVectorAt(file, layout.itemPostingsOffset, itemPostings);

    const uint64_t uniqueAreas = uniqueAreaCount(scan);
    std::array<uint8_t, WORLD_INDEX_HEADER_SIZE> header{};
    std::memcpy(header.data(), WORLD_INDEX_MAGIC.data(), WORLD_INDEX_MAGIC.size());
    putLittleEndian(header, 8, WORLD_INDEX_VERSION);
    putLittleEndian(header, 12, WORLD_INDEX_HEADER_SIZE);
    putLittleEndian(header, 16, layout.fileSize);
    putLittleEndian(header, 24, static_cast<uint64_t>(data.size()));
    putLittleEndian(header, 32, scan.tileCount);
    putLittleEndian(header, 40, scan.totalPlacements);
    putLittleEndian(header, 48, static_cast<uint64_t>(scan.mechanics.size()));
    putLittleEndian(header, 56, uniqueAreas);
    putLittleEndian(header, 64, scan.rawAreaCount);
    putLittleEndian(header, 72, layout.itemDirectoryOffset);
    putLittleEndian(header, 80, layout.areaDirectoryOffset);
    putLittleEndian(header, 88, layout.areaPostingsOffset);
    putLittleEndian(header, 96, layout.tileOffset);
    putLittleEndian(header, 104, layout.placementOffset);
    putLittleEndian(header, 112, layout.mechanicOffset);
    putLittleEndian(header, 120, layout.itemPostingsOffset);
    putLittleEndian(header, 128, static_cast<uint64_t>(ITEM_DIRECTORY_COUNT));
    putLittleEndian(header, 136, uniqueAreas);
    putLittleEndian(header, 144, static_cast<uint32_t>(sizeof(TileRecordBinary)));
    putLittleEndian(header, 148, static_cast<uint32_t>(sizeof(PlacementRecordBinary)));
    putLittleEndian(header, 152, static_cast<uint32_t>(sizeof(MechanicRecordBinary)));
    putLittleEndian(header, 156, static_cast<uint32_t>(sizeof(AreaRecordBinary)));
    putLittleEndian(header, 160, static_cast<uint32_t>(sizeof(uint32_t)));
    putLittleEndian(header, 164, scan.header.version);
    putLittleEndian(header, 168, static_cast<uint32_t>(scan.header.width));
    putLittleEndian(header, 172, static_cast<uint32_t>(scan.header.height));
    putLittleEndian(header, 176, scan.header.itemsMajor);
    putLittleEndian(header, 180, scan.header.itemsMinor);
    putLittleEndian(header, 184, scan.unknownAttributeTails);
    putLittleEndian(header, 192, static_cast<uint32_t>(scan.maxItemDepth < 0 ? 0 : scan.maxItemDepth));

    file.seekp(0);
    file.write(reinterpret_cast<const char*>(header.data()), static_cast<std::streamsize>(header.size()));
    file.flush();
    if (!file) {
        throw std::runtime_error("Cannot finalize world-index header");
    }
    file.close();
    std::filesystem::rename(temporaryPath, outputPath);

    std::cout << "{\"format\":\"canary-otbm-world-index-build-v1\",\"output\":\""
              << jsonEscape(outputPath.filename().string()) << "\",\"fileSize\":" << layout.fileSize
              << ",\"tileCount\":" << scan.tileCount
              << ",\"totalPlacements\":" << scan.totalPlacements
              << ",\"mechanicPlacements\":" << scan.mechanics.size()
              << ",\"areaCount\":" << uniqueAreas
              << ",\"rawAreaCount\":" << scan.rawAreaCount
              << ",\"uniqueItemIds\":" << uniqueItemIds(scan)
              << ",\"unknownAttributeTails\":" << scan.unknownAttributeTails
              << ",\"maxItemDepth\":" << scan.maxItemDepth << "}\n";
}

} // namespace

int main(int argc, char** argv) {
    const bool worldIndex = argc == 4 && std::string(argv[1]) == "--world-index";
    const bool patchAnchors = argc == 4 && std::string(argv[1]) == "--patch-anchors";
    if ((!worldIndex && !patchAnchors && argc != 3) || ((worldIndex || patchAnchors) && argc != 4)) {
        std::cerr << "usage: otbm_item_audit_scan MAP OUTPUT.json\n"
                  << "       otbm_item_audit_scan --world-index MAP OUTPUT.widx\n"
                  << "       otbm_item_audit_scan --patch-anchors MAP OUTPUT.json\n";
        return 2;
    }
    try {
        const bool explicitMode = worldIndex || patchAnchors;
        const std::filesystem::path mapPath = explicitMode ? argv[2] : argv[1];
        const std::filesystem::path outputPath = explicitMode ? argv[3] : argv[2];
        const auto data = readFile(mapPath);
        if (data.size() < 8) {
            throw std::runtime_error("OTBM file is too small");
        }
        const ScanData scan = scanMap(data);
        if (worldIndex) {
            writeWorldIndex(outputPath, data, scan);
        } else if (patchAnchors) {
            writePatchAnchorReport(mapPath, outputPath, data, scan);
            std::cout << "anchors=" << scan.patchAnchors.size() << "\n";
        } else {
            writeLegacyReport(mapPath, outputPath, data, scan);
            std::cout << "tiles=" << scan.tileCount << " placements=" << scan.totalPlacements
                      << " unique=" << uniqueItemIds(scan) << " mechanics=" << scan.mechanics.size() << "\n";
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << "\n";
        return 1;
    }
}
