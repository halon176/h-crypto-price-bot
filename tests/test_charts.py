import pandas as pd

from src.handlers.cg_calls import _render_chart_image


def test_render_chart_image_returns_jpeg():
    df = pd.DataFrame({"timeframe": pd.date_range("2026-10-01", periods=48, freq="h"), "prices": range(48)})

    buffer = _render_chart_image(df, "Bitcoin (BTC)", "2 days chart", "dark", "bitcoin", "2")

    assert buffer.getvalue()[:2] == b"\xff\xd8"
