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

    basedir = Path(__file__).parent

    env_path = basedir / "test.env"
    config = dotenv_values(env_path)

    pydantic_path = basedir / "test.json"
    with pydantic_path.open("r") as f:
        content = f.read()
        pydtest = PydatenicTest.model_validate_json(content)

    sqlver = pymysql.version_info

    ports = serial.tools.list_ports.comports(include_links=False)
    names = [p.name for p in ports]

    cores = [1, 2, 4, 8, 16, 32]

    root = tk.Tk()
    root.title("pyinstaller-rpi-test")

    ttk.Label(root, text=f"{config=}").pack()
    ttk.Label(root, text=f"{pydtest=}").pack()
    ttk.Label(root, text=f"{sqlver=}").pack()
    ttk.Label(root, text=f"{names=}").pack()

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


if __name__ == "__main__":
    main()
