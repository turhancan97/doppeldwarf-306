"""The pretraining-family forest plot (AGENTS.md section 7.17)."""

from pathlib import Path

import pytest

from krasnal_id.config import backbone_config
from krasnal_id.viz.embedding_plot import VisualizationError
from krasnal_id.viz.family_plot import (
    FAMILIES,
    MODEL_LABEL,
    PANELS,
    Estimate,
    by_accuracy,
    collect,
    rows,
)


def test_every_model_is_a_packaged_backbone_in_exactly_one_family() -> None:
    models = [model for _, members in FAMILIES for model in members]
    assert len(models) == len(set(models)) == len(MODEL_LABEL) == 13
    for model in models:
        assert backbone_config(model).name == model


def test_rows_put_each_heading_above_its_members() -> None:
    laid_out = rows()
    assert laid_out[0] == ("Joint-embedding", None)
    assert laid_out[1:4] == [(None, "dino"), (None, "dinov2"), (None, "dinov3")]
    assert sum(family is not None for family, _ in laid_out) == len(FAMILIES)


def test_paradigms_and_their_models_are_ordered_by_top_1_best_first() -> None:
    scores = {"a": 80.0, "b": 95.0, "c": 90.0, "d": 90.0}
    estimates = {(model, "top_1"): Estimate(value, None, None) for model, value in scores.items()}
    families = (("First", ("a", "b")), ("Second", ("c",)), ("Third", ("d",)))
    ordered = by_accuracy(estimates, families)
    # The best model leads its paradigm, the best paradigm leads the figure, and a tie
    # keeps the order the paradigms were given in.
    assert ordered == [("First", ("b", "a")), ("Second", ("c",)), ("Third", ("d",))]
    assert rows(ordered)[:3] == [("First", None), (None, "b"), (None, "a")]


def test_right_is_better_in_every_panel() -> None:
    # Only the photographer effect is better when smaller, so only it is reversed.
    assert [panel.suffix for panel in PANELS if panel.reverse] == ["photographer_attributable"]
    assert all(panel.title and panel.unit for panel in PANELS)


def test_a_missing_estimate_is_refused_and_present_ones_are_scaled() -> None:
    metrics = {
        f"dinov2_{panel.suffix}": {"value": 0.5, "lower_bound": 0.4, "upper_bound": None}
        for panel in PANELS
    }
    found = collect(metrics, ["dinov2"])
    top_1 = found[("dinov2", "top_1")]
    assert (top_1.value, top_1.low, top_1.high) == (50.0, 40.0, None)
    assert found[("dinov2", "reject_margin_auroc")].value == 0.5
    with pytest.raises(VisualizationError, match="no clip_top_1"):
        collect(metrics, ["clip"])


def test_the_figure_renders_from_a_complete_artifact(tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")
    from krasnal_id.viz import figure_style as style
    from krasnal_id.viz.family_plot import render_family_figure

    metrics = {
        f"{model}_{panel.suffix}": {"value": 0.1, "lower_bound": 0.05, "upper_bound": 0.15}
        for model in MODEL_LABEL
        for panel in PANELS
    }
    path = render_family_figure(metrics, tmp_path / "family.png", style.CVWW.full, dpi=72)
    assert path.stat().st_size > 0
