from unittest.mock import patch

from app.services.briefing_service import OllamaBriefingService


def test_generate_briefing_sends_race_facts_to_ollama():
    race_analysis = {
        "race": {"year": 2024, "name": "Bahrain Grand Prix"},
        "winner": "Max Verstappen",
    }

    with patch("app.services.briefing_service.httpx.post") as post:
        post.return_value.json.return_value = {
            "response": "Verstappen wins in Bahrain."
        }

        briefing = OllamaBriefingService().generate_briefing(race_analysis)

    assert briefing == "Verstappen wins in Bahrain."
    post.assert_called_once()

    request = post.call_args
    assert request.args[0].endswith("/api/generate")
    assert request.kwargs["json"]["stream"] is False
    assert "Max Verstappen" in request.kwargs["json"]["prompt"]
