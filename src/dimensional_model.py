import pandas as pd


def build_dim_geography(df):
    columnas = [
        "Codigo Departamento UDS", "Departamento UDS",
        "Codigo Municipio UDS", "Municipio UDS",
        "Codigo CentroZonal UDS", "Centro Zonal UDS",
    ]
    dim_geography = df[columnas].drop_duplicates().reset_index(drop=True)
    dim_geography.insert(0, "geography_key", range(1, len(dim_geography) + 1))
    return dim_geography


def build_dim_service_unit(df):
    columnas = ["Codigo Unidad Servicio", "Unidad Servicio", "Estado UDS"]
    dim_service_unit = df[columnas].drop_duplicates().reset_index(drop=True)
    dim_service_unit.insert(0, "service_unit_key", range(1, len(dim_service_unit) + 1))
    return dim_service_unit


def build_dim_service(df):
    # Nombre Servicio + Tipo Servicio (Tipo Servicio es un atributo
    # derivado creado en transform.py a partir de Nombre Servicio).
    columnas = ["Nombre Servicio", "Tipo Servicio"]
    dim_service = df[columnas].drop_duplicates().reset_index(drop=True)
    dim_service.insert(0, "service_key", range(1, len(dim_service) + 1))
    return dim_service


def build_dim_beneficiary_profile(df):
    columnas = [
        "Sexo", "Rango Edad", "Grupo Etnico", "Presenta Discapacidad",
        "Zona Ubicacion Beneficiario", "Tipo de Beneficiario", "Pais Nacimiento",
    ]
    dim_beneficiary_profile = df[columnas].drop_duplicates().reset_index(drop=True)
    dim_beneficiary_profile.insert(0, "beneficiary_profile_key", range(1, len(dim_beneficiary_profile) + 1))
    return dim_beneficiary_profile


def build_dim_attention_status(df):
    # Estado Atención ya viene normalizado a A/I desde transform.py
    # (confirmado con la fuente oficial del ICBF).
    estados = df["Estado Atención"].unique()
    dim_attention_status = pd.DataFrame({"Estado Atención": estados})
    dim_attention_status["attention_status_key"] = range(1, len(dim_attention_status) + 1)

    descripciones = {"A": "Activo", "I": "Inactivo"}
    dim_attention_status["description"] = dim_attention_status["Estado Atención"].map(descripciones)

    return dim_attention_status


def build_fact_atencion(df, dim_geography, dim_service_unit, dim_service,
                         dim_beneficiary_profile, dim_attention_status):

    cols_geography = ["Codigo Departamento UDS", "Departamento UDS",
                       "Codigo Municipio UDS", "Municipio UDS",
                       "Codigo CentroZonal UDS", "Centro Zonal UDS"]
    cols_service_unit = ["Codigo Unidad Servicio", "Unidad Servicio", "Estado UDS"]
    cols_service = ["Nombre Servicio", "Tipo Servicio"]
    cols_beneficiary_profile = ["Sexo", "Rango Edad", "Grupo Etnico", "Presenta Discapacidad",
                                 "Zona Ubicacion Beneficiario", "Tipo de Beneficiario", "Pais Nacimiento"]

    # Nota: como las dimensiones NO renombraron sus columnas (a diferencia
    # de dim_technology/dim_country en el ejemplo, que sí renombraban),
    # el merge puede hacerse con on=[...] en vez de left_on/right_on,
    # ya que los nombres coinciden a ambos lados.
    df = df.merge(dim_geography, on=cols_geography, how="left")
    df = df.merge(dim_service_unit, on=cols_service_unit, how="left")
    df = df.merge(dim_service, on=cols_service, how="left")
    df = df.merge(dim_beneficiary_profile, on=cols_beneficiary_profile, how="left")
    df = df.merge(dim_attention_status[["Estado Atención", "attention_status_key"]],
                  on="Estado Atención", how="left")

    # El grano declarado exige colapsar (SUM) las filas que compartan
    # exactamente la misma combinación de dimensiones,
    # a diferencia del ejemplo de referencia, donde cada fila del
    # fact ya era única de por sí (una aplicación = una fila).
    grain_columns = ["geography_key", "service_unit_key", "service_key",
                      "beneficiary_profile_key", "attention_status_key"]

    fact_atencion = df.groupby(grain_columns, as_index=False)["Beneficiarios"].sum()

    fact_atencion = fact_atencion.rename(columns={
        "Beneficiarios": "total_beneficiarios",
    })

    fact_atencion.insert(0, "fact_key", range(1, len(fact_atencion) + 1))

    return fact_atencion

