"""Image providers. A provider turns a shot into an image file.

For now images are made outside the pipeline and dropped into a folder,
named by shot id (m1-02.jpg). A real image API can replace FolderProvider
later as long as it has the same get() method.
"""
from pathlib import Path
from typing import Protocol

from studio.storyboard import Shot

EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


class MissingImages(Exception):
    pass


class ImageProvider(Protocol):
    def get(self, shot: Shot, prompt: str) -> Path | None:
        """Return the image path for this shot, or None if there is none yet."""


class FolderProvider:
    def __init__(self, folder: Path):
        self.folder = Path(folder)

    def get(self, shot: Shot, prompt: str) -> Path | None:
        for ext in EXTENSIONS:
            path = self.folder / f"{shot.id}{ext}"
            if path.exists():
                return path
        return None
