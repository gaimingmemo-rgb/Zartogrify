import os
import glob

class PCScanner:
    def __init__(self):
        self.indexed_apps = {}

    def scan_installed_apps(self) -> dict:
        search_paths = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%ALLUSERSPROFILE%\Microsoft\Windows\Start Menu\Programs")
        ]
        found = {}
        for path in search_paths:
            if os.path.exists(path):
                for lnk in glob.glob(os.path.join(path, "**", "*.lnk"), recursive=True):
                    name = os.path.basename(lnk).replace(".lnk", "")
                    found[name] = lnk
        self.indexed_apps = found
        return found
