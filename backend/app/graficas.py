import pyodbc
import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Crear una instancia de FastAPI
app = FastAPI()

# Conexión al archivo .mdb
mdb_path = 'C:\\Users\\pc03d\\Desktop\\MDB-PRUEBAS\\20240802_PNF_Tz200_P23_FF_FF.MDB'

conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + mdb_path

def connect_db():
    conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_path};'
    return pyodbc.connect(conn_str)

def query_to_df(query, conn):
    return pd.read_sql_query(query, conn)


def create_graphs():
    conn = pyodbc.connect(conn_str)

    # Extraer datos de las tablas correspondientes
    query_raster_scan1 = 'SELECT Rinc, Scan, Bin4Amptd FROM RasterScan'
    query_motion_data = 'SELECT [scan sector 1 start], [scan sector 1 stop], [step 1 sector 1 start], [step 1 sector 1 stop], [scan sector 1 number], [step 1 sector 1 number] FROM AcDF_MotionData'

    # Cargar datos en dataframes
    df_raster_scan1 = pd.read_sql(query_raster_scan1, conn)
    df_motion_data = pd.read_sql(query_motion_data, conn)

    # Verificar si los DataFrames no están vacíos
    if df_raster_scan1.empty or df_motion_data.empty:
        print("Error: DataFrame(s) vacíos.")
        return None, None, None

    # Limitar los valores de 'Bin1Amptd' a -10 dB como mínimo
    df_raster_scan1['Bin4Amptd'] = np.where((df_raster_scan1['Bin4Amptd'] > -10), df_raster_scan1['Bin4Amptd'], -10)

    # Obtener los límites de START y STOP desde AcDF_MotionData
    scan_start_value = float(df_motion_data['scan sector 1 start'].values[0])
    scan_stop_value = float(df_motion_data['scan sector 1 stop'].values[0]) 
    step_start_value = float(df_motion_data['step 1 sector 1 start'].values[0])
    step_stop_value = float(df_motion_data['step 1 sector 1 stop'].values[0])
    number_scan_value = int(df_motion_data['scan sector 1 number'].values[0])
    number_step_value = int(df_motion_data['step 1 sector 1 number'].values[0])


    # Crear la rejilla de valores x e y
    x = np.linspace(scan_start_value, scan_stop_value, number_scan_value)
    y = np.linspace(step_start_value, step_stop_value, number_step_value)

    # Crear un DataFrame 2D para la gráfica
    radiation2d = df_raster_scan1.pivot(index='Rinc', columns='Scan', values='Bin4Amptd')

    return radiation2d.values, x.tolist(), y.tolist()  # Retornar los datos necesarios

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Generar las gráficas y obtener los datos necesarios
    z, x, y = create_graphs()  # Generar las gráficas y obtener datos

    # Verificar si los datos son válidos
    if z is None or x is None or y is None:
        return HTMLResponse(content="<h1>Error al cargar los datos de la gráfica.</h1>")

    # Crear contenido HTML, mostrando la gráfica giratoria y estática
    html_content = """
    <h1>Patrón de Radiacíon</h1>
    <div style="display: flex; width: 100vw; height: 100vh; margin: 0; padding: 0; overflow: hidden;">
        <div id="graph1" style="flex: 1; height: 100%; margin-left: -40px;"></div>
        <div id="graph2" style="flex: 1; height: 100%; margin-left: -30px;"></div>
    </div>

    """

    html_content += """
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
        // Datos para ambas gráficas
        var data = [{
            z: """ + str(z.tolist()) + """,
            x: """ + str(x) + """,
            y: """ + str(y) + """,
            type: 'surface',
            colorscale: 'Jet',
            colorbar: {
                title: 'dB',
                xpad: 10,  // Ajustar el espacio entre la barra de color y la gráfica
                x: 1.2  // Mover la barra de color más lejos de la gráfica
            }
        }];
        
        // Configuración de la gráfica giratoria (con barra de color y etiqueta)
        var layout1 = {
            title: 'Patrón de Radiacíon',
            autosize: false,
            width: null,
            height: null,
            scene: {
                camera: {
                    eye: { x: 2.5, y: 1.5, z: 1.5 }
                }
            }
        };
        
        Plotly.newPlot('graph1', data, layout1); // Crear la gráfica giratoria

        // Datos de la gráfica estática 
        var data2 = [{
            z: """ + str(z.tolist()) + """,
            x: """ + str(x) + """,
            y: """ + str(y) + """,
            type: 'surface',
            colorscale: 'Jet',
            showscale: false  // Eliminar la barra de color en esta gráfica
        }];

        // Configuración de la gráfica estática
        var layout2 = {
            title: 'Elevación 1 - Estática',
            autosize: false,
            width: null,
            height: null,
            scene: {
                camera: {
                    eye: { x: .6, y: 1, z: .3 }          
                }
            }
        };
        
        Plotly.newPlot('graph2', data2, layout2); // Crear la gráfica estática

        // Función para rotar la gráfica automáticamente
        var angle = 0;
        function rotateGraph() {
            angle += 1; // Aumentar el ángulo de rotación
            var eye = {
                x: -0.5 * Math.cos(angle * Math.PI / 180),
                y: 1.5 * Math.sin(angle * Math.PI / 180),
                z: 0.5
            };
            Plotly.relayout('graph1', { scene: { camera: { eye: eye } }}); // Actualizar la vista
        }
        setInterval(rotateGraph, 50); // Controlar la velocidad de rotación
    </script>
    """
    return HTMLResponse(content=html_content)
