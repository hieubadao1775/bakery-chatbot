import argparse
import json
import uuid
from urllib import error, request


def call_chat_api(api_url: str, user_id: str, chat_session_id: str, new_query: str, timeout: int = 30):
    payload = {
        "user_id": user_id,
        "chat_session_id": chat_session_id,
        "new_query": new_query,
    }

    req = request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body)


def run_terminal_chat(api_url: str, user_id: str, chat_session_id: str):
    print(f"API URL: {api_url}")
    print(f"user_id: {user_id}")
    print(f"chat_session_id: {chat_session_id}")
    print("Type your message and press Enter.")
    print("Commands: /exit to quit, /new to start a new session id")
    print("-" * 70)

    turn = 1
    while True:
        query = input(f"[Turn {turn}] You: ").strip()

        if not query:
            print("Please enter a non-empty message.")
            continue
        if query.lower() == "/exit":
            print("Chat ended.")
            break
        if query.lower() == "/new":
            chat_session_id = f"demo_session_{uuid.uuid4().hex[:8]}"
            print(f"Started new chat_session_id: {chat_session_id}")
            print("-" * 70)
            turn = 1
            continue

        try:
            status_code, response_json = call_chat_api(
                api_url=api_url,
                user_id=user_id,
                chat_session_id=chat_session_id,
                new_query=query,
            )
            answer = response_json.get("answer", "<missing answer>")
            print(f"[Turn {turn}] HTTP {status_code}")
            print(f"[Turn {turn}] Bot: {answer}")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            print(f"[Turn {turn}] HTTPError: {exc.code} {exc.reason}")
            print(f"[Turn {turn}] Detail   : {detail}")
            continue
        except error.URLError as exc:
            print(f"[Turn {turn}] Cannot connect to API: {exc}")
            print("Hint: start server with 'uvicorn api.main:app --reload --port 8000'")
            break
        except Exception as exc:
            print(f"[Turn {turn}] Unexpected error: {exc}")
            break

        print("-" * 70)
        turn += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive terminal client for POST /chat API")
    parser.add_argument("--url", default="http://127.0.0.1:8000/chat", help="Chat API URL")
    parser.add_argument("--user", default="demo_user", help="user_id to send")
    parser.add_argument(
        "--session",
        default=f"demo_session_{uuid.uuid4().hex[:8]}",
        help="initial chat_session_id",
    )

    args = parser.parse_args()
    run_terminal_chat(api_url=args.url, user_id=args.user, chat_session_id=args.session)
