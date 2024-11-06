import pyodbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go


##Este es el bueno para imprimir las graficas en 3D con los datos extraidos de MDB y tambien
##procesandolos en variables, 

# Ruta del archivo .mdb
mdb_path = 'C:\\Users\\pc03d\\Desktop\\graficasweb\\20241018_Ed1_PNF_FF_FF.MDB'

# Conexión a la base de datos .mdb
conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_path};'
conn = pyodbc.connect(conn_str)

# Función para ejecutar consultas y devolver el resultado en una lista de diccionarios
def query_to_list(query, conn):
    df = pd.read_sql(query, conn)
    return df.to_dict(orient='records')  # Convierte el DataFrame a una lista de diccionarios

# 1. Consulta a la tabla RasterScan para columnas Rinc, Scan y Bin4Amptd
query_raster_scan4 = 'SELECT Rinc, Scan, Bin4Amptd FROM RasterScan'
raster_scan4_data = query_to_list(query_raster_scan4, conn)

# 2. Consulta a la tabla AcDF_Frequency para la columna FREQUENCY
query_frequency = 'SELECT FREQUENCY FROM AcDF_Frequency'
frequency_data = query_to_list(query_frequency, conn)

# 3. Consulta a la tabla AcDF_MotionData para columnas específicas renombradas
query_motion_data = '''
SELECT [scan sector 1 start] AS SCAN_START, 
       [scan sector 1 stop] AS SCAN_STOP, 
       [step 1 sector 1 start] AS STEP_START, 
       [step 1 sector 1 stop] AS STEP_STOP, 
       [scan sector 1 number] AS POINTS_SCAN,
       [step 1 sector 1 number] AS POINTS_STEP 

FROM AcDF_MotionData
'''
motion_data = query_to_list(query_motion_data, conn)

# Extraer los valores necesarios de motion_data
scan_start_values = motion_data[0]['SCAN_START']
scan_stop_values = motion_data[0]['SCAN_STOP']
step_start_values = motion_data[0]['STEP_START']
step_stop_values = motion_data[0]['STEP_STOP']
points_values_scan = float(motion_data[0]['POINTS_SCAN'])
points_values_step = float(motion_data[0]['POINTS_STEP'])

# Cerrar la conexión
conn.close()

# Crear el DataFrame de datos de radiación a partir de raster_scan4_data
radiation = pd.DataFrame(raster_scan4_data)

# Filtrar valores de Bin4Amptd, estableciendo un límite mínimo de -10 dB
radiation['Bin4Amptd'] = np.where(radiation['Bin4Amptd'] > -10, radiation['Bin4Amptd'], -10)

# Crear un DataFrame vacío para los datos 3D de radiación
radiation3d = pd.DataFrame()

# Llenar el DataFrame radiation3d con los valores filtrados de Bin4Amptd
for i in range(points_values_scan):
    a = radiation[radiation['Scan'] == i]
    a.set_index('Rinc', inplace=True)
    radiation3d[i] = a['Bin4Amptd']

# Configurar los ejes x e y con las dimensiones de la matriz radiation3d
sh_0, sh_1 = radiation3d.shape
x = np.linspace(scan_start_values, scan_stop_values, sh_1)  # Eje X: valores de Scan
y = np.linspace(step_start_values, step_stop_values, sh_0)  # Eje Y: valores de Step

# Generar la gráfica 3D
fig = go.Figure(data=[go.Surface(z=radiation3d.values, x=x, y=y, colorscale='Jet', colorbar=dict(title='dB'))])

# Actualizar contornos y diseño de la gráfica
fig.update_traces(contours_z=dict(show=True, usecolormap=True, highlightcolor="limegreen", project_z=True))
fig.update_layout(
    title='Elevación',
    autosize=False,
    width=800, height=800,
    margin=dict(l=65, r=50, b=65, t=90)
)

# Mostrar la gráfica
fig.show()
