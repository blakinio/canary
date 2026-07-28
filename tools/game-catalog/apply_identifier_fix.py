from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


source_path = Path("src/game/catalog/game_catalog_exporter.cpp")
source = source_path.read_text(encoding="utf-8")

source = replace_once(
    source,
    "\t[[nodiscard]] Json commonEntity(\n",
    """\tvoid sortIdentifiers(Json &identifiers) {
\t\tauto &identifierArray = identifiers.get_ref<Json::array_t&>();
\t\tstd::ranges::sort(identifierArray, {}, [](const Json &identifier) {
\t\t\treturn std::pair(
\t\t\t\tidentifier.at(\"namespace\").get<std::string>(),
\t\t\t\tidentifier.at(\"value\").get<std::string>()
\t\t\t);
\t\t});
\t}

\t[[nodiscard]] Json commonEntity(
""",
    "identifier sorter insertion",
)

source = replace_once(
    source,
    """\tstd::unordered_map<std::uint16_t, std::string> itemKeys;

\tfor (std::size_t id = 0; id < items.size(); ++id) {
""",
    """\tstd::unordered_map<std::uint16_t, std::string> itemKeys;
\tstd::unordered_map<std::uint16_t, std::size_t> wareIdCounts;
\tfor (std::size_t id = 0; id < items.size(); ++id) {
\t\tconst auto &item = items.getItemType(id);
\t\tif (item.loaded && item.id != 0 && !item.name.empty() && item.wareId != 0) {
\t\t\t++wareIdCounts[item.wareId];
\t\t}
\t}
\tstd::unordered_map<std::uint32_t, std::size_t> monsterRaceIdCounts;
\tfor (const auto &[registryKey, monster] : monsters.monsters) {
\t\tif (monster && !registryKey.empty() && !monster->name.empty() && monster->info.raceid != 0) {
\t\t\t++monsterRaceIdCounts[static_cast<std::uint32_t>(monster->info.raceid)];
\t\t}
\t}

\tfor (std::size_t id = 0; id < items.size(); ++id) {
""",
    "identifier count prepass",
)

source = replace_once(
    source,
    """\t\tif (item.wareId != 0) {
\t\t\tidentifiers.push_back(Json { { \"namespace\", \"canary.ware_id\" }, { \"value\", std::to_string(item.wareId) } });
\t\t}
""",
    """\t\tif (item.wareId != 0 && wareIdCounts[item.wareId] == 1) {
\t\t\tidentifiers.push_back(Json { { \"namespace\", \"canary.ware_id\" }, { \"value\", std::to_string(item.wareId) } });
\t\t}
\t\tsortIdentifiers(identifiers);
""",
    "unique ware identifier emission",
)

source = replace_once(
    source,
    """\t\tif (monster->info.raceid != 0) {
\t\t\tidentifiers.push_back(Json { { \"namespace\", \"canary.monster_race_id\" }, { \"value\", std::to_string(monster->info.raceid) } });
\t\t}
""",
    """\t\tif (monster->info.raceid != 0 && monsterRaceIdCounts[static_cast<std::uint32_t>(monster->info.raceid)] == 1) {
\t\t\tidentifiers.push_back(Json { { \"namespace\", \"canary.monster_race_id\" }, { \"value\", std::to_string(monster->info.raceid) } });
\t\t}
\t\tsortIdentifiers(identifiers);
""",
    "unique race identifier emission",
)

source = replace_once(
    source,
    """\tstd::unordered_set<std::string> entityKeys;
\tstd::pair<std::string, std::string> previousEntity;
""",
    """\tstd::unordered_set<std::string> entityKeys;
\tstd::unordered_map<std::string, std::string> identifierOwners;
\tstd::pair<std::string, std::string> previousEntity;
""",
    "identifier owner registry",
)

source = replace_once(
    source,
    """\t\tif (entity.at(\"introduced_in\").is_string() && entity.at(\"removed_in\").is_string()) {
\t\t\tconst auto introduced = releaseOrders[entity.at(\"introduced_in\").get<std::string>()];
\t\t\tconst auto removed = releaseOrders[entity.at(\"removed_in\").get<std::string>()];
\t\t\tif (removed <= introduced) {
\t\t\t\terrors.emplace_back(\"Entity removed_in is not an exclusive later release: \" + key);
\t\t\t}
\t\t}
""",
    """\t\tif (entity.at(\"introduced_in\").is_string() && entity.at(\"removed_in\").is_string()) {
\t\t\tconst auto introduced = releaseOrders[entity.at(\"introduced_in\").get<std::string>()];
\t\t\tconst auto removed = releaseOrders[entity.at(\"removed_in\").get<std::string>()];
\t\t\tif (removed <= introduced) {
\t\t\t\terrors.emplace_back(\"Entity removed_in is not an exclusive later release: \" + key);
\t\t\t}
\t\t}
\t\tif (!entity.contains(\"identifiers\") || !entity.at(\"identifiers\").is_array()) {
\t\t\terrors.emplace_back(\"Entity identifiers are missing or invalid: \" + key);
\t\t} else {
\t\t\tstd::optional<std::pair<std::string, std::string>> previousIdentifier;
\t\t\tfor (const auto &identifier : entity.at(\"identifiers\")) {
\t\t\t\tif (!identifier.is_object() || !identifier.contains(\"namespace\") || !identifier.at(\"namespace\").is_string()
\t\t\t\t    || !identifier.contains(\"value\") || !identifier.at(\"value\").is_string()) {
\t\t\t\t\terrors.emplace_back(\"Entity contains an invalid identifier: \" + key);
\t\t\t\t\tcontinue;
\t\t\t\t}
\t\t\t\tconst auto namespaceValue = identifier.at(\"namespace\").get<std::string>();
\t\t\t\tconst auto identifierValue = identifier.at(\"value\").get<std::string>();
\t\t\t\tconst std::pair currentIdentifier(namespaceValue, identifierValue);
\t\t\t\tif (namespaceValue.empty() || identifierValue.empty() || (previousIdentifier && *previousIdentifier >= currentIdentifier)) {
\t\t\t\t\terrors.emplace_back(\"Entity identifiers are empty, duplicated, or not sorted: \" + key);
\t\t\t\t}
\t\t\t\tpreviousIdentifier = currentIdentifier;
\t\t\t\tconst auto identityKey = namespaceValue + \"\\0\" + identifierValue;
\t\t\t\tconst auto [owner, inserted] = identifierOwners.emplace(identityKey, key);
\t\t\t\tif (!inserted && owner->second != key) {
\t\t\t\t\terrors.emplace_back(\"Identifier resolves to multiple canonical entities: \" + namespaceValue + \":\" + identifierValue);
\t\t\t\t}
\t\t\t}
\t\t}
""",
    "producer identifier validation",
)
source_path.write_text(source, encoding="utf-8", newline="\n")

test_path = Path("tests/unit/game/catalog/game_catalog_test.cpp")
test = test_path.read_text(encoding="utf-8")
test = replace_once(
    test,
    "TEST(GameCatalogExporter, FixedInputsProduceByteIdenticalOutput) {\n",
    """TEST(GameCatalogExporter, NonUniqueSnapshotIdentifiersRemainDataOnlyAndCollisionsFailClosed) {
\tItems items;
\tMonsters monsters;
\tpopulateRuntime(items, monsters);
\titems.getItems()[2516].wareId = 777;
\titems.getItems().resize(2518);
\tauto &secondItem = items.getItems()[2517];
\tsecondItem.loaded = true;
\tsecondItem.id = 2517;
\tsecondItem.name = \"Dragon Shield Replica\";
\tsecondItem.type = ITEM_TYPE_SHIELD;
\tsecondItem.wareId = 777;

\tauto secondMonster = std::make_shared<MonsterType>(\"Dragon Replica\");
\tsecondMonster->info.health = 1;
\tsecondMonster->info.healthMax = 1;
\tsecondMonster->info.raceid = 34;
\tmonsters.monsters.emplace(\"dragon replica\", std::move(secondMonster));

\tauto document = buildSnapshotDocument(
\t\tfixtureManifest(), items, monsters, \"2026-07-28T00:00:00Z\",
\t\t\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\",
\t\t\"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\"
\t);
\tEXPECT_TRUE(validateSnapshotDocument(document).empty());

\tstd::size_t duplicateWareRecords = 0;
\tstd::size_t duplicateRaceRecords = 0;
\tfor (const auto &entity : document.at(\"entities\")) {
\t\tconst auto &data = entity.at(\"data\");
\t\tconst auto hasIdentifier = [&entity](const std::string &identifierNamespace) {
\t\t\treturn std::ranges::any_of(entity.at(\"identifiers\"), [&identifierNamespace](const auto &identifier) {
\t\t\t\treturn identifier.at(\"namespace\") == identifierNamespace;
\t\t\t});
\t\t};
\t\tif (entity.at(\"type\") == \"item\" && data.at(\"ware_id\") == 777) {
\t\t\t++duplicateWareRecords;
\t\t\tEXPECT_FALSE(hasIdentifier(\"canary.ware_id\"));
\t\t}
\t\tif (entity.at(\"type\") == \"creature\" && data.at(\"race_id\") == 34) {
\t\t\t++duplicateRaceRecords;
\t\t\tEXPECT_FALSE(hasIdentifier(\"canary.monster_race_id\"));
\t\t}
\t}
\tEXPECT_EQ(duplicateWareRecords, 2);
\tEXPECT_EQ(duplicateRaceRecords, 2);

\tauto &firstEntityIdentifiers = document.at(\"entities\").front().at(\"identifiers\");
\tauto &secondEntityIdentifiers = document.at(\"entities\").at(1).at(\"identifiers\");
\tsecondEntityIdentifiers.push_back(firstEntityIdentifiers.front());
\tEXPECT_FALSE(validateSnapshotDocument(document).empty());
}

TEST(GameCatalogExporter, FixedInputsProduceByteIdenticalOutput) {
""",
    "identifier regression test",
)
test_path.write_text(test, encoding="utf-8", newline="\n")
