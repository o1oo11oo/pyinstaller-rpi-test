import platform
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import matplotlib.pyplot as plt
import mplcursors
import pymysql
import serial.tools.list_ports
from dotenv import dotenv_values
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pydantic import BaseModel


class PydatenicTest(BaseModel):
    test: str


def main():
    print("Hello from pyinstaller-rpi-test!")

    executable, bundle, base, local = local_config_path("local.json")

    env_path = resource_path("test.env")
    config = dotenv_values(env_path)

    pydantic_path = resource_path("test.json")
    with pydantic_path.open("r") as f:
        content = f.read()
        pydtest = PydatenicTest.model_validate_json(content)

    sqlver = pymysql.version_info

    ports = serial.tools.list_ports.comports(include_links=False)
    names = [p.name for p in ports]

    picotool, kind = find_picotool()
    if picotool:
        result = subprocess.run(
            [str(picotool), "version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version = result.stdout.strip()
        version += f" ({kind})"
    else:
        version = "No picotool binary found"

    cores = [1, 2, 4, 8, 16, 32]

    root = tk.Tk()
    root.title("pyinstaller-rpi-test")

    ttk.Label(root, text=f"{executable=}").pack()
    ttk.Label(root, text=f"{bundle=}").pack()
    ttk.Label(root, text=f"{base=}").pack()
    ttk.Label(root, text=f"{local=}").pack()
    ttk.Label(root, text=f"{config=}").pack()
    ttk.Label(root, text=f"{pydtest=}").pack()
    ttk.Label(root, text=f"{sqlver=}").pack()
    ttk.Label(root, text=f"{names=}").pack()
    ttk.Label(root, text=f"{version=}").pack()

    plot_frame = ttk.Frame(root)
    plot_frame.pack()
    figure = plt.Figure(dpi=100, layout="constrained")
    ax = figure.add_subplot(111)
    ax.set_title("AMD")
    ax.set_xlabel("Cores")
    ax.set_ylabel("Cores")
    ax.plot(cores)
    canvas = FigureCanvasTkAgg(figure, plot_frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    cursor = mplcursors.cursor(ax, hover=mplcursors.HoverMode.Transient)
    cursor.connect(
        "add",
        lambda sel: sel.annotation.set_text(
            f"cores[int(round({sel.index}))]={cores[int(round(sel.index))]}"
        ),
    )

    root.mainloop()


def local_config_path(
    relative: str | Path | None = None,
) -> tuple[Path | None, Path | None, Path, Path]:
    """
    Return absolute path to config, whether running
    from source or from a PyInstaller bundle.
    """
    executable = None
    bundle = None

    if getattr(sys, "frozen", False):
        executable = Path(sys.executable).resolve()

        # check for macOS bundle
        if platform.system() == "Darwin":
            bundle = executable.parent.parent.parent

            if bundle.exists() and bundle.name.endswith(".app"):
                base = bundle.parent
            else:
                base = executable.parent
        else:
            base = executable.parent
    else:
        base = Path(__file__).resolve().parent

    res = base / relative if relative else base

    return (executable, bundle, base, res)


def resource_path(relative: str | Path) -> Path:
    """
    Return absolute path to resource, whether running
    from source or from a PyInstaller bundle.
    """
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent

    return base / relative


def find_picotool() -> tuple[Path | None, str]:
    exe_name = "picotool.exe" if platform.system() == "Windows" else "picotool"

    # 1) Bundled (PyInstaller or local assets/)
    bundled = resource_path(Path("assets") / "picotool" / exe_name)
    if bundled.exists() and bundled.is_file():
        return (bundled, "bundled")

    # 2) On PATH
    path_tool = shutil.which("picotool")
    if path_tool:
        return (Path(path_tool), "system")

    # 3) Optional: local project root (dev convenience)
    local = Path.cwd() / exe_name
    if local.exists():
        return (local, "local")

    return (None, "not found")


if __name__ == "__main__":
    main()
