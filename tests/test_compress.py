from pathlib import Path
from up2b.up2b_lib.compress import Compressor


class TestCompress:
    def test_compress(self):
        compressor = Compressor(2 * 1024 * 1024)
        compressed_path = compressor(Path("/Users/thepoy/Downloads/day.jpg"))
        assert isinstance(compressed_path, Path)
