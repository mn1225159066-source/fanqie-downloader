import os
import sys

def get_desktop_path():
    """
    获取当前系统的“桌面”目录，尽量可靠。
    - Windows：优先使用 OneDrive 的桌面（支持中文“桌面”），否则使用 USERPROFILE 下的 Desktop/桌面。
    - 其他系统：使用 ~/Desktop。
    若均不存在，回退到“文档”或用户主目录。
    """
    try:
        home = os.path.expanduser("~")
        candidates = []

        if sys.platform.startswith("win"):
            # 可能存在的 OneDrive 变量（家庭/商业版）
            one_candidates = [
                os.environ.get("OneDrive"),
                os.environ.get("OneDriveConsumer"),
                os.environ.get("OneDriveCommercial"),
            ]
            one_candidates = [p for p in one_candidates if p]
            # 有些机器是 OneDrive - 公司名
            userprofile = os.environ.get("USERPROFILE", home)
            potential_onedrives = []
            # 默认 OneDrive 根
            potential_onedrives.extend(one_candidates)
            # 兼容 OneDrive - * 目录
            try:
                for name in os.listdir(userprofile):
                    if name.lower().startswith("onedrive"):
                        potential_onedrives.append(os.path.join(userprofile, name))
            except Exception:
                pass

            # OneDrive 下的 Desktop/桌面
            for od in potential_onedrives:
                candidates.append(os.path.join(od, "Desktop"))
                candidates.append(os.path.join(od, "桌面"))

            # 用户目录下的 Desktop/桌面
            candidates.append(os.path.join(userprofile, "Desktop"))
            candidates.append(os.path.join(userprofile, "桌面"))
            candidates.append(os.path.join(home, "Desktop"))
            candidates.append(os.path.join(home, "桌面"))
        else:
            candidates.append(os.path.join(home, "Desktop"))

        for p in candidates:
            if p and os.path.isdir(p):
                return p

        # 回退：文档目录
        docs_candidates = [
            os.path.join(home, "Documents"),
            os.path.join(home, "文档"),
        ]
        for d in docs_candidates:
            if os.path.isdir(d):
                return d
        return home
    except Exception:
        return os.path.expanduser("~")

def get_documents_path():
    """
    获取“文档”目录路径（跨平台）。
    - Windows：优先 OneDrive 的 Documents/文档；否则 USERPROFILE 下的 Documents/文档；再否则 ~/Documents/文档。
    - 其他系统：~/Documents。
    若不存在则回退到用户主目录。
    """
    try:
        home = os.path.expanduser("~")
        candidates = []

        if sys.platform.startswith("win"):
            userprofile = os.environ.get("USERPROFILE", home)
            one_candidates = [
                os.environ.get("OneDrive"),
                os.environ.get("OneDriveConsumer"),
                os.environ.get("OneDriveCommercial"),
            ]
            one_candidates = [p for p in one_candidates if p]
            potential_onedrives = []
            potential_onedrives.extend(one_candidates)
            try:
                for name in os.listdir(userprofile):
                    if name.lower().startswith("onedrive"):
                        potential_onedrives.append(os.path.join(userprofile, name))
            except Exception:
                pass

            for od in potential_onedrives:
                candidates.append(os.path.join(od, "Documents"))
                candidates.append(os.path.join(od, "文档"))

            # 用户目录下的 Documents/文档
            candidates.append(os.path.join(userprofile, "Documents"))
            candidates.append(os.path.join(userprofile, "文档"))
            candidates.append(os.path.join(home, "Documents"))
            candidates.append(os.path.join(home, "文档"))
        else:
            candidates.append(os.path.join(home, "Documents"))

        for p in candidates:
            if p and os.path.isdir(p):
                return p
        return home
    except Exception:
        return os.path.expanduser("~")
