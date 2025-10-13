---
tags:
  - setup
  - installation
  - requirements
  - getting-started
---

# Installation

This guide will help you install and set up CulicidaeLab Server on your local machine or server environment.

## System Requirements

### Hardware Requirements

- **Processor (CPU):** Any modern x86-64 CPU
- **Memory (RAM):** Minimum 2 GB, 8 GB or more recommended for large datasets
- **Graphics Card (GPU):** NVIDIA GPU with CUDA support recommended for AI model operations (minimum 2 GB VRAM, 4 GB+ recommended)
- **Storage:** At least 10 GB of free space for installation, dependencies, and data

### Software Requirements

**Operating Systems (tested):**
- Windows 10/11
- Linux 22.04+

**Required Software:**
- Git
- Python 3.11
- uv 0.8.13 (recommended) or pip
- For Linux: `libgl1` package

## Installation Methods

### Method 1: Using uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager that provides better dependency resolution and faster installations.

1. **Install uv** (if not already installed):
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/iloncka-ds/culicidaelab-server.git
   cd culicidaelab-server
   ```

3. **Create virtual environment and install dependencies:**
   ```bash
   uv venv -p 3.11
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync -p 3.11
   uv pip install -e .
   uv cache clean
   ```

### Method 2: Using pip

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iloncka-ds/culicidaelab-server.git
   cd culicidaelab-server
   ```

2. **Create virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   python -m pip install -e .
   python -m pip cache purge
   ```

## Post-Installation Setup

### 1. Generate Sample Data

Create the JSON/GeoJSON files for initial database population:

```bash
python -m backend.data.sample_data.generate_sample_data
```

This creates sample files in the `sample_data/` directory including:
- `sample_species.json`
- `sample_observations.geojson`
- `sample_diseases.json`

### 2. Initialize Database

Set up LanceDB tables and populate them with sample data:

```bash
python -m backend.scripts.populate_lancedb
```

### 3. Verify Installation

Check if the database was populated successfully:

```bash
python -m backend.scripts.query_lancedb observations --limit 5
```

## Environment Configuration

### Backend Configuration

Create a `.env` file in the `backend/` directory with your configuration:

```bash
# Copy the example configuration
cp backend/.env.example backend/.env
```

Edit the `.env` file to match your environment settings.

### Frontend Configuration

The frontend configuration is handled in `frontend/config.py`. Review and modify as needed for your deployment.

## Troubleshooting

### Common Issues

**GPU/CUDA Issues:**
- Ensure NVIDIA drivers are installed and up to date
- Verify CUDA compatibility with your GPU
- For CPU-only operation, the system will automatically fall back

**Permission Issues on Linux:**
- Ensure you have proper permissions for the installation directory
- Install `libgl1` package: `sudo apt-get install libgl1-mesa-glx`

**Python Version Issues:**
- Ensure Python 3.11 is installed and active
- Use `python --version` to verify

**Memory Issues:**
- Increase system RAM or use smaller batch sizes
- Consider using CPU-only mode for lower memory usage

### Getting Help

If you encounter issues during installation:

1. Check the [GitHub Issues](https://github.com/iloncka-ds/culicidaelab-server/issues) for similar problems
2. Review the [troubleshooting guide](../user-guide/troubleshooting.md)
3. Join the discussion on [GitHub Discussions](https://github.com/iloncka-ds/culicidaelab-server/discussions)

## Next Steps

After successful installation, proceed to the [Quick Start Guide](quick-start.md) to learn how to run and use CulicidaeLab Server.