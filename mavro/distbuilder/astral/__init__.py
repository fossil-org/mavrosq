import os

class DistBuilder:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self.pyname: str = self.path.removesuffix(".mav") + ".py"
    def buildStdDist(self) -> None:
        from ...internal.build import build
        build(
            usage="python.exe",
            path=self.path,
            dist_path=self.pyname,
            no_delete=True,
            run=False
        )
        os.system(f"pyinstaller --onefile --upx-dir=upx --log-level ERROR --noconfirm --distpath . {self.pyname}")
        os.remove(self.pyname)
        os.remove(self.path.removesuffix(".mav") + ".spec")