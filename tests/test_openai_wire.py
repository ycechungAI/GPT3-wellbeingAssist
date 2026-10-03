"""Run llm.py through the real OpenAI SDK (as used for OpenRouter) against a local fake server.

The other tests replace the client entirely; this one checks the actual request the SDK
sends and that we parse a real Chat Completions response.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from openai import OpenAI

import llm


@pytest.fixture
def server():
    replies: list[str] = []
    requests: list[dict] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append({"path": self.path, "auth": self.headers["Authorization"], **body})
            payload = json.dumps(
                {
                    "id": f"chatcmpl-{len(requests)}",
                    "object": "chat.completion",
                    "created": 0,
                    "model": body["model"],
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "stop",
                            "message": {"role": "assistant", "content": replies.pop(0)},
                        }
                    ],
                }
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    client = OpenAI(api_key="test-key", base_url=f"http://127.0.0.1:{httpd.server_port}/v1")
    yield client, replies, requests
    httpd.shutdown()


def test_full_checkin_over_the_wire(server):
    client, replies, requests = server
    replies += [
        "Yes",
        "Do you also have a fever?",
        "Yes",
        '{"symptoms": [{"symptom": "Cough", "when": "Unknown"}, '
        '{"symptom": "Fever", "when": "Yesterday"}]}',
    ]

    assert llm.is_unwell(client, "I have a dry cough") is True
    question = llm.next_question(client, "I have a dry cough")
    assert question == "Do you also have a fever?"
    assert llm.answered_question(client, question, "Yes, since yesterday") is True
    assert llm.extract_symptoms(client, "I have a dry cough\nYes, since yesterday") == [
        {"symptom": "Cough", "when": "Unknown"},
        {"symptom": "Fever", "when": "Yesterday"},
    ]

    assert [r["path"] for r in requests] == ["/v1/chat/completions"] * 4
    assert all(r["auth"] == "Bearer test-key" for r in requests)
    assert requests[0]["model"] == llm.MODEL and requests[0]["temperature"] == 0
    assert requests[0]["messages"][1] == {"role": "user", "content": "I have a dry cough"}
    assert requests[3]["response_format"] == {"type": "json_object"}
