# cuestionarios-app

Aplicación en Streamlit para generar mensajes personalizados por bloque a partir de un Excel exportado de cursos en eXeLearning.

## Requisitos

- Python 3.10+
- Dependencias del archivo `requirements.txt`

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

## Uso

1. Sube un archivo `.xlsx`.
2. Selecciona la hoja del Excel.
3. Revisa/ajusta las columnas de:
   - Alumno (opcional)
   - Bloque
   - Estado (terminado/completado)
4. Pulsa **Generar mensajes**.
5. Descarga el CSV con el resultado.

La app intenta interpretar estados comunes (`sí/no`, `completado/pendiente`, `1/0`, porcentajes, etc.).
