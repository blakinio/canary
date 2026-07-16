/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_record_handoff.hpp"

#include "../../../shared/game/multichannel/fake_cluster_pending_operation_repository.hpp"
#include "../../../shared/game/multichannel/fake_cluster_record_ownership_resolver.hpp"

#include <atomic>
#include <gtest/gtest.h>
#include <mutex>
#include <thread>
#include <vector>

namespace {
	constexpr const char* TestKind = "PLAYER_INBOX";

	ClusterPendingOperationRecord makeRecord(const std::string &operationId, int32_t recordId, int64_t createdAtMs) {
		ClusterPendingOperationRecord record;
		record.operationId = operationId;
		record.recordKind = TestKind;
		record.recordId = recordId;
		record.operationType = "DELIVER_MAIL_ITEM";
		record.payload = "test-payload";
		record.enqueuedByChannelId = 1;
		record.createdAtMs = createdAtMs;
		return record;
	}

	// Minimal handler double: always reports the configured outcome,
	// counts how many times each verb was called - enough to assert
	// ClusterRecordHandoff's dispatch logic without any real business
	// effect (that's PR 2's job, tested against the mail-specific
	// scenarios instead).
	class RecordingHandler : public IClusterRecordOperationHandler {
	public:
		ClusterRecordApplyResult applyOwned(const ClusterPendingOperationRecord &record) override {
			++applyOwnedCallCount;
			lastAppliedOperationId = record.operationId;
			return ownedResult;
		}

		ClusterRecordApplyResult applyUnowned(const ClusterPendingOperationRecord &record) override {
			++applyUnownedCallCount;
			lastAppliedOperationId = record.operationId;
			return unownedResult;
		}

		int32_t applyOwnedCallCount = 0;
		int32_t applyUnownedCallCount = 0;
		std::string lastAppliedOperationId;
		ClusterRecordApplyResult ownedResult { ClusterRecordApplyOutcome::Applied, "" };
		ClusterRecordApplyResult unownedResult { ClusterRecordApplyOutcome::Applied, "" };
	};
} // namespace

class ClusterRecordHandoffTest : public ::testing::Test {
protected:
	FakeClusterPendingOperationRepository repository;
	FakeClusterRecordOwnershipResolver resolver;
	ClusterRecordHandoff handoff { repository, resolver };
};

// 1. First enqueue of a fresh operation_id succeeds.
TEST_F(ClusterRecordHandoffTest, FirstEnqueueSucceeds) {
	const auto record = makeRecord("op-1", 100, 1000);
	EXPECT_TRUE(handoff.enqueue(record));
	EXPECT_EQ(1u, repository.rowCountForTesting());
}

// 2. Re-enqueue of the same operation_id is rejected (idempotent no-op).
TEST_F(ClusterRecordHandoffTest, ReplayEnqueueIsRejected) {
	const auto record = makeRecord("op-1", 100, 1000);
	ASSERT_TRUE(handoff.enqueue(record));
	EXPECT_FALSE(handoff.enqueue(record));
	EXPECT_EQ(1u, repository.rowCountForTesting());
}

// 3. Ownership resolution: online here / online elsewhere / offline everywhere.
TEST_F(ClusterRecordHandoffTest, ResolveOwnershipReflectsResolverState) {
	resolver.setOwnedByChannelForTesting(TestKind, 100, 2);
	EXPECT_EQ(ClusterRecordOwnershipOutcome::OwnedByChannel, handoff.resolveOwnership(TestKind, 100, std::nullopt).outcome);
	EXPECT_EQ(2, handoff.resolveOwnership(TestKind, 100, std::nullopt).ownerChannelId);

	resolver.setNoLiveOwnerForTesting(TestKind, 101);
	EXPECT_EQ(ClusterRecordOwnershipOutcome::NoLiveOwner, handoff.resolveOwnership(TestKind, 101, std::nullopt).outcome);

	// No override set for 102 -> defaults to Unknown (fail-closed default).
	EXPECT_EQ(ClusterRecordOwnershipOutcome::Unknown, handoff.resolveOwnership(TestKind, 102, std::nullopt).outcome);
}

// 4. Ownership resolution for a statically-owned kind (HOUSE): the caller-
// supplied recordChannelId is echoed back directly, no resolver override needed.
TEST_F(ClusterRecordHandoffTest, StaticallyOwnedKindEchoesCallerSuppliedChannel) {
	const auto ownership = handoff.resolveOwnership("HOUSE", 55, 3);
	EXPECT_EQ(ClusterRecordOwnershipOutcome::OwnedByChannel, ownership.outcome);
	EXPECT_EQ(3, ownership.ownerChannelId);
}

// 5. Apply succeeds when this process is the resolved owner; row becomes APPLIED.
TEST_F(ClusterRecordHandoffTest, SweepAppliesWhenThisProcessIsOwner) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setOwnedByChannelForTesting(TestKind, 100, 7);

	RecordingHandler handler;
	const auto transitioned = handoff.sweep(TestKind, 7, 10, 2000, handler);

	EXPECT_EQ(1, transitioned);
	EXPECT_EQ(1, handler.applyOwnedCallCount);
	EXPECT_EQ(0, handler.applyUnownedCallCount);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Applied, row->status);
}

// 6. Apply is skipped (row stays PENDING) when another process is the resolved owner.
TEST_F(ClusterRecordHandoffTest, SweepSkipsWhenAnotherChannelIsOwner) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setOwnedByChannelForTesting(TestKind, 100, 9);

	RecordingHandler handler;
	const auto transitioned = handoff.sweep(TestKind, 7, 10, 2000, handler);

	EXPECT_EQ(0, transitioned);
	EXPECT_EQ(0, handler.applyOwnedCallCount);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Pending, row->status);
}

// 7. Two ClusterRecordHandoff instances (simulating two processes) both
// consider the same PENDING row; only the one whose channel id matches
// the resolved owner actually applies it - the other must not call the
// handler at all, let alone apply twice.
TEST_F(ClusterRecordHandoffTest, OnlyTheResolvedOwnerAppliesNotBoth) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setOwnedByChannelForTesting(TestKind, 100, 7);

	// A second orchestrator sharing the same fakes (as if a second process
	// shared the same DB/ownership-source state, which is the real-world
	// equivalent).
	ClusterRecordHandoff otherProcessHandoff { repository, resolver };

	RecordingHandler channelSevenHandler;
	RecordingHandler channelNineHandler;

	const auto transitionedByNine = otherProcessHandoff.sweep(TestKind, 9, 10, 2000, channelNineHandler);
	EXPECT_EQ(0, transitionedByNine);
	EXPECT_EQ(0, channelNineHandler.applyOwnedCallCount);

	const auto transitionedBySeven = handoff.sweep(TestKind, 7, 10, 2000, channelSevenHandler);
	EXPECT_EQ(1, transitionedBySeven);
	EXPECT_EQ(1, channelSevenHandler.applyOwnedCallCount);

	// A further sweep by either process must not re-apply (row is no longer PENDING).
	const auto secondPassBySeven = handoff.sweep(TestKind, 7, 10, 3000, channelSevenHandler);
	EXPECT_EQ(0, secondPassBySeven);
	EXPECT_EQ(1, channelSevenHandler.applyOwnedCallCount);
}

// 8. Stale ownership: a channel that no longer resolves as the owner (e.g.
// a relog moved the session elsewhere between enqueue and sweep) does not apply.
TEST_F(ClusterRecordHandoffTest, StaleOwnershipRefusesToApply) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setOwnedByChannelForTesting(TestKind, 100, 7);

	RecordingHandler handler;
	ASSERT_EQ(1, handoff.sweep(TestKind, 7, 10, 2000, handler));

	// Simulate a second, unrelated pending op for the same record after
	// ownership moved to channel 9 - channel 7 must not apply it even
	// though it applied the *previous* one moments earlier.
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-2", 100, 1500)));
	resolver.setOwnedByChannelForTesting(TestKind, 100, 9);

	const auto transitioned = handoff.sweep(TestKind, 7, 10, 3000, handler);
	EXPECT_EQ(0, transitioned);
	EXPECT_EQ(1, handler.applyOwnedCallCount); // unchanged from the first sweep
}

// 11. Retry of the same operation after the row is already APPLIED is a safe no-op.
TEST_F(ClusterRecordHandoffTest, SweepOfAlreadyAppliedRowIsNoOp) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setOwnedByChannelForTesting(TestKind, 100, 7);

	RecordingHandler handler;
	ASSERT_EQ(1, handoff.sweep(TestKind, 7, 10, 2000, handler));
	ASSERT_EQ(1, handler.applyOwnedCallCount);

	// findPendingForKind will not even return the row a second time (no
	// longer PENDING), so the handler must not be invoked again.
	const auto secondSweep = handoff.sweep(TestKind, 7, 10, 3000, handler);
	EXPECT_EQ(0, secondSweep);
	EXPECT_EQ(1, handler.applyOwnedCallCount);
}

// 12. Ownership cannot currently be confirmed (Unknown) - must defer, not
// guess NoLiveOwner. Mirrors the design doc's Redis-outage/DB-outage
// fail-closed requirement (§14 test 12/13) at the orchestration level.
TEST_F(ClusterRecordHandoffTest, UnknownOwnershipDefersRatherThanApplying) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setUnknownForTesting(TestKind, 100);

	RecordingHandler handler;
	const auto transitioned = handoff.sweep(TestKind, 7, 10, 2000, handler);

	EXPECT_EQ(0, transitioned);
	EXPECT_EQ(0, handler.applyOwnedCallCount);
	EXPECT_EQ(0, handler.applyUnownedCallCount);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Pending, row->status);
}

// NoLiveOwner routes to applyUnowned, not applyOwned, and any channel id
// may apply it (there is no "owner" to match against for this outcome).
TEST_F(ClusterRecordHandoffTest, NoLiveOwnerRoutesToApplyUnowned) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setNoLiveOwnerForTesting(TestKind, 100);

	RecordingHandler handler;
	const auto transitioned = handoff.sweep(TestKind, 42, 10, 2000, handler);

	EXPECT_EQ(1, transitioned);
	EXPECT_EQ(0, handler.applyOwnedCallCount);
	EXPECT_EQ(1, handler.applyUnownedCallCount);
}

// AlreadyHandled (the handler's own claim lost a race to another process)
// must not transition the row and must not be treated as a failure.
TEST_F(ClusterRecordHandoffTest, AlreadyHandledOutcomeLeavesRowUntouched) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setNoLiveOwnerForTesting(TestKind, 100);

	RecordingHandler handler;
	handler.unownedResult = ClusterRecordApplyResult { ClusterRecordApplyOutcome::AlreadyHandled, "" };

	const auto transitioned = handoff.sweep(TestKind, 42, 10, 2000, handler);
	EXPECT_EQ(0, transitioned);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Pending, row->status);
}

// A definitive business-level failure marks the row FAILED with the
// handler's reason, and does not attempt a further apply on the same sweep.
TEST_F(ClusterRecordHandoffTest, FailedDefinitivelyMarksRowFailedWithReason) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setOwnedByChannelForTesting(TestKind, 100, 7);

	RecordingHandler handler;
	handler.ownedResult = ClusterRecordApplyResult { ClusterRecordApplyOutcome::FailedDefinitively, "mailbox full" };

	const auto transitioned = handoff.sweep(TestKind, 7, 10, 2000, handler);
	EXPECT_EQ(1, transitioned);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Failed, row->status);
	EXPECT_EQ("mailbox full", row->lastError);
}

// 18. Manual recovery: markAbandoned moves a row out of the sweep's
// consideration set.
TEST_F(ClusterRecordHandoffTest, AbandonedRowIsNoLongerSwept) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	ASSERT_TRUE(repository.markAbandoned("op-1", 1500, "operator investigated, do not apply"));
	resolver.setOwnedByChannelForTesting(TestKind, 100, 7);

	RecordingHandler handler;
	const auto transitioned = handoff.sweep(TestKind, 7, 10, 2000, handler);

	EXPECT_EQ(0, transitioned);
	EXPECT_EQ(0, handler.applyOwnedCallCount);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Abandoned, row->status);
}

// A sweep for one record kind must not touch pending operations of a
// different kind (multi-tenancy of the same table across future consumers).
TEST_F(ClusterRecordHandoffTest, SweepOnlyConsidersItsOwnRecordKind) {
	auto houseRecord = makeRecord("op-house", 200, 1000);
	houseRecord.recordKind = "HOUSE";
	houseRecord.operationType = "REVOKE_HOUSE_OWNER";
	houseRecord.recordChannelId = 7;
	ASSERT_TRUE(handoff.enqueue(houseRecord));
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-mail", 100, 1000)));
	resolver.setOwnedByChannelForTesting(TestKind, 100, 7);

	RecordingHandler handler;
	const auto transitioned = handoff.sweep(TestKind, 7, 10, 2000, handler);

	EXPECT_EQ(1, transitioned);
	EXPECT_EQ("op-mail", handler.lastAppliedOperationId);
	const auto houseRow = repository.findByIdForTesting("op-house");
	ASSERT_TRUE(houseRow.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Pending, houseRow->status);
}

// 7 (concurrent variant). Real multiple threads, each modeling a separate
// process's own sweep, all racing to apply the *same* NoLiveOwner
// operation. A correctly-implemented handler (§4.11.2's own required
// transactional claim, simulated here with an atomic compare-and-swap)
// combined with ClusterRecordHandoff's markApplied "WHERE status =
// 'PENDING'" guard must together produce exactly one Applied outcome -
// every other racer must see AlreadyHandled, never a second Applied and
// never a lost operation. Mirrors ClusterLeaderElectionTest's own
// 16-thread concurrent-acquire race test.
namespace {
	class ClaimingHandler : public IClusterRecordOperationHandler {
	public:
		ClusterRecordApplyResult applyOwned(const ClusterPendingOperationRecord &) override {
			ADD_FAILURE() << "applyOwned should not be called for a NoLiveOwner record";
			return { ClusterRecordApplyOutcome::FailedDefinitively, "unexpected" };
		}

		ClusterRecordApplyResult applyUnowned(const ClusterPendingOperationRecord &) override {
			if (!claimed.exchange(true)) {
				appliedCount.fetch_add(1);
				return { ClusterRecordApplyOutcome::Applied, "" };
			}
			return { ClusterRecordApplyOutcome::AlreadyHandled, "" };
		}

		std::atomic<bool> claimed { false };
		std::atomic<int> appliedCount { 0 };
	};
} // namespace

TEST_F(ClusterRecordHandoffTest, ConcurrentSweepOfNoLiveOwnerRecordHasExactlyOneWinner) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setNoLiveOwnerForTesting(TestKind, 100);

	constexpr int racerCount = 16;
	ClaimingHandler handler;
	std::vector<std::thread> threads;
	std::vector<int32_t> transitionedByThread(racerCount, 0);
	std::atomic<int> readyCount { 0 };
	std::atomic<bool> go { false };

	for (int i = 0; i < racerCount; ++i) {
		threads.emplace_back([&, i] {
			readyCount.fetch_add(1);
			while (!go.load()) {
				std::this_thread::yield();
			}
			// Each thread simulates a different process's own channel id -
			// irrelevant for NoLiveOwner routing, but realistic.
			transitionedByThread[static_cast<std::size_t>(i)] = handoff.sweep(TestKind, 100 + i, 10, 2000, handler);
		});
	}

	while (readyCount.load() < racerCount) {
		std::this_thread::yield();
	}
	go.store(true);

	for (auto &thread : threads) {
		thread.join();
	}

	EXPECT_EQ(1, handler.appliedCount.load());

	int totalTransitioned = 0;
	for (const auto transitioned : transitionedByThread) {
		totalTransitioned += transitioned;
	}
	// Exactly one thread's sweep() call sees Applied (the winner);
	// AlreadyHandled outcomes do not count as transitioned.
	EXPECT_EQ(1, totalTransitioned);

	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Applied, row->status);
}

// enqueueAndTryApplyNow: this process is already the confirmed owner ->
// applies synchronously, in the same call, no sweep needed.
TEST_F(ClusterRecordHandoffTest, EnqueueAndTryApplyNowAppliesImmediatelyWhenThisProcessOwns) {
	resolver.setOwnedByChannelForTesting(TestKind, 100, 7);
	RecordingHandler handler;

	const auto outcome = handoff.enqueueAndTryApplyNow(makeRecord("op-1", 100, 1000), 7, 2000, handler);

	EXPECT_EQ(ClusterRecordHandoffOutcome::EnqueuedDurably, outcome);
	EXPECT_EQ(1, handler.applyOwnedCallCount);
	EXPECT_EQ(0, handler.applyUnownedCallCount);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Applied, row->status);
}

// enqueueAndTryApplyNow: no live owner anywhere -> applies synchronously via
// applyUnowned, same call, no sweep needed.
TEST_F(ClusterRecordHandoffTest, EnqueueAndTryApplyNowAppliesImmediatelyWhenNoLiveOwner) {
	resolver.setNoLiveOwnerForTesting(TestKind, 100);
	RecordingHandler handler;

	const auto outcome = handoff.enqueueAndTryApplyNow(makeRecord("op-1", 100, 1000), 7, 2000, handler);

	EXPECT_EQ(ClusterRecordHandoffOutcome::EnqueuedDurably, outcome);
	EXPECT_EQ(0, handler.applyOwnedCallCount);
	EXPECT_EQ(1, handler.applyUnownedCallCount);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Applied, row->status);
}

// enqueueAndTryApplyNow: owned by another channel -> row is created and left
// PENDING for that channel's own sweep; applyOwned is never called here
// (only the confirmed owner may call it).
TEST_F(ClusterRecordHandoffTest, EnqueueAndTryApplyNowDefersWhenAnotherChannelOwns) {
	resolver.setOwnedByChannelForTesting(TestKind, 100, 9);
	RecordingHandler handler;

	const auto outcome = handoff.enqueueAndTryApplyNow(makeRecord("op-1", 100, 1000), 7, 2000, handler);

	EXPECT_EQ(ClusterRecordHandoffOutcome::EnqueuedDurably, outcome);
	EXPECT_EQ(0, handler.applyOwnedCallCount);
	EXPECT_EQ(0, handler.applyUnownedCallCount);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Pending, row->status);
}

// enqueueAndTryApplyNow: ownership cannot currently be confirmed -> row is
// created and left PENDING, fail-closed, nothing attempted.
TEST_F(ClusterRecordHandoffTest, EnqueueAndTryApplyNowDefersWhenOwnershipUnknown) {
	resolver.setUnknownForTesting(TestKind, 100);
	RecordingHandler handler;

	const auto outcome = handoff.enqueueAndTryApplyNow(makeRecord("op-1", 100, 1000), 7, 2000, handler);

	EXPECT_EQ(ClusterRecordHandoffOutcome::EnqueuedDurably, outcome);
	EXPECT_EQ(0, handler.applyOwnedCallCount);
	EXPECT_EQ(0, handler.applyUnownedCallCount);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Pending, row->status);
}

// enqueueAndTryApplyNow: a real enqueue failure (e.g. DB unreachable) - no
// row exists, caller must not treat the source state as consumed.
TEST_F(ClusterRecordHandoffTest, EnqueueAndTryApplyNowReportsNotEnqueuedOnRepositoryFailure) {
	repository.setNextEnqueueSucceedsForTesting(false);
	RecordingHandler handler;

	const auto outcome = handoff.enqueueAndTryApplyNow(makeRecord("op-1", 100, 1000), 7, 2000, handler);

	EXPECT_EQ(ClusterRecordHandoffOutcome::NotEnqueued, outcome);
	EXPECT_EQ(0, handler.applyOwnedCallCount);
	EXPECT_EQ(0, handler.applyUnownedCallCount);
	EXPECT_FALSE(repository.findByIdForTesting("op-1").has_value());
}

// enqueueAndTryApplyNow: a definitive business failure on the synchronous
// attempt (e.g. mailbox full) - row is durably marked FAILED, but the
// caller must be told not to treat the source state as consumed.
TEST_F(ClusterRecordHandoffTest, EnqueueAndTryApplyNowReportsFailedDefinitivelyOnBusinessFailure) {
	resolver.setNoLiveOwnerForTesting(TestKind, 100);
	RecordingHandler handler;
	handler.unownedResult = ClusterRecordApplyResult { ClusterRecordApplyOutcome::FailedDefinitively, "mailbox full" };

	const auto outcome = handoff.enqueueAndTryApplyNow(makeRecord("op-1", 100, 1000), 7, 2000, handler);

	EXPECT_EQ(ClusterRecordHandoffOutcome::EnqueuedButFailedDefinitively, outcome);
	const auto row = repository.findByIdForTesting("op-1");
	ASSERT_TRUE(row.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Failed, row->status);
	EXPECT_EQ("mailbox full", row->lastError);
}

// enqueueAndTryApplyNow: duplicate operationId (idempotent replay) reports
// NotEnqueued and does not invoke the handler a second time - the original
// row (whatever state it's in) is left untouched.
TEST_F(ClusterRecordHandoffTest, EnqueueAndTryApplyNowRejectsDuplicateOperationId) {
	resolver.setNoLiveOwnerForTesting(TestKind, 100);
	RecordingHandler handler;

	const auto first = handoff.enqueueAndTryApplyNow(makeRecord("op-1", 100, 1000), 7, 2000, handler);
	ASSERT_EQ(ClusterRecordHandoffOutcome::EnqueuedDurably, first);
	ASSERT_EQ(1, handler.applyUnownedCallCount);

	const auto second = handoff.enqueueAndTryApplyNow(makeRecord("op-1", 100, 1000), 7, 3000, handler);
	EXPECT_EQ(ClusterRecordHandoffOutcome::NotEnqueued, second);
	EXPECT_EQ(1, handler.applyUnownedCallCount);
}

// Mail-specific "concurrent deliveries" scenario: two *different* mail
// operations (distinct operation_id, e.g. two separate senders on two
// different channels mailing the same fully-offline recipient at close to
// the same time) both go through enqueueAndTryApplyNow concurrently. This
// is distinct from the earlier same-row sweep race test - here, both
// operations are legitimate and *both* must be delivered; neither may be
// lost, and neither may silently overwrite the other (design doc's "no
// item loss / no item duplication" requirement for the mail consumer).
namespace {
	class CountingUnownedHandler : public IClusterRecordOperationHandler {
	public:
		ClusterRecordApplyResult applyOwned(const ClusterPendingOperationRecord &) override {
			ADD_FAILURE() << "applyOwned should not be called for a NoLiveOwner record";
			return { ClusterRecordApplyOutcome::FailedDefinitively, "unexpected" };
		}

		ClusterRecordApplyResult applyUnowned(const ClusterPendingOperationRecord &record) override {
			std::lock_guard<std::mutex> lock(mutex);
			deliveredOperationIds.push_back(record.operationId);
			return { ClusterRecordApplyOutcome::Applied, "" };
		}

		std::mutex mutex;
		std::vector<std::string> deliveredOperationIds;
	};
} // namespace

TEST_F(ClusterRecordHandoffTest, TwoDistinctConcurrentDeliveriesToSameOfflineRecipientBothSucceed) {
	resolver.setNoLiveOwnerForTesting(TestKind, 100);
	CountingUnownedHandler handler;

	std::thread senderA([&] {
		const auto outcome = handoff.enqueueAndTryApplyNow(makeRecord("op-a", 100, 1000), 7, 2000, handler);
		EXPECT_EQ(ClusterRecordHandoffOutcome::EnqueuedDurably, outcome);
	});
	std::thread senderB([&] {
		const auto outcome = handoff.enqueueAndTryApplyNow(makeRecord("op-b", 100, 1000), 9, 2000, handler);
		EXPECT_EQ(ClusterRecordHandoffOutcome::EnqueuedDurably, outcome);
	});
	senderA.join();
	senderB.join();

	// Both distinct mail items must have been delivered - neither lost,
	// neither silently dropped in favor of the other.
	ASSERT_EQ(2u, handler.deliveredOperationIds.size());
	EXPECT_NE(handler.deliveredOperationIds[0], handler.deliveredOperationIds[1]);

	const auto rowA = repository.findByIdForTesting("op-a");
	const auto rowB = repository.findByIdForTesting("op-b");
	ASSERT_TRUE(rowA.has_value());
	ASSERT_TRUE(rowB.has_value());
	EXPECT_EQ(ClusterPendingOperationStatus::Applied, rowA->status);
	EXPECT_EQ(ClusterPendingOperationStatus::Applied, rowB->status);
}

// 19. Single-channel compatibility is enforced entirely at the call site
// (no sweep is ever scheduled when multiChannelEnabled is false - PR 2's
// scope, see design doc §10) - here, confirm the orchestration itself has
// no implicit dependency on multichannel being enabled: it works
// correctly against a "channel 1" single-channel-shaped scenario too.
TEST_F(ClusterRecordHandoffTest, WorksCorrectlyForSingleChannelShapedIds) {
	ASSERT_TRUE(handoff.enqueue(makeRecord("op-1", 100, 1000)));
	resolver.setOwnedByChannelForTesting(TestKind, 100, 1);

	RecordingHandler handler;
	const auto transitioned = handoff.sweep(TestKind, 1, 10, 2000, handler);
	EXPECT_EQ(1, transitioned);
}
