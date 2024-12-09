import subprocess

import pytest


def test_molsimplify_installation():
    """Test if molsimplify is installed and accessible"""
    result = subprocess.run(["which", "molsimplify"], capture_output=True, text=True)
    assert result.returncode == 0, "molsimplify not found in PATH"

    # Test basic molsimplify command
    test_command = "molsimplify -h"
    result = subprocess.run(test_command, shell=True, capture_output=True, text=True)
    assert result.returncode == 0, "molsimplify help command failed"


def test_xtb_installation():
    """Test if xtb is installed and accessible"""
    # Check if xtb executable exists
    result = subprocess.run(["which", "xtb"], capture_output=True, text=True)
    assert result.returncode == 0, "xtb not found in PATH"

    # Test basic xtb command
    test_command = "xtb --version"
    result = subprocess.run(test_command, shell=True, capture_output=True, text=True)
    assert result.returncode == 0, "xtb version command failed"


def test_basic_molsimplify_calculation(temp_output_dir):
    """Test basic molsimplify structure generation"""
    test_dir = temp_output_dir / "test_molsimplify"
    test_dir.mkdir(exist_ok=True)

    # Simple test case with a basic complex
    parameters = [
        "-skipANN", "True",
        "-core", "Pd",
        "-geometry", "sqp",
        "-lig", "NH3", "[Cl-]", "[Br-]", "NH3",
        "-coord", "4",
        "-ligocc", "1,1,1,1",
        "-rundir", f"'{test_dir}'",
    ]

    command = " ".join(["molsimplify", *parameters])
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    assert result.returncode == 0, "Basic molsimplify calculation failed"

    # Check if output files were generated
    xyz_files = list(test_dir.rglob("*.xyz"))
    assert len(xyz_files) > 0, "No XYZ files generated"


def test_basic_xtb_calculation(temp_output_dir):
    """Test basic xtb optimization"""
    # Create a simple water molecule XYZ file
    water_xyz = """3
    Water molecule
    O          0.00000        0.00000        0.11779
    H          0.00000        0.75545       -0.47116
    H          0.00000       -0.75545       -0.47116
    """

    xyz_file = temp_output_dir / "water.xyz"
    xyz_file.write_text(water_xyz)

    try:
        # Run basic xtb optimization
        command = f"cd {temp_output_dir} && xtb water.xyz --opt"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        assert result.returncode == 0, "Basic xtb calculation failed"

        # Check if output files were generated
        assert (temp_output_dir / "xtbopt.xyz").exists(), "No optimization output found"

    except Exception as e:
        pytest.fail(f"XTB calculation failed with error: {str(e)}")
