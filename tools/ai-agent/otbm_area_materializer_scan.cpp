#if defined(__GNUC__) && !defined(__clang__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmaybe-uninitialized"
#endif
#define main otbm_item_audit_scan_embedded_main
#include "otbm_item_audit_scan.cpp"
#undef main
#if defined(__GNUC__) && !defined(__clang__)
#pragma GCC diagnostic pop
#endif

namespace {

constexpr const char* NATIVE_TILE_AREA_SPAN_FORMAT = "canary-otbm-native-tile-area-spans-v1";
constexpr const char* NATIVE_TILE_SPAN_FORMAT = "canary-otbm-native-tile-spans-v1";

struct TileAreaSpan {
    uint16_t baseX = 0;
    uint16_t baseY = 0;
    uint8_t z = 0;
    size_t startOffset = 0;
    size_t endOffsetExclusive = 0;
};

struct TileSpan {
    uint16_t baseX = 0;
    uint16_t baseY = 0;
    uint8_t areaZ = 0;
    uint16_t x = 0;
    uint16_t y = 0;
    uint8_t z = 0;
    uint8_t nodeType = 0;
    size_t startOffset = 0;
    size_t endOffsetExclusive = 0;
};

struct SpanContext {
    uint8_t type = 0;
    size_t startOffset = 0;
    int areaX = -1;
    int areaY = -1;
    int areaZ = -1;
    std::optional<size_t> tileAreaIndex;
    std::optional<size_t> tileIndex;
};

struct StructuralSpanReport {
    size_t mapDataStartOffset = 0;
    size_t mapDataEndOffset = 0;
    size_t insertionOffset = 0;
    bool tileAreaSectionContiguous = true;
    std::vector<TileAreaSpan> areas;
    std::vector<TileSpan> tiles;
};

StructuralSpanReport collectStructuralSpans(const std::vector<uint8_t>& data) {
    // Reuse the existing full native scanner first. The span walk below only
    // records physical node boundaries after the canonical parser accepts the map.
    static_cast<void>(scanMap(data));

    StructuralSpanReport report;
    std::vector<SpanContext> stack;
    stack.reserve(64);
    size_t mapDataCount = 0;
    bool sawTileArea = false;
    bool tileAreaSectionClosed = false;
    std::optional<size_t> lastTileAreaEnd;

    size_t position = 4;
    while (position < data.size()) {
        const uint8_t value = data[position];
        if (value == NODE_ESCAPE) {
            if (position + 1 >= data.size()) {
                throw std::runtime_error("Dangling OTBM escape byte while collecting structural spans");
            }
            position += 2;
            continue;
        }
        if (value == NODE_START) {
            if (position + 1 >= data.size()) {
                throw std::runtime_error("OTBM node has no type while collecting structural spans");
            }
            const uint8_t nodeType = data[position + 1];
            const SpanContext* parent = stack.empty() ? nullptr : &stack.back();
            SpanContext context;
            context.type = nodeType;
            context.startOffset = position;
            if (parent) {
                context.areaX = parent->areaX;
                context.areaY = parent->areaY;
                context.areaZ = parent->areaZ;
            }

            if (nodeType == OTBM_MAP_DATA) {
                ++mapDataCount;
                if (mapDataCount != 1) {
                    throw std::runtime_error("OTBM contains more than one MAP_DATA node");
                }
                report.mapDataStartOffset = position;
            }

            if (parent && parent->type == OTBM_MAP_DATA) {
                if (nodeType == OTBM_TILE_AREA) {
                    if (tileAreaSectionClosed) {
                        report.tileAreaSectionContiguous = false;
                    }
                    PropertyReader reader(data, position + 2);
                    TileAreaSpan span;
                    span.baseX = reader.readU16();
                    span.baseY = reader.readU16();
                    span.z = reader.readByte();
                    span.startOffset = position;
                    context.areaX = span.baseX;
                    context.areaY = span.baseY;
                    context.areaZ = span.z;
                    context.tileAreaIndex = report.areas.size();
                    report.areas.push_back(span);
                    sawTileArea = true;
                } else if (sawTileArea) {
                    tileAreaSectionClosed = true;
                }
            } else if (
                parent && parent->type == OTBM_TILE_AREA && (nodeType == OTBM_TILE || nodeType == OTBM_HOUSETILE)
            ) {
                if (parent->areaX < 0 || parent->areaY < 0 || parent->areaZ < 0) {
                    throw std::runtime_error("OTBM tile has no resolved TILE_AREA parent coordinates");
                }
                PropertyReader reader(data, position + 2);
                const int absoluteX = parent->areaX + static_cast<int>(reader.readByte());
                const int absoluteY = parent->areaY + static_cast<int>(reader.readByte());
                if (absoluteX > 0xFFFF || absoluteY > 0xFFFF || parent->areaZ > 15) {
                    throw std::runtime_error("OTBM tile coordinates are outside the supported range");
                }
                TileSpan span;
                span.baseX = static_cast<uint16_t>(parent->areaX);
                span.baseY = static_cast<uint16_t>(parent->areaY);
                span.areaZ = static_cast<uint8_t>(parent->areaZ);
                span.x = static_cast<uint16_t>(absoluteX);
                span.y = static_cast<uint16_t>(absoluteY);
                span.z = static_cast<uint8_t>(parent->areaZ);
                span.nodeType = nodeType;
                span.startOffset = position;
                context.tileIndex = report.tiles.size();
                report.tiles.push_back(span);
            }

            stack.push_back(context);
            position += 2;
            continue;
        }
        if (value == NODE_END) {
            if (stack.empty()) {
                throw std::runtime_error("Unexpected OTBM node end while collecting structural spans");
            }
            const SpanContext ending = stack.back();
            if (ending.tileIndex) {
                TileSpan& span = report.tiles[*ending.tileIndex];
                span.endOffsetExclusive = position + 1;
            }
            if (ending.tileAreaIndex) {
                TileAreaSpan& span = report.areas[*ending.tileAreaIndex];
                span.endOffsetExclusive = position + 1;
                lastTileAreaEnd = position + 1;
            }
            if (ending.type == OTBM_MAP_DATA) {
                report.mapDataEndOffset = position;
            }
            stack.pop_back();
            ++position;
            continue;
        }
        ++position;
    }

    if (!stack.empty()) {
        throw std::runtime_error("OTBM contains unterminated nodes while collecting structural spans");
    }
    if (mapDataCount != 1 || report.mapDataEndOffset == 0) {
        throw std::runtime_error("OTBM must contain exactly one complete MAP_DATA node");
    }
    if (!lastTileAreaEnd) {
        throw std::runtime_error("OTBM contains no direct TILE_AREA child under MAP_DATA");
    }
    report.insertionOffset = *lastTileAreaEnd;
    for (const auto& span : report.areas) {
        if (span.endOffsetExclusive <= span.startOffset || span.endOffsetExclusive > data.size()) {
            throw std::runtime_error("Incomplete TILE_AREA physical span");
        }
    }
    for (const auto& span : report.tiles) {
        if (span.endOffsetExclusive <= span.startOffset || span.endOffsetExclusive > data.size()) {
            throw std::runtime_error("Incomplete tile physical span");
        }
    }
    return report;
}

void writeTileAreaSpanReport(
    const std::filesystem::path& mapPath,
    const std::filesystem::path& outputPath,
    const std::vector<uint8_t>& data
) {
    const ScanData scan = scanMap(data);
    const MapHeaderInfo header = scan.header;
    const StructuralSpanReport report = collectStructuralSpans(data);

    std::filesystem::create_directories(outputPath.parent_path().empty() ? std::filesystem::path(".") : outputPath.parent_path());
    std::ofstream out(outputPath);
    if (!out) {
        throw std::runtime_error("Cannot create tile-area span report");
    }
    out << "{\n"
        << "  \"format\": \"" << NATIVE_TILE_AREA_SPAN_FORMAT << "\",\n"
        << "  \"source\": {\"path\": \"" << jsonEscape(mapPath.filename().string())
        << "\", \"size\": " << data.size()
        << ", \"otbmVersion\": " << header.version
        << ", \"width\": " << header.width
        << ", \"height\": " << header.height
        << ", \"itemsMajor\": " << header.itemsMajor
        << ", \"itemsMinor\": " << header.itemsMinor
        << ", \"unknownAttributeTails\": " << scan.unknownAttributeTails << "},\n"
        << "  \"mapData\": {\"startOffset\": " << report.mapDataStartOffset
        << ", \"endOffset\": " << report.mapDataEndOffset
        << ", \"insertionOffset\": " << report.insertionOffset
        << ", \"tileAreaSectionContiguous\": " << (report.tileAreaSectionContiguous ? "true" : "false") << "},\n"
        << "  \"areas\": [\n";

    for (size_t index = 0; index < report.areas.size(); ++index) {
        const auto& span = report.areas[index];
        out << "    {\"baseX\": " << span.baseX
            << ", \"baseY\": " << span.baseY
            << ", \"z\": " << static_cast<unsigned int>(span.z)
            << ", \"startOffset\": " << span.startOffset
            << ", \"endOffsetExclusive\": " << span.endOffsetExclusive
            << ", \"byteLength\": " << (span.endOffsetExclusive - span.startOffset) << "}";
        if (index + 1 != report.areas.size()) {
            out << ',';
        }
        out << '\n';
    }
    out << "  ]\n}\n";
    if (!out) {
        throw std::runtime_error("Cannot finalize tile-area span report");
    }
}

void writeTileSpanReport(
    const std::filesystem::path& mapPath,
    const std::filesystem::path& outputPath,
    const std::vector<uint8_t>& data
) {
    const ScanData scan = scanMap(data);
    const MapHeaderInfo header = scan.header;
    const StructuralSpanReport report = collectStructuralSpans(data);

    std::filesystem::create_directories(outputPath.parent_path().empty() ? std::filesystem::path(".") : outputPath.parent_path());
    std::ofstream out(outputPath);
    if (!out) {
        throw std::runtime_error("Cannot create tile span report");
    }
    out << "{\n"
        << "  \"format\": \"" << NATIVE_TILE_SPAN_FORMAT << "\",\n"
        << "  \"source\": {\"path\": \"" << jsonEscape(mapPath.filename().string())
        << "\", \"size\": " << data.size()
        << ", \"otbmVersion\": " << header.version
        << ", \"width\": " << header.width
        << ", \"height\": " << header.height
        << ", \"itemsMajor\": " << header.itemsMajor
        << ", \"itemsMinor\": " << header.itemsMinor
        << ", \"unknownAttributeTails\": " << scan.unknownAttributeTails << "},\n"
        << "  \"tiles\": [\n";

    for (size_t index = 0; index < report.tiles.size(); ++index) {
        const auto& span = report.tiles[index];
        out << "    {\"areaBaseX\": " << span.baseX
            << ", \"areaBaseY\": " << span.baseY
            << ", \"areaZ\": " << static_cast<unsigned int>(span.areaZ)
            << ", \"x\": " << span.x
            << ", \"y\": " << span.y
            << ", \"z\": " << static_cast<unsigned int>(span.z)
            << ", \"nodeType\": " << static_cast<unsigned int>(span.nodeType)
            << ", \"startOffset\": " << span.startOffset
            << ", \"endOffsetExclusive\": " << span.endOffsetExclusive
            << ", \"byteLength\": " << (span.endOffsetExclusive - span.startOffset) << "}";
        if (index + 1 != report.tiles.size()) {
            out << ',';
        }
        out << '\n';
    }
    out << "  ]\n}\n";
    if (!out) {
        throw std::runtime_error("Cannot finalize tile span report");
    }
}

} // namespace

int main(int argc, char** argv) {
    const bool tileAreaSpans = argc == 4 && std::string(argv[1]) == "--tile-area-spans";
    const bool tileSpans = argc == 4 && std::string(argv[1]) == "--tile-spans";
    if (!tileAreaSpans && !tileSpans) {
        return otbm_item_audit_scan_embedded_main(argc, argv);
    }
    try {
        const std::filesystem::path mapPath = argv[2];
        const std::filesystem::path outputPath = argv[3];
        const auto data = readFile(mapPath);
        if (data.size() < 8) {
            throw std::runtime_error("OTBM file is too small");
        }
        if (tileAreaSpans) {
            writeTileAreaSpanReport(mapPath, outputPath, data);
        } else {
            writeTileSpanReport(mapPath, outputPath, data);
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
