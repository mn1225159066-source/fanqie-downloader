import os
import sys

def get_desktop_path():
    """
    Returns a reliable Desktop directory path on the current OS.
    On Windows, prefers OneDrive Desktop if enabled; otherwise uses USERPROFILE/Desktop.
    Falls back to Documents or home when Desktop is unavailable.
    """
    try:
        home = os.path.expanduser("~")
        candidates = []

        if sys.platform.startswith("win"):
            onedrive = os.environ.get("OneDrive")
            if onedrive:
                candidates.append(os.path.join(onedrive, "Desktop"))

            userprofile = os.environ.get("USERPROFILE", home)
            candidates.append(os.path.join(userprofile, "Desktop"))
            candidates.append(os.path.join(home, "Desktop"))
        else:
            candidates.append(os.path.join(home, "Desktop"))

        for p in candidates:
            if p and os.path.isdir(p):
                return p

        docs = os.path.join(home, "Documents")
        if os.path.isdir(docs):
            return docs
        return home
    except Exception:
        return os.path.expanduser("~")

