import io
from typing import Iterable

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Mensajes por bloque (eXeLearning)", page_icon="📚", layout="wide")


def normalize_columns(columns: Iterable[str]) -> dict[str, str]:
    """Devuelve un mapa de nombre_normalizado -> nombre_original."""
    mapping: dict[str, str] = {}
    for col in columns:
        normalized = (
            str(col)
            .strip()
            .lower()
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )
        mapping[normalized] = col
    return mapping


def find_first_existing(mapping: dict[str, str], options: list[str]) -> str | None:
    for option in options:
        if option in mapping:
            return mapping[option]
    return None


def parse_completed(value: object) -> bool | None:
    """
    Convierte distintas variantes a estado completado.
    Devuelve True/False o None si no se puede inferir.
    """
    if pd.isna(value):
        return None

    if isinstance(value, (int, float)):
        return value >= 1

    text = str(value).strip().lower()
    truthy = {
        "si",
        "sí",
        "yes",
        "true",
        "completado",
        "completa",
        "finalizado",
        "terminado",
        "hecho",
        "1",
        "100%",
    }
    falsy = {
        "no",
        "false",
        "pendiente",
        "incompleto",
        "sin terminar",
        "0",
        "0%",
    }

    if text in truthy:
        return True
    if text in falsy:
        return False

    if text.endswith("%"):
        try:
            percentage = float(text.replace("%", "").replace(",", "."))
            return percentage >= 100
        except ValueError:
            return None

    return None


def build_message(student: str, block: str, completed: bool | None) -> str:
    student_part = f"{student}: " if student else ""
    if completed is True:
        return f"{student_part}¡Enhorabuena! Has terminado el bloque \"{block}\"."
    if completed is False:
        return (
            f"{student_part}Aún no has terminado el bloque \"{block}\". "
            "Te animo a completarlo esta semana."
        )
    return (
        f"{student_part}No he podido determinar el estado del bloque \"{block}\". "
        "Revisa el valor en el Excel."
    )


st.title("📚 Generador de mensajes por bloque (eXeLearning)")
st.write(
    "Sube tu archivo Excel y la app generará un mensaje para cada bloque "
    "según si está terminado o no."
)

uploaded_file = st.file_uploader("Sube el Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    excel_bytes = io.BytesIO(uploaded_file.read())
    sheets = pd.read_excel(excel_bytes, sheet_name=None)

    sheet_name = st.selectbox("Selecciona la hoja", list(sheets.keys()))
    df = sheets[sheet_name].copy()

    st.subheader("Vista previa de datos")
    st.dataframe(df.head(20), use_container_width=True)

    if df.empty:
        st.warning("La hoja seleccionada está vacía.")
    else:
        normalized = normalize_columns(df.columns)
        student_col = find_first_existing(
            normalized,
            ["alumno", "estudiante", "nombre", "usuario", "user", "student"],
        )
        block_col = find_first_existing(
            normalized,
            ["bloque", "modulo", "módulo", "unidad", "actividad", "block", "module"],
        )
        status_col = find_first_existing(
            normalized,
            [
                "terminado",
                "finalizado",
                "completado",
                "estado",
                "progreso",
                "finished",
                "completed",
                "status",
            ],
        )

        with st.expander("Configurar columnas", expanded=True):
            selected_student = st.selectbox(
                "Columna de alumno (opcional)",
                ["(sin columna de alumno)", *df.columns],
                index=(["(sin columna de alumno)", *df.columns].index(student_col) if student_col else 0),
            )
            selected_block = st.selectbox(
                "Columna de bloque",
                list(df.columns),
                index=list(df.columns).index(block_col) if block_col else 0,
            )
            selected_status = st.selectbox(
                "Columna de estado/terminado",
                list(df.columns),
                index=list(df.columns).index(status_col) if status_col else 0,
            )

        if st.button("Generar mensajes", type="primary"):
            output = df.copy()

            student_series = (
                output[selected_student] if selected_student != "(sin columna de alumno)" else pd.Series([""] * len(output))
            )

            output["mensaje"] = [
                build_message(str(student).strip(), str(block).strip(), parse_completed(status))
                for student, block, status in zip(
                    student_series,
                    output[selected_block],
                    output[selected_status],
                )
            ]

            st.subheader("Mensajes generados")
            st.dataframe(output[[selected_block, selected_status, "mensaje"]], use_container_width=True)

            csv = output.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "Descargar resultados (CSV)",
                data=csv,
                file_name="mensajes_por_bloque.csv",
                mime="text/csv",
            )
else:
    st.info("👆 Sube un archivo para comenzar.")
