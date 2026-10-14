"""
Nombre: results
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-10
Descripción: Genera y guarda los resultados de rendimiento de las
implementaciones secuencial y paralela 
"""

import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # sin ventana: solo guarda los archivos
import matplotlib.pyplot as plt
import numpy as np
import csv  


def _base_name(rows, cols, procs):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"tiempos_{rows}x{cols}_np{procs}_{stamp}"


def _save_steps_plot(times_seq, times_par, rows, cols, procs, base):
    """Guarda la gráfica de tiempo por paso: secuencial vs paralelo."""
    steps = range(1, len(times_seq) + 1)
    plt.figure(figsize=(10, 5))
    plt.plot(steps, times_seq, label="Secuencial", color="tab:red")
    plt.plot(steps, times_par, label="Paralelo (MPI)", color="tab:green")
    plt.xlabel("Paso")
    plt.ylabel("Tiempo (ms)")
    plt.title(f"Tiempo por generación - matriz {rows}x{cols} - {procs} procesos")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(base + "_tiempo_por_paso.png", dpi=150)
    plt.close()


def _save_summary_table(times_seq, times_par, rows, cols, procs, base):
    """Guarda la tabla comparativa (promedio, desv., mín, máx, speedup) como imagen."""
    seq = np.array(times_seq)
    par = np.array(times_par)

    ddof = 1 if len(seq) > 1 else 0  # desv. muestral; evita NaN con un solo paso
    mean_seq, std_seq = seq.mean(), seq.std(ddof=ddof)
    mean_par, std_par = par.mean(), par.std(ddof=ddof)
    speedup = mean_seq / mean_par

    cell_text = [
        ["Secuencial", f"{mean_seq:.3f}", f"{std_seq:.3f}",
         f"{seq.min():.3f}", f"{seq.max():.3f}"],
        ["Paralelo (MPI)", f"{mean_par:.3f}", f"{std_par:.3f}",
         f"{par.min():.3f}", f"{par.max():.3f}"],
        ["Speedup", f"{speedup:.2f}x", "-", "-", "-"],
    ]

    fig, ax = plt.subplots(figsize=(8, 2.6))
    ax.axis("off")
    table = ax.table(
        cellText=cell_text,
        colLabels=["Motor", "Promedio (ms)", "Desv. est. (ms)", "Mín (ms)", "Máx (ms)"],
        loc="center", cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.8)
    ax.set_title(f"matriz {rows}x{cols} - {procs} procesos - {len(seq)} pasos")
    fig.tight_layout()
    fig.savefig(base + "_tabla_comparativa.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def save_results(times_seq, times_par, rows, cols, procs, folder="resultados"):
    """Guarda la gráfica por paso y la tabla comparativa como archivos PNG."""
    if not times_seq:
        return

    os.makedirs(folder, exist_ok=True)
    base = os.path.join(folder, _base_name(rows, cols, procs))

    _save_steps_plot(times_seq, times_par, rows, cols, procs, base)
    _save_summary_table(times_seq, times_par, rows, cols, procs, base)
    _save_steps_csv(times_seq, times_par, base)


def _save_steps_csv(times_seq, times_par, base):
    """Guarda el tiempo de cada paso en un CSV."""
    with open(base + "_tiempos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["paso", "secuencial_ms", "paralelo_ms"])
        for i, (s, p) in enumerate(zip(times_seq, times_par), start=1):
            writer.writerow([i, f"{s:.4f}", f"{p:.4f}"])