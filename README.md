# Juego de la Vida: Secuencial vs Paralelo (MPI)

Taller de Infraestructuras Paralelas y Distribuidas (750023C). Compara una versión secuencial con una paralela hecha con `mpi4py`, usando una interfaz gráfica en `pygame`.

## Requisitos

- Git
- Python 3.9 o superior
- Una implementación de MPI instalada en el sistema (ver abajo)
- Entorno gráfico (la GUI abre una ventana)

> `mpi4py` no incluye MPI. Hay que instalar MPI **antes** de ejecutar `pip install -r requirements.txt`.

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/Crimson-Blues/parallel_game_of_life.git
cd parallel
```

## 2. Instalar MPI y dependencias

### Windows

1. Instalar **Microsoft MPI** (descargar los dos archivos desde la página oficial de Microsoft):
   - `msmpisetup.exe` (runtime, trae `mpiexec`)
   - `msmpisdk.msi` (SDK, necesario para compilar `mpi4py`)
2. Cerrar y volver a abrir la terminal para que se actualice el `PATH`.
3. Crear el entorno virtual e instalar las librerías:
```powershell
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
```

### Linux (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip openmpi-bin libopenmpi-dev

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### CachyOS / Arch Linux

CachyOS está basado en Arch, por lo que se usa `pacman`. El paquete `python` ya incluye `venv`, y `openmpi` trae `mpirun` y los headers necesarios para compilar `mpi4py`.

```bash
sudo pacman -Syu
sudo pacman -S --needed python python-pip openmpi

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### macOS

```bash
brew install open-mpi python

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Ejecutar

```bash
mpiexec -n 4 python main.py
```
Donde `-n` indica el **número de procesos** MPI que se lanzan. Por ejemplo, `-n 4` crea 4 procesos.

- En Linux/macOS también sirve `mpirun -n 4 python3 main.py`.
- Si Open MPI muestra `not enough slots available`, agregar `--oversubscribe`:
```bash
  mpirun --oversubscribe -n 4 python3 main.py
```
- El número de procesos no debe superar el número de filas del tablero.

Al cerrar la ventana se crea la carpeta `resultados/` con las gráficas y el CSV de tiempos.
