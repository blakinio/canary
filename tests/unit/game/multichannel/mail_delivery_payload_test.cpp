/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/mail_delivery_payload.hpp"

#include <gtest/gtest.h>

TEST(MailDeliveryPayloadTest, RoundTripsAPlainParcel) {
	multichannel::MailDeliveryPayload payload;
	payload.itemId = 2595;
	payload.itemCount = 1;
	payload.itemAttributesHex = "deadbeef";

	const auto serialized = multichannel::serializeMailDeliveryPayload(payload);
	const auto parsed = multichannel::deserializeMailDeliveryPayload(serialized);

	ASSERT_TRUE(parsed.has_value());
	EXPECT_EQ(payload.itemId, parsed->itemId);
	EXPECT_EQ(payload.itemCount, parsed->itemCount);
	EXPECT_EQ("", parsed->writer);
	EXPECT_EQ(0, parsed->writtenDate);
	EXPECT_EQ("", parsed->text);
	EXPECT_EQ(payload.itemAttributesHex, parsed->itemAttributesHex);
}

TEST(MailDeliveryPayloadTest, RoundTripsAWrittenLetterWithSpecialCharacters) {
	multichannel::MailDeliveryPayload payload;
	payload.itemId = 2598;
	payload.itemCount = 1;
	payload.writer = "Player|With|Pipes";
	payload.writtenDate = 1752480000;
	payload.text = "Hello\nworld | pipe-separated | text with unicode: żółć";
	payload.itemAttributesHex = "cafebabe";

	const auto serialized = multichannel::serializeMailDeliveryPayload(payload);
	const auto parsed = multichannel::deserializeMailDeliveryPayload(serialized);

	ASSERT_TRUE(parsed.has_value());
	EXPECT_EQ(payload.writer, parsed->writer);
	EXPECT_EQ(payload.writtenDate, parsed->writtenDate);
	EXPECT_EQ(payload.text, parsed->text);
}

TEST(MailDeliveryPayloadTest, DelimiterInsideUserContentDoesNotCorruptOtherFields) {
	multichannel::MailDeliveryPayload payload;
	payload.itemId = 100;
	payload.itemCount = 5;
	payload.writer = "||||";
	payload.text = "|a|b|c|";
	payload.itemAttributesHex = "";

	const auto serialized = multichannel::serializeMailDeliveryPayload(payload);
	const auto parsed = multichannel::deserializeMailDeliveryPayload(serialized);

	ASSERT_TRUE(parsed.has_value());
	EXPECT_EQ(100, parsed->itemId);
	EXPECT_EQ(5, parsed->itemCount);
	EXPECT_EQ("||||", parsed->writer);
	EXPECT_EQ("|a|b|c|", parsed->text);
}

TEST(MailDeliveryPayloadTest, EmptyPayloadIsRejected) {
	EXPECT_FALSE(multichannel::deserializeMailDeliveryPayload("").has_value());
}

TEST(MailDeliveryPayloadTest, TooFewFieldsIsRejected) {
	EXPECT_FALSE(multichannel::deserializeMailDeliveryPayload("1|2|3").has_value());
}

TEST(MailDeliveryPayloadTest, TooManyFieldsIsRejected) {
	EXPECT_FALSE(multichannel::deserializeMailDeliveryPayload("1|2|3|4|5|6|7").has_value());
}

TEST(MailDeliveryPayloadTest, NonNumericItemIdIsRejected) {
	EXPECT_FALSE(multichannel::deserializeMailDeliveryPayload("notanumber|1||0||").has_value());
}

TEST(MailDeliveryPayloadTest, OddLengthHexFieldIsRejected) {
	// "abc" is an odd-length hex string in the writer field - malformed.
	EXPECT_FALSE(multichannel::deserializeMailDeliveryPayload("1|1|abc|0||").has_value());
}

TEST(MailDeliveryPayloadTest, DifferentInputsProduceDifferentSerializations) {
	multichannel::MailDeliveryPayload a;
	a.itemId = 1;
	multichannel::MailDeliveryPayload b;
	b.itemId = 2;
	EXPECT_NE(multichannel::serializeMailDeliveryPayload(a), multichannel::serializeMailDeliveryPayload(b));
}
