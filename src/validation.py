import pandas as pd


def validation(df):
    
    df = df.copy ()

    # =========================================================
    # 1. VALIDACIÓN ESTRUCTURAL
    # =========================================================

    # ---------------------------------------------------------
    # 1.1 Validar que el dataset no esté vacío
    # ---------------------------------------------------------

    if df.empty:
        print("ERROR: el dataset está vacío.")
    else:
        print(
            f"OK: el dataset contiene {len(df)} filas."
        )


    # ---------------------------------------------------------
    # 1.2 Validar columnas obligatorias
    # ---------------------------------------------------------

    columnas_requeridas = [
        "Codigo Departamento UDS",
        "Departamento UDS",
        "Codigo Municipio UDS",
        "Municipio UDS",
        "Codigo CentroZonal UDS",
        "Centro Zonal UDS",

        # Identificación del servicio
        "Codigo Unidad Servicio",
        "Unidad Servicio",
        "Estado UDS",
        "Nombre Servicio",
        "Tipo Servicio",
        "Tipo de Beneficiario",

        # Características del beneficiario
        "Sexo",
        "Rango Edad",
        "Grupo Etnico",
        "Presenta Discapacidad",
        "Zona Ubicacion Beneficiario",
        "Pais Nacimiento",
        "Estado Atención",

        # Medida principal
        "Beneficiarios"
    ]


    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]


    if columnas_faltantes:
        print(
            "ERROR: faltan las siguientes columnas:"
        )
        print(columnas_faltantes)

    else:
        print(
            "OK: todas las columnas requeridas "
            "están presentes."
        )


    # ---------------------------------------------------------
    # 1.3 Resultado general de la estructura
    # ---------------------------------------------------------

    if df.empty or columnas_faltantes:
        print(
            "ERROR: la validación estructural "
            "NO fue superada."
        )
    else:
        print(
            "OK: la validación estructural "
            "fue superada."
        )   
                          
    # =========================================================
    # 2. TIPOS De Datos
    # =========================================================
    
    columnas_numerico = [
            "Codigo Departamento UDS",
            "Codigo Municipio UDS",
            "Codigo CentroZonal UDS",
            "Codigo Unidad Servicio",
            "Beneficiarios"
    ]
    
    for columna in columnas_numerico:
        if columna not in df.columns:
            print(f"ERROR: falta la columna {columna}.")
            continue  

        if not pd.api.types.is_integer_dtype(df[columna]):
            print(f"ERROR: {columna} no es entero.")
        else:
            print(f"OK: {columna} es entero.")

    # =========================================================
    # 2.1 TIPOS De Datos Categoricos
    # =========================================================

    columna_categorico = [ 
            "Unidad Servicio",
            "Estado UDS",
            "Nombre Servicio",
            "Tipo Servicio",
            "Tipo de Beneficiario",
            "Sexo",
            "Rango Edad",
            "Grupo Etnico",
            "Presenta Discapacidad",
            "Zona Ubicacion Beneficiario",
            "Pais Nacimiento",
            "Estado Atención",
            "Municipio UDS",
            "Departamento UDS",
            "Centro Zonal UDS"
    ]

    for columna in columna_categorico:
        if columna not in df.columns:
            print(f"ERROR: falta la columna {columna}.")
            continue

        if not (pd.api.types.is_string_dtype(df[columna]) or
                isinstance(df[columna].dtype, pd.CategoricalDtype)):
            print(f"ERROR: {columna} no es string ni category.")
        else:
            print(f"OK: {columna} es string o category.")
            
            
    def validar_categoria(nombre_columna, valores_validos):
    
        if nombre_columna not in df.columns:
            return 
        encontrados = set(df[nombre_columna].dropna().unique())
        invalidos = encontrados - valores_validos   

        if  invalidos :
            print(f"ERROR: {nombre_columna} tiene categorías inválidas: {invalidos}")
        else:
            print(f"OK: todas las categorías de {nombre_columna} son válidas.")
            
    # =========================================================
    # 2.2 Validacion de Categorias
    # =========================================================
    
    
    validar_categoria("Sexo", {"M", "H", "I"})
    
    validar_categoria("Estado Atención", {"A", "I"})
    
    validar_categoria("Presenta Discapacidad", {"SI", "NO"})
    
    validar_categoria("Estado UDS", {"ACTIVA", "INACTIVA"})
    
    validar_categoria(
        
        "Zona Ubicacion Beneficiario",
        
        {"CABECERA", "RESTO", "SIN INFORMACIÓN"}
    )
    validar_categoria(
        
        "Grupo Etnico",
        
        {
            
            "NO SE AUTORRECONOCE EN NINGUNO DE LOS ANTERIORES",
            
            "INDÍGENA", "AFROCOLOMBIANO (A)", "COMUNIDAD NEGRA",
            
            "RAIZAL", "PALENQUERO (A)", "ROM/GITANO",
        }
    )
    
    validar_categoria(
    "Rango Edad",
    {
        "0-6 MESES", "6 MESES - 5 AÑOS", "6 - 8 AÑOS",
        "9 - 13 AÑOS", "14 - 17 AÑOS", "MAYOR A 18 AÑOS",
        "SIN INFORMACIÓN",
    }
    ) 
    
    validar_categoria(
        
        "Tipo Servicio",
        
        {
            "HCB", "MAI", "CENTRO DE DESARROLLO INFANTIL", "JARDÍN",
            "EDUCACIÓN INICIAL", "SEMILLAS DE VIDA", "SERVICIO PROPIO",
            "OTROS", "SIN INFORMACIÓN",
        }
    )
    # =========================================================
    # 3. Validación de identificadores
    # =========================================================
    
    
    columna_identificadores=[
            "Codigo Departamento UDS",
            "Codigo Municipio UDS",
            "Codigo CentroZonal UDS",
            "Codigo Unidad Servicio",
     ]
    
    for columna in columna_identificadores:
        
        if columna not in df.columns:
            print(f"ERROR: falta la columna {columna}.")
            continue

        nulos = df[columna].isnull().sum()
        if nulos > 0:
            print(f"ERROR: {columna} tiene {nulos} valores nulos.")
        else:
            print(f"OK: {columna} no tiene valores nulos.")
            
    # =========================================================
    # 3.1 Validación de Rango
    # =========================================================

        # Validar que los identificadores sean mayores que cero.
        # Los valores nulos se excluyen porque ya fueron validados arriba.
        valores_no_positivos = df.loc[
            df[columna].notna() & (df[columna] <= 0),
            columna
        ]

        if not valores_no_positivos.empty:
            print(
                f"ERROR: {columna} tiene "
                f"{len(valores_no_positivos)} valores menores o iguales a 0."
            )
        else:
            print(f"OK: todos los valores de {columna} son mayores que 0.")

    # Beneficiarios también debe ser una cantidad positiva.
    
    columna = "Beneficiarios"
    if columna in df.columns:
        valores_no_positivos = df.loc[
            df[columna].notna() & (df[columna] <= 0),
            columna
        ]

        if not valores_no_positivos.empty:
            print(
                f"ERROR: {columna} tiene "
                f"{len(valores_no_positivos)} valores menores o iguales a 0."
            )
        else:
            print(f"OK: todos los valores de {columna} son mayores que 0.")
    
    # =========================================================
    # 3.2 Validación de identificadores(Departamento)
    # =========================================================
    
    inconsistentes = (
        df.groupby("Codigo Departamento UDS")["Departamento UDS"]
        .nunique()
    )

    inconsistentes = inconsistentes[
        inconsistentes > 1
    ]

    if len(inconsistentes) > 0:

        print(
            "ERROR: inconsistencias entre "
            "Código Departamento ↔ Departamento."
        )

    else:

        print(
            "OK: Código Departamento ↔ Departamento "
            "es consistente."
        )
        
    # =========================================================
    # 3.3 Validación de identificadores(Municipio)
    # =========================================================
    
    inconsistentes = (
        df.groupby("Codigo Municipio UDS")["Municipio UDS"]
        .nunique()
    )

    inconsistentes = inconsistentes[
        inconsistentes > 1
    ]

    if len(inconsistentes) > 0:

        print(
            "ERROR: inconsistencias entre "
            "Código Municipio ↔ Municipio."
        )

    else:

        print(
            "OK: Código Municipio ↔ Municipio "
            "es consistente."
        )

    # =========================================================
    # 3.4 Validación de identificadores(Municipio y Departamentos)
    # =========================================================
    
    inconsistentes = (
        df.groupby("Codigo Municipio UDS")["Codigo Departamento UDS"]
        .nunique()
    )

    inconsistentes = inconsistentes[
        inconsistentes > 1
    ]

    if len(inconsistentes) > 0:

        print(
            "ERROR: un municipio aparece asociado "
            "a múltiples departamentos."
        )

    else:

        print(
            "OK: Municipio ↔ Departamento "
            "es consistente."
        )

