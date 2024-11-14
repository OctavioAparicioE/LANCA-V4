import pyodbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# Ruta del archivo .mdb
mdb_path = 'C:\\Users\\pc03d\\Desktop\\MDB-PRUEBAS\\20241018_Ed1_PNF_FF_FF.MDB'

# Conexión a la base de datos .mdb
conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_path};'
conn = pyodbc.connect(conn_str)

# Función para ejecutar consultas y devolver el resultado en un DataFrame
def query_to_df(query, conn):
    return pd.read_sql_query(query, conn)

# 1. Consulta a la tabla RasterScan para columnas Rinc, Scan y Bin4Amptd
query_raster_scan4 = 'SELECT Rinc, Scan, Bin4Amptd FROM RasterScan'
raster_scan4_data = query_to_df(query_raster_scan4, conn)

# Crear el DataFrame de datos de radiación a partir de raster_scan4_data
radiation = raster_scan4_data.copy()

# Filtrar valores de Bin4Amptd, estableciendo un límite mínimo de -10 dB
radiation['Bin4Amptd'] = np.where(radiation['Bin4Amptd'] > -10, radiation['Bin4Amptd'], -10)

# Leer los datos de la tabla AcDF_MotionData
query_rstimes = "SELECT [scan sector 1 start], [scan sector 1 stop], [step 1 sector 1 start], [step 1 sector 1 stop], [scan sector 1 number], [step 1 sector 1 number] FROM AcDF_MotionData"
df_rstimes = query_to_df(query_rstimes, conn)

# Variables de límites y número de pasos para la gráfica
scan_start_value = float(df_rstimes['scan sector 1 start'].values[0])
scan_stop_value = float(df_rstimes['scan sector 1 stop'].values[0])
step_start_value = float(df_rstimes['step 1 sector 1 start'].values[0])
step_stop_value = float(df_rstimes['step 1 sector 1 stop'].values[0])
number_scan_value = int(df_rstimes['scan sector 1 number'].values[0])
number_step_value = int(df_rstimes['step 1 sector 1 number'].values[0])

# Crear un DataFrame para los datos 3D de radiación
radiation3d = pd.DataFrame()

# Llenar el DataFrame radiation3d con los valores filtrados de Bin4Amptd usando Scan como eje X y Step como eje Y
for i in range(number_scan_value):
    a = radiation[radiation['Scan'] == i]
    a.set_index('Rinc', inplace=True)
    radiation3d[i] = a['Bin4Amptd']

# Configurar los ejes x e y con las dimensiones de la matriz radiation3d
x = np.linspace(scan_start_value, scan_stop_value, number_scan_value)  # Eje X: valores de Scan
y = np.linspace(step_start_value, step_stop_value, number_step_value)  # Eje Y: valores de Step

# Crear la aplicación Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Gráfico Azimuth & Elevacíon"),
    
    # Contenedor para los gráficos, con estilo flex para alineación horizontal
    html.Div([
        dcc.Graph(id='3d-graph', style={'width': '30%', 'height': '80vh', 'display': 'inline-block', 'padding': '1%'}),
        dcc.Graph(id='azimut-graph', style={'width': '30%', 'height': '80vh', 'display': 'inline-block', 'padding': '1%'}),
        dcc.Graph(id='elevacion-graph', style={'width': '30%', 'height': '80vh', 'display': 'inline-block', 'padding': '1%'}),
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-around'})
])

# Inicializar la gráfica 3D con Plotly
@app.callback(
    Output('3d-graph', 'figure'),
    Input('azimut-graph', 'hoverData')
)
def update_3d_graph(hoverData):
    fig = go.Figure(data=[
        go.Surface(
            z=radiation3d.values,
            x=x,
            y=y,
            colorscale='Jet',
            colorbar=dict(title='Amplitud (dB)', titlefont=dict(size=14))
        )
    ])
    fig.update_layout(title="Patron de Radiacion", scene=dict(
        xaxis_title="Scan",
        yaxis_title="Step",
        zaxis_title="Amplitud (dB)"
    ))
    return fig

# Callback para actualizar la gráfica de Azimut
@app.callback(
    Output('azimut-graph', 'figure'),
    Input('3d-graph', 'hoverData')
)
def update_azimut_graph(hoverData):
    if hoverData:
        y_index = hoverData['points'][0]['y']
    else:
        y_index = step_start_value + (step_stop_value - step_start_value) / 2
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=radiation3d.loc[y_index], mode='lines', name='Azimut'))
    fig.update_layout(
        title="Gráfico de Azimut",
        xaxis_title="Scan (Rango de Scan Start a Scan Stop)",
        yaxis_title="Amplitud (dB)"
    )
    return fig

# Callback para actualizar la gráfica de Elevación
@app.callback(
    Output('elevacion-graph', 'figure'),
    Input('3d-graph', 'hoverData')
)
def update_elevacion_gsraph(hoverData):
    if hoverData:
        x_index = hoverData['points'][0]['x']
    else:
        x_index = scan_start_value + (scan_stop_value - scan_start_value) / 2
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y, y=radiation3d.T.loc[x_index], mode='lines', name='Elevación'))
    fig.update_layout(
        title="Gráfico de Elevación",
        xaxis_title="Step (Rango de Step Start a Step Stop)",
        yaxis_title="Amplitud (dB)"
    )
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False)