from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def configure_plotting(*, dpi: int = 300, font_size: int = 10, style: str = "whitegrid", palette: str = "husl") -> None:
    plt.style.use("seaborn-v0_8-darkgrid")
    sns.set_palette(palette)
    sns.set_style(style)
    plt.rcParams["figure.dpi"] = dpi
    plt.rcParams["font.size"] = font_size
