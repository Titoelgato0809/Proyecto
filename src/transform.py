import pandas as pd


def transformar(df):
    """
    Transformación y preparación del dataset.

    Responsabilidades:
    - Estandarizar categorías y textos.
    - Corregir tipos de datos.
    - Preparar identificadores.
    - Preparar valores faltantes.
    - Crear atributos derivados justificados.

    No realiza agregaciones ni cálculos de KPIs.
    """

    df = df.copy()

    # =========================================================
    # 1. IDENTIFICADORES
    # =========================================================

    # Los códigos territoriales son identificadores.
    # Se mantienen como enteros porque no presentan
    # información decimal ni valores faltantes.
    df["Codigo Departamento UDS"] = pd.to_numeric(
        df["Codigo Departamento UDS"],
        errors="raise"
    ).astype("Int64")

    df["Codigo Municipio UDS"] = pd.to_numeric(
        df["Codigo Municipio UDS"],
        errors="raise"
    ).astype("Int64")

    df["Codigo CentroZonal UDS"] = pd.to_numeric(
        df["Codigo CentroZonal UDS"],
        errors="raise"
    ).astype("Int64")

    df["Codigo Unidad Servicio"] = pd.to_numeric(
        df["Codigo Unidad Servicio"],
        errors="raise"
    ).astype("Int64")


    # =========================================================
    # 2. VIGENCIA
    # =========================================================

    # No es una fecha. Es un identificador de vigencia
    # y actualmente contiene un único año.
    df["Vigencia"] = pd.to_numeric(
        df["Vigencia"],
        errors="raise"
    ).astype("Int64")


    # =========================================================
    # 3. VARIABLE NUMÉRICA PRINCIPAL
    # =========================================================

    df["Beneficiarios"] = pd.to_numeric(
        df["Beneficiarios"],
        errors="raise"
    )

    # Validación de la medida
    if (df["Beneficiarios"] < 0).any():
        raise ValueError(
            "La variable Beneficiarios contiene valores negativos."
        )

    if df["Beneficiarios"].isna().any():
        raise ValueError(
            "La variable Beneficiarios contiene valores nulos."
        )

    # Los beneficiarios representan cantidades enteras.
    df["Beneficiarios"] = df["Beneficiarios"].astype("Int64")


    # =========================================================
    # 4. ESTANDARIZACIÓN DE VARIABLES CATEGÓRICAS
    # =========================================================

    columnas_categoricas = [
        "Departamento UDS",
        "Municipio UDS",
        "Centro Zonal UDS",
        "Unidad Servicio",
        "Estado UDS",
        "Modalidad",
        "Nombre Servicio",
        "Tipo de Beneficiario",
        "Sexo",
        "Rango Edad",
        "Grupo Etnico",
        "Presenta Discapacidad",
        "Zona Ubicacion Beneficiario",
        "Pais Nacimiento",
        "Estado Atención"
    ]

    for columna in columnas_categoricas:

        df[columna] = (
            df[columna]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.upper()
        )


    # =========================================================
    # 5. NORMALIZACIÓN DE ESTADO DE ATENCIÓN
    # =========================================================

    # El origen utiliza:
    # 1 = A
    # 2 = I
    # además de A e I.
    mapa_estado_atencion = {
        "1": "A",
        "2": "I",
        "A": "A",
        "I": "I"
    }

    df["Estado Atención"] = (
        df["Estado Atención"]
        .replace(mapa_estado_atencion)
    )


    # Validar que no aparezcan categorías inesperadas
    estados_validos = {"A", "I"}

    estados_encontrados = set(
        df["Estado Atención"]
        .dropna()
        .unique()
    )

    estados_invalidos = estados_encontrados - estados_validos

    if estados_invalidos:
        raise ValueError(
            f"Valores inesperados en Estado Atención: "
            f"{estados_invalidos}"
        )


    # =========================================================
    # 6. CATEGORÍAS FALTANTES
    # =========================================================

    # Estos faltantes sí se conservan explícitamente como
    # categoría analítica.
    df["Zona Ubicacion Beneficiario"] = (
        df["Zona Ubicacion Beneficiario"]
        .fillna("SIN INFORMACIÓN")
    )

    df["Pais Nacimiento"] = (
        df["Pais Nacimiento"]
        .fillna("SIN INFORMACIÓN")
    )

    df["Rango Edad"] = (
        df["Rango Edad"]
        .fillna("SIN INFORMACIÓN")
    )


    # Modalidad NO se imputa porque presenta una proporción
    # muy alta de valores faltantes y no se utilizará como
    # variable analítica principal.
    #
    # Se conserva para trazabilidad.


    # =========================================================
    # 7. ATRIBUTO DERIVADO JUSTIFICADO
    # =========================================================

    # R3 requiere trabajar con el tipo de servicio.
    # Se deriva a partir de Nombre Servicio porque Modalidad
    # presenta demasiados valores faltantes.

    def clasificar_servicio(nombre):

        if pd.isna(nombre):
            return "SIN INFORMACIÓN"

        nombre = str(nombre)

        if "HCB" in nombre:
            return "HCB"

        if "MAI" in nombre:
            return "MAI"

        if "CENTRO DE DESARROLLO INFANTIL" in nombre:
            return "CENTRO DE DESARROLLO INFANTIL"

        if "JARDIN" in nombre:
            return "JARDÍN"

        if "EDUCACION INICIAL" in nombre:
            return "EDUCACIÓN INICIAL"

        if "SEMILLAS DE VIDA" in nombre:
            return "SEMILLAS DE VIDA"

        if "CRIC" in nombre:
            return "SERVICIO PROPIO"

        return "OTROS"

    df["Tipo Servicio"] = (
        df["Nombre Servicio"]
        .apply(clasificar_servicio)
    )


    # =========================================================
    # 8. TIPOS CATEGÓRICOS
    # =========================================================

    # Se convierten las variables categóricas al tipo
    # category para reducir memoria y dejar explícita
    # su naturaleza.
    for columna in columnas_categoricas + ["Tipo Servicio"]:
        df[columna] = df[columna].astype("category")
        
    # =========================================================
    # 9. Seleccionar dataset para trabajar 
    # =======================================================
    
    def dataset_definitivo(df):

        columnas_definitivas = [
            # Identificación territorial
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

        return df[columnas_definitivas].copy()

    
    df = dataset_definitivo(df)

    return df