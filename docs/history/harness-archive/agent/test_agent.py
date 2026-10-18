import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from agent import agent as bridge


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.sessions = root / "sessions"
        self.ledger = root / "ledger"
        self.incidents = root / "incidents"
        self.sessions.mkdir()
        self.ledger.mkdir()
        self.incidents.mkdir()
        self.patches = [
            patch.object(bridge, "SESSIONS", self.sessions),
            patch.object(bridge, "LEDGER", self.ledger),
            patch.object(bridge, "INCIDENTS", self.incidents),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.temp.cleanup()

    def test_run_loop_preserves_full_history_and_ollama_tool_result_shape(self):
        session = bridge.Session("history-test")
        conversation = [
            {"role": "user", "content": "Start Gate 1"},
            {"role": "assistant", "content": "What problem should this solve?"},
            {"role": "user", "content": "Help users find files"},
        ]
        responses = [
            {"message": {"role": "assistant", "content": "", "tool_calls": [
                {"function": {"name": "read_file", "arguments": {"path": "MANUAL.md"}}}
            ]}},
            {"message": {"role": "assistant", "content": "", "tool_calls": [
                {"function": {"name": "respond", "arguments": {"message": "Done"}}}
            ]}},
        ]
        received = []

        def fake_call(messages, tools):
            received.append((copy.deepcopy(messages), copy.deepcopy(tools)))
            return responses.pop(0)

        with patch.object(bridge, "call_ollama_native", side_effect=fake_call):
            result = bridge.run_loop(session, conversation, 3, False)

        self.assertEqual(result, "Done")
        sent_messages = received[0][0]
        self.assertEqual(
            [(m["role"], m["content"]) for m in sent_messages[-3:]],
            [(m["role"], m["content"]) for m in conversation],
        )
        followup = received[1][0]
        tool_reply = next(m for m in followup if m.get("role") == "tool")
        self.assertEqual(tool_reply["tool_name"], "read_file")
        self.assertNotIn("name", tool_reply)

    def test_parser_fallback_uses_parser_args_attribute(self):
        session = bridge.Session("parser-test")
        parser_call = SimpleNamespace(
            name="respond", args={"arg0": {"message": "Parsed"}}
        )
        with (
            patch.object(bridge, "call_ollama_native", return_value={"message": {"content": "<tool-call>"}}),
            patch.object(bridge, "try_parse_tool_calls", return_value=[parser_call]),
        ):
            result = bridge.run_loop(
                session, [{"role": "user", "content": "hello"}], 1, False
            )
        self.assertEqual(result, "Parsed")

    def test_plan_writes_are_scoped_and_approval_status_requires_explicit_approval(self):
        repo = Path(self.temp.name) / "repo"
        plan = repo / "docs" / "plans" / "demo"
        plan.mkdir(parents=True)
        status = plan / "00-status.md"
        status.write_text("- Gate 1 — Product: pending\n")
        session = bridge.Session("write-test")
        session.set_plan_slug("demo")

        with patch.object(bridge, "REPO_ROOT", repo):
            result = bridge.execute_tool(
                "write_file",
                {"path": "docs/plans/demo/01-product.md", "content": "# Product"},
                session,
                False,
            )
            self.assertIn("wrote docs/plans/demo/01-product.md", result)

            updated_status = "- Gate 1 — Product: APPROVED 2026-10-17\n"
            result = bridge.execute_tool(
                "write_file",
                {"path": "docs/plans/demo/00-status.md", "content": updated_status},
                session,
                False,
            )
            self.assertTrue(result.startswith("ERROR:"))
            result = bridge.execute_tool(
                "write_file",
                {"path": "docs/plans/demo/00-status.md", "content": updated_status},
                session,
                True,
            )
            self.assertIn("wrote docs/plans/demo/00-status.md", result)

            result = bridge.execute_tool(
                "write_file",
                {"path": "docs/plans/demo/../../README.md", "content": "out"},
                session,
                False,
            )
            self.assertTrue(result.startswith("ERROR:"))

    def test_implementation_tools_require_gate_four_approval(self):
        repo = Path(self.temp.name) / "repo"
        plan = repo / "docs" / "plans" / "demo"
        plan.mkdir(parents=True)
        (plan / "00-status.md").write_text("- Gate 4 — Slice plan: APPROVED 2026-10-17\n")
        session = bridge.Session("gate-test")
        session.set_plan_slug("demo")
        with patch.object(bridge, "REPO_ROOT", repo):
            self.assertTrue(bridge._gate4_approved(session))
            self.assertFalse(bridge._allowlisted_command("git status; echo unsafe"))
            self.assertFalse(bridge._allowlisted_command("pytest -p malicious"))
            self.assertTrue(bridge._allowlisted_command("git diff --check"))

    def test_shell_tool_is_not_offered_before_gate_four_approval(self):
        names = [
            tool["function"]["name"]
            for tool in bridge.factory_tools(include_write=True, include_bash=False)
        ]
        self.assertNotIn("run_bash", names)

    def test_explicit_approval_requires_current_approval_prompt(self):
        self.assertTrue(bridge._is_explicit_approval([
            {"role": "assistant", "content": "Approve Gate 1, or what should change?"},
            {"role": "user", "content": "approve"},
        ]))
        self.assertFalse(bridge._is_explicit_approval([
            {"role": "assistant", "content": "What feature do you want?"},
            {"role": "user", "content": "yes"},
        ]))

    def test_endpoint_returns_full_history_and_stable_conversation_id(self):
        captured = []

        def fake_loop(session, conversation, _max_steps, _approval):
            captured.append((session.id, conversation))
            return "ok"

        messages = [
            {"role": "user", "content": "Start"},
            {"role": "assistant", "content": "Question"},
            {"role": "user", "content": "Answer"},
        ]
        with patch.object(bridge, "run_loop", side_effect=fake_loop):
            client = bridge.APP.test_client()
            first = client.post(
                "/v1/chat/completions",
                json={"messages": messages, "conversation_id": "conversation-123"},
            )
            second = client.post(
                "/v1/chat/completions",
                json={"messages": messages, "conversation_id": "conversation-123"},
            )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(captured[0][0], captured[1][0])
        self.assertEqual(captured[0][1], messages)
        self.assertEqual(first.json["conversation_id"], "conversation-123")

    def test_max_steps_returns_non_success_http_response(self):
        with patch.object(bridge, "run_loop", side_effect=RuntimeError("max steps")):
            response = bridge.APP.test_client().post(
                "/v1/chat/completions",
                json={"messages": [{"role": "user", "content": "hello"}],
                      "conversation_id": "max-steps-test"},
            )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json["error"]["type"], "agent_error")

    def test_unstructured_model_responses_stop_at_retry_limit(self):
        session = bridge.Session("retry-test")
        conversation = [{"role": "user", "content": "hello"}]
        with (
            patch.object(bridge, "call_ollama_native", return_value={"message": {"content": "plain text"}}) as call,
            patch.dict(bridge.CONFIG, {"max_retries": 2, "trust_text_when_tools_present": False}),
            self.assertRaisesRegex(RuntimeError, "did not call a tool after 2 attempts"),
        ):
            bridge.run_loop(session, conversation, 25, False)
        self.assertEqual(call.call_count, 2)


if __name__ == "__main__":
    unittest.main()
