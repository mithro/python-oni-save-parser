"""Tests for pipeline orchestrator."""
from pathlib import Path

from oni_save_parser.rendering.pipeline import MapRenderer


def test_map_renderer_initialization() -> None:
    """Test creating a MapRenderer."""
    renderer = MapRenderer()
    assert renderer is not None


def test_render_save_to_png(tmp_path: Path) -> None:
    """Test end-to-end rendering of a save file."""
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        import pytest
        pytest.skip("Test save file not available")

    output_dir = tmp_path / "renders"
    renderer = MapRenderer()

    output_files = renderer.render(
        save_path=save_path,
        output_dir=output_dir,
        scale=2,
    )

    # Verify output files created
    assert len(output_files) > 0
    for file_path in output_files:
        assert Path(file_path).exists()
        assert Path(file_path).suffix == ".png"
