#!/usr/bin/env python3
"""
Docker entrypoint script for Solara application.
Handles proper IPython kernel context initialization in containerized environments.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_ipython_context():
    """Initialize IPython kernel context to prevent ContextVar errors."""
    try:
        # Import IPython components
        from IPython.core.application import BaseIPythonApplication
        from IPython.core.interactiveshell import InteractiveShell
        from traitlets.config import Config
        
        # Create a minimal IPython configuration
        config = Config()
        config.InteractiveShell.colors = 'NoColor'
        config.InteractiveShell.confirm_exit = False
        config.InteractiveShell.editor = 'nano'
        
        # Initialize the shell context
        if not BaseIPythonApplication.initialized():
            app = BaseIPythonApplication.instance()
            app.initialize([])
        
        # Ensure we have a shell instance
        if InteractiveShell.instance() is None:
            shell = InteractiveShell.instance(config=config)
            shell.init_create_namespaces()
        
        logger.info("IPython context initialized successfully")
        return True
        
    except Exception as e:
        logger.warning(f"Could not initialize IPython context: {e}")
        return False

def setup_jupyter_dirs():
    """Create and set up Jupyter directories."""
    dirs = [
        "/tmp/.ipython",
        "/tmp/.jupyter", 
        "/tmp/.local/share/jupyter",
        "/tmp/.local/share/jupyter/runtime"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
    logger.info("Jupyter directories created")

def main():
    """Main entrypoint function."""
    logger.info("Starting Solara application with Docker entrypoint")
    
    # Set up directories
    setup_jupyter_dirs()
    
    # Initialize IPython context
    setup_ipython_context()
    
    # Set environment variables for kernel management
    os.environ.setdefault("SOLARA_KERNEL_CULL_TIMEOUT", "0")
    os.environ.setdefault("SOLARA_KERNEL_CULL_INTERVAL", "0")
    os.environ.setdefault("JUPYTER_ENABLE_LAB", "no")
    
    # Import and run Solara
    try:
        import subprocess
        import sys
        
        cmd = [
            sys.executable, "-m", "solara", "run", 
            "frontend.main", 
            "--host", "0.0.0.0", 
            "--port", "8765"
        ]
        
        logger.info(f"Executing: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except Exception as e:
        logger.error(f"Failed to start Solara: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()