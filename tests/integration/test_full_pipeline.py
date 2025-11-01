"""Integration tests for the complete rendering pipeline."""
from pathlib import Path

import pytest
from PIL import Image

from oni_save_parser.rendering.pipeline import MapRenderer


@pytest.fixture
def test_save_file() -> Path:
    """Get the path to a test save file."""
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        pytest.skip("Test save file not available")
    return save_path


@pytest.fixture
def renderer() -> MapRenderer:
    """Create a MapRenderer instance."""
    return MapRenderer()


def test_full_pipeline_basic(
    renderer: MapRenderer,
    test_save_file: Path,
    tmp_path: Path,
) -> None:
    """Test complete pipeline with real save file."""
    output_dir = tmp_path / "renders"

    # Run the full pipeline
    output_files = renderer.render(
        save_path=test_save_file,
        output_dir=output_dir,
        scale=2,
    )

    # Verify files were created
    assert len(output_files) > 0, "No output files were created"
    assert output_dir.exists(), "Output directory was not created"

    # Verify each output file
    for output_file in output_files:
        output_path = Path(output_file)
        assert output_path.exists(), f"Output file not found: {output_file}"
        assert output_path.suffix == ".png", f"Wrong file type: {output_file}"

        # Verify it's a valid PNG image
        with Image.open(output_path) as img:
            assert img.mode == "RGB", f"Wrong image mode: {img.mode}"
            assert img.width > 0, "Image has zero width"
            assert img.height > 0, "Image has zero height"


def test_full_pipeline_multiple_scales(
    renderer: MapRenderer,
    test_save_file: Path,
    tmp_path: Path,
) -> None:
    """Test pipeline with different scale values."""
    for scale in [1, 2, 4]:
        output_dir = tmp_path / f"scale_{scale}"

        output_files = renderer.render(
            save_path=test_save_file,
            output_dir=output_dir,
            scale=scale,
        )

        assert len(output_files) > 0
        # Check that scaling is applied correctly
        output_path = Path(output_files[0])
        with Image.open(output_path) as img:
            # Width should be proportional to scale
            # (We don't know exact dimensions, but should be divisible)
            assert img.width % scale == 0, f"Width not aligned to scale {scale}"
            assert img.height % scale == 0, f"Height not aligned to scale {scale}"


def test_full_pipeline_output_naming(
    renderer: MapRenderer,
    test_save_file: Path,
    tmp_path: Path,
) -> None:
    """Test that output filenames follow the expected pattern."""
    output_dir = tmp_path / "renders"

    output_files = renderer.render(
        save_path=test_save_file,
        output_dir=output_dir,
    )

    assert len(output_files) > 0

    # Check filename pattern
    for output_file in output_files:
        filename = Path(output_file).name
        # Should contain colony name, cycle, and asteroid info
        assert "cycle-" in filename, f"Missing cycle in filename: {filename}"
        assert "asteroid-" in filename, f"Missing asteroid in filename: {filename}"
        assert filename.endswith(".png"), f"Wrong extension: {filename}"


def test_full_pipeline_multiple_asteroids(
    renderer: MapRenderer,
    tmp_path: Path,
) -> None:
    """Test rendering a save with multiple asteroids if available."""
    # Try to find a save file with multiple asteroids
    # Using mid-game save which likely has more asteroids
    save_path = Path("test_saves/02-mid-game-cycle-148.sav")
    if not save_path.exists():
        pytest.skip("Multi-asteroid test save file not available")

    output_dir = tmp_path / "multi_asteroid"

    output_files = renderer.render(
        save_path=save_path,
        output_dir=output_dir,
    )

    # Should have at least one asteroid
    assert len(output_files) >= 1, "No asteroids were rendered"

    # All files should be valid
    for output_file in output_files:
        assert Path(output_file).exists()


def test_full_pipeline_consistency(
    renderer: MapRenderer,
    test_save_file: Path,
    tmp_path: Path,
) -> None:
    """Test that rendering the same save twice produces identical results."""
    output_dir_1 = tmp_path / "run1"
    output_dir_2 = tmp_path / "run2"

    # Render twice
    files_1 = renderer.render(test_save_file, output_dir_1)
    files_2 = renderer.render(test_save_file, output_dir_2)

    # Should produce same number of files
    assert len(files_1) == len(files_2)

    # Compare each pair of images
    for file_1, file_2 in zip(sorted(files_1), sorted(files_2)):
        with Image.open(file_1) as img_1, Image.open(file_2) as img_2:
            # Same dimensions
            assert img_1.size == img_2.size
            # Same pixel data
            assert list(img_1.getdata()) == list(img_2.getdata())


def test_pipeline_handles_invalid_save(
    renderer: MapRenderer,
    tmp_path: Path,
) -> None:
    """Test that pipeline handles invalid save files gracefully."""
    # Create a fake save file
    invalid_save = tmp_path / "invalid.sav"
    invalid_save.write_text("This is not a valid save file")

    output_dir = tmp_path / "output"

    # Should raise an exception (not crash)
    with pytest.raises(Exception):
        renderer.render(invalid_save, output_dir)
