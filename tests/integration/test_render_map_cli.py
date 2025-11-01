"""Integration tests for render_map CLI."""
import subprocess
from pathlib import Path


def test_render_map_help() -> None:
    """Test render_map --help."""
    result = subprocess.run(
        ["uv", "run", "python", "examples/render_map.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "render_map.py" in result.stdout
    assert "--output-dir" in result.stdout


def test_render_map_basic(tmp_path: Path) -> None:
    """Test basic rendering of a save file."""
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        import pytest
        pytest.skip("Test save file not available")

    output_dir = tmp_path / "renders"

    result = subprocess.run(
        [
            "uv", "run", "python", "examples/render_map.py",
            str(save_path),
            "--output-dir", str(output_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_dir.exists()

    # Check that PNG files were created
    png_files = list(output_dir.glob("*.png"))
    assert len(png_files) > 0
