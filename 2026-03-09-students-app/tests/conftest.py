"""
Shared pytest fixtures for all test files.
The live_server fixture starts the Flask app once per session in a background
thread so integration tests can hit real HTTP endpoints without needing a
manually-started server.
"""
import threading
import time

import pytest
import requests as req


@pytest.fixture(scope="session")
def live_server():
    from app.controller import students_app

    url = "http://127.0.0.1:5001"

    thread = threading.Thread(
        target=lambda: students_app.run(
            host="127.0.0.1",
            port=5001,
            use_reloader=False,
            debug=False,
        ),
        daemon=True,
    )
    thread.start()

    # wait up to 10 s for the server to accept connections
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            req.get(url, timeout=1)
            break
        except req.exceptions.ConnectionError:
            time.sleep(0.3)
    else:
        pytest.fail("Flask server did not start within 10 seconds")

    return url
