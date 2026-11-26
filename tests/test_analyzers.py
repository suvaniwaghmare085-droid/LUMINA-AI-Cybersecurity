import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from url_analyzer import analyze_url
from risk_engine import assess_risk

def test_url_http_flagged():
    result = analyze_url("http://192.0.2.10/login")
    assert result["heuristic_score"] > 0
    assert any("HTTP" in reason or "IP address" in reason for reason in result["signals"])

def test_https_normal_url_no_structural_flags():
    result = analyze_url("https://www.example.com/about")
    assert result["heuristic_score"] == 0

def test_risk_output_shape():
    result = assess_risk(url_result=analyze_url("http://192.0.2.10/login"))
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] in {"SAFE", "SUSPICIOUS", "HIGH RISK"}
    assert result["reasons"]
