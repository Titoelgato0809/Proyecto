import pandas as pd
from collections import defaultdict

# ==========================================
# 1. CONFIGURACIÓN Y CONVERSIÓN INICIAL
# ==========================================

ruta_excel = r"C:\Users\Titoelgato\OneDrive\Quinto semestre\ETL\Proyecto\Data\raw\DatasetCompleto.xlsx"
ruta_csv = r"C:\Users\Titoelgato\OneDrive\Quinto semestre\ETL\Proyecto\Data\raw\DatasetCompleto.csv"


# df = pd.read_excel(ruta_excel, engine="calamine")
# df.to_csv(ruta_csv, index=False, encoding="utf-8")

ruta = ruta_csv
TAMANO_LOTE = 50000

variables_caracterizacion = [
    'Sexo', 'Rango Edad', 'Grupo Etnico', 'Presenta Discapacidad',
    'Tipo de Beneficiario', 'Zona Ubicacion Beneficiario', 'Pais Nacimiento'
]

columnas_territoriales = [
    'Vigencia', 'Codigo Departamento UDS', 'Codigo Municipio UDS',
    'Codigo CentroZonal UDS', 'Codigo Unidad Servicio'
]

columnas_grano_completo = columnas_territoriales + variables_caracterizacion + ['Estado Atención']

# ==========================================
# 2. ACUMULADORES
# ==========================================

total_filas = 0
nulos_totales = None

depto_codigo_a_nombre = defaultdict(set)

# Beneficiarios por dimensión (dict -> se convierte a Series al final)
beneficiarios_departamento = defaultdict(int)
beneficiarios_municipio = defaultdict(int)

conteo_modalidad = pd.Series(dtype='int64')
conteo_nombre_servicio = pd.Series(dtype='int64')
conteo_estado_uds = pd.Series(dtype='int64')

conteo_caracterizacion = {col: pd.Series(dtype='int64') for col in variables_caracterizacion}
beneficiarios_por_caracteristica = {col: defaultdict(int) for col in variables_caracterizacion}

# Cruces territorio + característica: dict con tupla (Departamento, valor_columna) como llave
cruces_territorio = {col: defaultdict(int) for col in variables_caracterizacion}

# Modalidad nula: qué Nombre Servicio la origina
modalidad_nula_por_servicio = pd.Series(dtype='int64')
beneficiarios_modalidad_nula_por_estado = defaultdict(int)

conteo_estado_atencion = pd.Series(dtype='int64')
beneficiarios_por_estado_atencion = defaultdict(int)

duplicados_territoriales = 0
duplicados_grano_completo = 0

# ==========================================
# 3. LECTURA Y ACUMULACIÓN POR LOTES
# ==========================================

for lote in pd.read_csv(ruta, chunksize=TAMANO_LOTE):

    total_filas += len(lote)

    # --- Nulos ---
    nulos_lote = lote.isnull().sum()
    nulos_totales = nulos_lote if nulos_totales is None else nulos_totales.add(nulos_lote, fill_value=0)

    # --- Validación territorial ---
    for cod, nom in lote[['Codigo Departamento UDS', 'Departamento UDS']].drop_duplicates().itertuples(index=False):
        depto_codigo_a_nombre[cod].add(nom)

    # --- Beneficiarios por territorio (SUMA real, acumulada en dict) ---
    for depto, valor in lote.groupby('Departamento UDS')['Beneficiarios'].sum().items():
        beneficiarios_departamento[depto] += valor

    for muni, valor in lote.groupby('Municipio UDS')['Beneficiarios'].sum().items():
        beneficiarios_municipio[muni] += valor

    # --- Modalidad / servicio ---
    conteo_modalidad = conteo_modalidad.add(lote['Modalidad'].value_counts(dropna=False), fill_value=0)
    conteo_nombre_servicio = conteo_nombre_servicio.add(lote['Nombre Servicio'].value_counts(dropna=False), fill_value=0)
    conteo_estado_uds = conteo_estado_uds.add(lote['Estado UDS'].value_counts(dropna=False), fill_value=0)

    # --- Caracterización + cruce con Beneficiarios ---
    for col in variables_caracterizacion:
        conteo_caracterizacion[col] = conteo_caracterizacion[col].add(
            lote[col].value_counts(dropna=False), fill_value=0)

        for valor_col, suma in lote.groupby(col)['Beneficiarios'].sum().items():
            beneficiarios_por_caracteristica[col][valor_col] += suma

        # --- Cruce territorio + característica ---
        cruce_lote = lote.groupby(['Departamento UDS', col])['Beneficiarios'].sum()
        for llave, valor in cruce_lote.items():
            cruces_territorio[col][llave] += valor

    # --- Investigar Modalidad nula ---
    modalidad_nula = lote[lote['Modalidad'].isna()]
    modalidad_nula_por_servicio = modalidad_nula_por_servicio.add(
        modalidad_nula['Nombre Servicio'].value_counts(), fill_value=0)

    for estado, valor in modalidad_nula.groupby('Estado Atención')['Beneficiarios'].sum().items():
        beneficiarios_modalidad_nula_por_estado[estado] += valor

    # --- Estado Atención ---
    conteo_estado_atencion = conteo_estado_atencion.add(
        lote['Estado Atención'].value_counts(dropna=False), fill_value=0)

    for estado, valor in lote.groupby('Estado Atención')['Beneficiarios'].sum().items():
        beneficiarios_por_estado_atencion[estado] += valor

    # --- Duplicados (conteos escalares, se suman directamente) ---
    duplicados_territoriales += lote.duplicated(subset=columnas_territoriales).sum()
    duplicados_grano_completo += lote.duplicated(subset=columnas_grano_completo).sum()

# ==========================================
# 4. RESULTADOS FINALES (dataset completo)
# ==========================================

print(f"Total de filas procesadas: {total_filas}\n")

print("========== NULOS TOTALES ==========")
print(nulos_totales)

print("\n========== VALIDACIÓN TERRITORIAL ==========")
inconsistencias = {c: n for c, n in depto_codigo_a_nombre.items() if len(n) > 1}
print(f"Códigos de departamento con más de un nombre: {len(inconsistencias)}")
if inconsistencias:
    print(inconsistencias)

print("\n========== BENEFICIARIOS POR DEPARTAMENTO (total real) ==========")
serie_depto = pd.Series(beneficiarios_departamento).sort_values(ascending=False)
print(serie_depto.astype(int))
print("\n% de participación nacional:")
print((serie_depto / serie_depto.sum() * 100).round(2))

print("\n========== TOP 20 MUNICIPIOS POR BENEFICIARIOS ==========")
serie_muni = pd.Series(beneficiarios_municipio).sort_values(ascending=False)
print(serie_muni.head(20).astype(int))

print("\n========== MODALIDAD ==========")
print(conteo_modalidad.sort_values(ascending=False).astype(int))

print("\n========== NOMBRE SERVICIO (top 20) ==========")
print(conteo_nombre_servicio.sort_values(ascending=False).head(20).astype(int))

print("\n========== ESTADO UDS ==========")
print(conteo_estado_uds.astype(int))

print("\n========== CARACTERIZACIÓN DE BENEFICIARIOS ==========")
for col in variables_caracterizacion:
    print(f"\n--- {col} (conteo de registros) ---")
    print(conteo_caracterizacion[col].sort_values(ascending=False).astype(int))
    print(f"\n--- {col} (suma de Beneficiarios) ---")
    serie_col = pd.Series(beneficiarios_por_caracteristica[col]).sort_values(ascending=False)
    print(serie_col.astype(int))

print("\n========== TERRITORIO + CARACTERÍSTICAS (top 15 cada uno) ==========")
for col in variables_caracterizacion:
    print(f"\n--- Departamento + {col} ---")
    serie_final = pd.Series(cruces_territorio[col])
    print(serie_final.sort_values(ascending=False).head(15).astype(int))

print("\n========== INVESTIGACIÓN: MODALIDAD NULA ==========")
print(f"Total de registros con Modalidad nula: {int(nulos_totales['Modalidad'])} de {total_filas} "
      f"({nulos_totales['Modalidad']/total_filas*100:.1f}%)")
print("\n¿De qué Nombre Servicio vienen los nulos de Modalidad?")
print(modalidad_nula_por_servicio.sort_values(ascending=False).astype(int))
print("\nBeneficiarios en filas con Modalidad nula, por Estado Atención:")
print(pd.Series(beneficiarios_modalidad_nula_por_estado).astype(int))

print("\n========== ESTADO ATENCIÓN ==========")
print("Conteo de registros:")
print(conteo_estado_atencion.astype(int))
print("\nSuma de beneficiarios:")
print(pd.Series(beneficiarios_por_estado_atencion).astype(int))


print("\n========== ANÁLISIS DE GRANO ==========")
print(f"Duplicados SOLO por columnas territoriales (misma unidad de servicio, distintas filas): "
      f"{duplicados_territoriales}")
print(f"Duplicados incluyendo TODAS las características del beneficiario (grano completo): "
      f"{duplicados_grano_completo}")
print("(Si este segundo número es 0 o cercano a 0, confirma que cada fila es una combinación "
      "única de atributos, y 'Beneficiarios' es el conteo agregado de ese grupo.)")