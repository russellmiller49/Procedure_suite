"""Tests for Responses API output parsing.

These focus on newer Responses API shapes where assistant text blocks may be
typed as "output_text" (not just "text"), and ensure prompt-echo "input_text"
blocks are ignored.
"""

from __future__ import annotations

from app.common.openai_responses import (
    parse_responses_json_object,
    parse_responses_text,
)


def test_parse_message_output_text_block() -> None:
    resp = {
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": '{"ok": true}'}],
            }
        ]
    }
    assert parse_responses_text(resp) == '{"ok": true}'
    assert parse_responses_json_object(resp) == {"ok": True}


def test_parse_falls_back_when_output_text_empty() -> None:
    resp = {
        "output_text": "",
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": '{"x": 1}'}],
            }
        ],
    }
    assert parse_responses_text(resp) == '{"x": 1}'


def test_ignores_input_text_echo() -> None:
    resp = {
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "input_text", "text": "Return JSON..."},
                    {"type": "output_text", "text": '{"y": 2}'},
                ],
            }
        ]
    }
    assert parse_responses_text(resp) == '{"y": 2}'

