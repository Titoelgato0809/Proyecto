import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Ruta calculada de forma relativa a este archivo (src/extract.py),
# en vez de una ruta absoluta fija a una máquina/usuario específico.
# Esto es lo único que cambia: sigue apuntando al mismo archivo
# dentro de la misma estructura de carpetas del proyecto
# (Proyecto/Data/raw/DatasetCompleto.xlsx).
RUTA_RAW = Path(__file__).resolve().parent.parent / "Data" / "raw" / "DatasetCompleto.xlsx"


# ============================================================
# EXTRACCIÓN
# ============================================================

def extraer_datos(ruta: Path) -> pd.DataFrame:
    """
    Extrae los datos del archivo Excel utilizando Pandas
    con el motor calamine.
    """

    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta}"
        )

    print("Iniciando extracción...")
    print(f"Archivo: {ruta}")

    # Se mantiene calamine como motor principal (más rápido para
    # archivos grandes). Si el paquete python-calamine no está
    # instalado en el entorno, se avisa y se usa openpyxl como
    # respaldo para no detener la ejecución.
    try:
        df = pd.read_excel(
            ruta,
            engine="calamine"
        )
    except ImportError:
        print(
            "\nAdvertencia: no se encontró el motor 'calamine' "
            "(falta instalar python-calamine). Usando 'openpyxl' "
            "como motor de respaldo."
        )
        df = pd.read_excel(
            ruta,
            engine="openpyxl"
        )

    print("\nExtracción completada.")
    print(f"Filas: {df.shape[0]:,}")
    print(f"Columnas: {df.shape[1]}")

    return df


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    df = extraer_datos(RUTA_RAW)

    print("\nPrimeras 5 filas:")
    print(df.head())