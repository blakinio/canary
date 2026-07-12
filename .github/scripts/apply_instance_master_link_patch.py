from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1))


creature_hpp = Path("src/creatures/creature.hpp")
replace_once(
    creature_hpp,
    "class ItemType;\n",
    "class ItemType;\nclass InstanceCreatureBinder;\n",
)
replace_once(
    creature_hpp,
    "\tbool setMaster(const std::shared_ptr<Creature> &newMaster, bool reloadCreature = false);\n",
    "\tbool setMaster(const std::shared_ptr<Creature> &newMaster, bool reloadCreature = false);\n"
    "\tbool setMaster(const std::shared_ptr<Creature> &newMaster, InstanceCreatureBinder &binder, bool reloadCreature = false);\n",
)

creature_cpp = Path("src/creatures/creature.cpp")
replace_once(
    creature_cpp,
    '#include "game/game.hpp"\n',
    '#include "game/game.hpp"\n#include "game/instance/instance_creature_binder.hpp"\n',
)
text = creature_cpp.read_text()
anchor = "\nbool Creature::addCondition(const std::shared_ptr<Condition> &condition, bool attackerPlayer /* = false*/) {"
if text.count(anchor) != 1:
    raise RuntimeError("creature.cpp: addCondition anchor is not unique")
if "InstanceCreatureBinder &binder" in text:
    raise RuntimeError("creature.cpp: instance-aware setMaster overload already exists")
overload = '''

bool Creature::setMaster(const std::shared_ptr<Creature> &newMaster, InstanceCreatureBinder &binder, bool reloadCreature /* = false*/) {
\tif (!newMaster) {
\t\treturn setMaster(newMaster, reloadCreature);
\t}

\tconst auto &self = getCreature();
\treturn binder.inheritAndApply(*newMaster, *self, [this, newMaster, reloadCreature] {
\t\treturn setMaster(newMaster, reloadCreature);
\t});
}
'''.rstrip()
creature_cpp.write_text(text.replace(anchor, overload + "\n" + anchor, 1))

test_path = Path("tests/unit/game/instance/instance_creature_binder_test.cpp")
replace_once(
    test_path,
    '#include "game/instance/instance_creature_binder.hpp"\n',
    '#include "creatures/monsters/monster.hpp"\n'
    '#include "creatures/monsters/monsters.hpp"\n'
    '#include "game/instance/instance_creature_binder.hpp"\n',
)
helper_anchor = "\tstd::vector<InstanceMapRegion> makeBinderRegions(std::size_t count) {"
helper = '''
\tstd::shared_ptr<Monster> makeRuntimeMonster(const std::string &name) {
\t\tconst auto monsterType = std::make_shared<MonsterType>(name);
\t\tconst auto monster = std::make_shared<Monster>(monsterType);
\t\tmonster->setID();
\t\treturn monster;
\t}

'''
text = test_path.read_text()
if text.count(helper_anchor) != 1:
    raise RuntimeError("binder test: region helper anchor is not unique")
text = text.replace(helper_anchor, helper + helper_anchor, 1)
if "InstanceAwareSetMasterCommitsOwnershipAndLink" in text:
    raise RuntimeError("binder test: runtime setMaster tests already exist")
tests = '''

TEST(InstanceCreatureBinderTest, LegacySetMasterKeepsNormalWorldBehavior) {
\tconst auto master = makeRuntimeMonster("legacy-master");
\tconst auto summon = makeRuntimeMonster("legacy-summon");

\tEXPECT_TRUE(summon->setMaster(master));
\tEXPECT_EQ(master, summon->getMaster());
\tEXPECT_TRUE(summon->hasBeenSummoned());
\tASSERT_EQ(1u, master->getSummons().size());
\tEXPECT_EQ(summon, master->getSummons().front());
}

TEST(InstanceCreatureBinderTest, InstanceAwareSetMasterCommitsOwnershipAndLink) {
\tInstanceManager manager(makeBinderRegions(1));
\tInstanceCreatureBinder binder(manager);
\tconst auto instance = manager.createInstance({ .name = "runtime-master-link" });
\tconst auto master = makeRuntimeMonster("instance-master");
\tconst auto summon = makeRuntimeMonster("instance-summon");
\tASSERT_TRUE(instance.ok);
\tASSERT_TRUE(binder.bind(instance.id, *master));

\tEXPECT_TRUE(summon->setMaster(master, binder));
\tEXPECT_EQ(master, summon->getMaster());
\tEXPECT_TRUE(summon->hasBeenSummoned());
\tASSERT_TRUE(binder.ownerOf(*summon).has_value());
\tEXPECT_EQ(instance.id, *binder.ownerOf(*summon));
\tASSERT_EQ(1u, master->getSummons().size());
\tEXPECT_EQ(summon, master->getSummons().front());
}

TEST(InstanceCreatureBinderTest, InstanceAwareSetMasterRejectsCrossInstanceBeforeMutation) {
\tInstanceManager manager(makeBinderRegions(2));
\tInstanceCreatureBinder binder(manager);
\tconst auto first = manager.createInstance({ .name = "first" });
\tconst auto second = manager.createInstance({ .name = "second" });
\tconst auto master = makeRuntimeMonster("first-master");
\tconst auto summon = makeRuntimeMonster("second-summon");
\tASSERT_TRUE(first.ok);
\tASSERT_TRUE(second.ok);
\tASSERT_TRUE(binder.bind(first.id, *master));
\tASSERT_TRUE(binder.bind(second.id, *summon));

\tEXPECT_FALSE(summon->setMaster(master, binder));
\tEXPECT_FALSE(summon->getMaster());
\tEXPECT_FALSE(summon->hasBeenSummoned());
\tEXPECT_TRUE(master->getSummons().empty());
\tEXPECT_EQ(first.id, *binder.ownerOf(*master));
\tEXPECT_EQ(second.id, *binder.ownerOf(*summon));
}

TEST(InstanceCreatureBinderTest, InstanceAwareSetMasterRejectsUnownedMasterForOwnedSummon) {
\tInstanceManager manager(makeBinderRegions(1));
\tInstanceCreatureBinder binder(manager);
\tconst auto instance = manager.createInstance({ .name = "owned-summon" });
\tconst auto master = makeRuntimeMonster("unowned-master");
\tconst auto summon = makeRuntimeMonster("owned-summon");
\tASSERT_TRUE(instance.ok);
\tASSERT_TRUE(binder.bind(instance.id, *summon));

\tEXPECT_FALSE(summon->setMaster(master, binder));
\tEXPECT_FALSE(summon->getMaster());
\tEXPECT_FALSE(summon->hasBeenSummoned());
\tEXPECT_TRUE(master->getSummons().empty());
\tEXPECT_FALSE(binder.ownerOf(*master).has_value());
\tEXPECT_EQ(instance.id, *binder.ownerOf(*summon));
}

TEST(InstanceCreatureBinderTest, InstanceAwareSetMasterReassignsWithinSameInstance) {
\tInstanceManager manager(makeBinderRegions(1));
\tInstanceCreatureBinder binder(manager);
\tconst auto instance = manager.createInstance({ .name = "reassign" });
\tconst auto firstMaster = makeRuntimeMonster("first-master");
\tconst auto secondMaster = makeRuntimeMonster("second-master");
\tconst auto summon = makeRuntimeMonster("reassigned-summon");
\tASSERT_TRUE(instance.ok);
\tASSERT_TRUE(binder.bind(instance.id, *firstMaster));
\tASSERT_TRUE(binder.bind(instance.id, *secondMaster));
\tASSERT_TRUE(summon->setMaster(firstMaster, binder));

\tEXPECT_TRUE(summon->setMaster(secondMaster, binder));
\tEXPECT_EQ(secondMaster, summon->getMaster());
\tEXPECT_TRUE(firstMaster->getSummons().empty());
\tASSERT_EQ(1u, secondMaster->getSummons().size());
\tEXPECT_EQ(summon, secondMaster->getSummons().front());
\tEXPECT_EQ(instance.id, *binder.ownerOf(*summon));
\tEXPECT_EQ(3u, manager.registeredCreatureCount(instance.id));
}

TEST(InstanceCreatureBinderTest, InstanceAwareClearMasterPreservesOwnershipBoundary) {
\tInstanceManager manager(makeBinderRegions(1));
\tInstanceCreatureBinder binder(manager);
\tconst auto instance = manager.createInstance({ .name = "clear-master" });
\tconst auto master = makeRuntimeMonster("clear-master");
\tconst auto summon = makeRuntimeMonster("clear-summon");
\tASSERT_TRUE(instance.ok);
\tASSERT_TRUE(binder.bind(instance.id, *master));
\tASSERT_TRUE(summon->setMaster(master, binder));

\tEXPECT_TRUE(summon->setMaster(nullptr, binder));
\tEXPECT_FALSE(summon->getMaster());
\tEXPECT_TRUE(summon->hasBeenSummoned());
\tEXPECT_TRUE(master->getSummons().empty());
\tASSERT_TRUE(binder.ownerOf(*summon).has_value());
\tEXPECT_EQ(instance.id, *binder.ownerOf(*summon));
}
'''
test_path.write_text(text.rstrip() + tests.rstrip() + "\n")
