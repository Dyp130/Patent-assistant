#!/usr/bin/env python
"""Entry point for the Patent Drafting Assistant."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import get_settings

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    print(f"启动 {settings.app_name} v{settings.app_version}")
    print(f"访问地址: http://{settings.host}:{settings.port}")
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
