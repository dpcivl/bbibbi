import unittest
from unittest.mock import MagicMock, patch
import paho.mqtt.client as mqtt

from legacy.mqtt_example import on_connect, on_subscribe, on_unsubscribe, on_message

class TestClient(unittest.TestCase):
        
    @patch("builtins.print")
    def test_on_subscribe_failure(self, mock_print):
        # Mock reason_code_list with a failure case
        client = MagicMock()
        reason_code_list = [MagicMock(is_failure=True, __str__=lambda x: "FailureReason")]

        # Call the on_subscribe function
        on_subscribe(client, None, None, reason_code_list, None)

        # Check if print was called with the expected failure message
        mock_print.assert_called_once_with("Broker rejected you subscription: FailureReason")

    @patch("builtins.print")
    def test_on_subscribe_success(self, mock_print):
        # Mock reason_code_list with a success case and QoS value
        client = MagicMock()
        reason_code_list = [MagicMock(is_failure=False, value=0)]

        # Call the on_subscribe function
        on_subscribe(client, None, None, reason_code_list, None)

        # Check if print was called with the expected success message
        mock_print.assert_called_once_with("Broker granted the following QoS: 0")
        
    @patch("builtins.print")
    def test_unsubscribe_success_no_reason_code(self, mock_print):
        # 성공적인 unsubscribe 경우로 reason_code_list가 비어 있을 때
        client = MagicMock()

        # Call the on_unsubscribe function
        on_unsubscribe(client, None, None, [], None)

        # Check if success message was printed and client.disconnect was called
        mock_print.assert_called_once_with("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
        client.disconnect.assert_called_once()
        
    @patch("builtins.print")
    def test_unsubscribe_success_with_reason_code(self, mock_print):
        # 성공적인 unsubscribe 경우로 reason_code_list의 첫 항목이 실패가 아닐 때
        client = MagicMock()
        reason_code_list = [MagicMock(is_failure=False)]

        # Call the on_unsubscribe function
        on_unsubscribe(client, None, None, reason_code_list, None)

        # Check if success message was printed and client.disconnect was called
        mock_print.assert_called_once_with("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
        client.disconnect.assert_called_once()

    @patch("builtins.print")
    def test_unsubscribe_failure(self, mock_print):
        # 실패하는 unsubscribe 경우로 reason_code_list의 첫 항목이 실패일 때
        client = MagicMock()
        reason_code_list = [MagicMock(is_failure=True, __str__=lambda x: "FailureReason")]

        # Call the on_unsubscribe function
        on_unsubscribe(client, None, None, reason_code_list, None)

        # Check if failure message was printed and client.disconnect was called
        mock_print.assert_called_once_with("Broker replied with failure: FailureReason")
        client.disconnect.assert_called_once()
        
    def test_on_message_adds_payload_to_userdata(self):
        # Arrange
        client = MagicMock()
        userdata = []
        message = MagicMock(payload=b"test_payload")

        # Act
        on_message(client, userdata, message)

        # Assert
        self.assertIn(b"test_payload", userdata)
        client.unsubscribe.assert_not_called()  # Should not unsubscribe for fewer than 10 messages

    def test_on_message_unsubscribes_after_10_messages(self):
        # Arrange
        client = MagicMock()
        userdata = [b"msg"] * 9  # 9 messages in userdata
        message = MagicMock(payload=b"test_payload")

        # Act
        on_message(client, userdata, message)

        # Assert
        self.assertIn(b"test_payload", userdata)
        self.assertEqual(len(userdata), 10)  # Check if userdata has exactly 10 messages
        client.unsubscribe.assert_called_once_with("$SYS/#")  # Should unsubscribe after reaching 10 messages

    @patch("builtins.print")
    def test_on_connect_failure(self, mock_print):
        # Mock reason_code with is_failure returning True
        client = MagicMock()
        reason_code = MagicMock(is_failure=True)

        # Call the on_connect function
        on_connect(client, None, None, reason_code, None)

        # Check if print was called with the expected failure message
        mock_print.assert_called_once_with(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
        client.subscribe.assert_not_called()  # Ensure subscribe is not called on failure

    def test_on_connect_success(self):
        # Mock reason_code with is_failure returning False
        client = MagicMock()
        reason_code = MagicMock(is_failure=False)

        # Call the on_connect function
        on_connect(client, None, None, reason_code, None)

        # Check if subscribe was called with the correct topic
        client.subscribe.assert_called_once_with("$SYS/#")
        
    