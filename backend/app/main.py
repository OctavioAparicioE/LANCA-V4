from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, File, UploadFile
from app.models import DatosMedicionPrincipal, StartStop, VariablesAntena, Mediciones, PuntosMedicion, Frecuencias
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os
import pymysql
import pyodbc
import pandas as pd
import numpy as np
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app import database
from fastapi import Request, Form, Depends
from fastapi.responses import HTMLResponse
from app.database import get_db_connection
from app.database2 import get_db_connec
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import mysql.connector
from fastapi.responses import HTMLResponse
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots


app = FastAPI()

# Obtén la ruta absoluta del directorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Configura el directorio para los templates dentro de la carpeta frontend
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "../../frontend"))
# Monta el directorio estático dentro de la carpeta frontend/src
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "../../frontend/src")), name="static")



#######################################

# Ruta GET para mostrar la página con los datos iniciales (vacíos)
@app.get("/identificador")
def get_datos_medicion(request: Request, db: Session = Depends(get_db_connec)):
    todos_los_identificadores = db.query(DatosMedicionPrincipal).all()  # Todos los identificadores
    return templates.TemplateResponse("identi.html", {"request": request, "datos": [], "todos_los_identificadores": todos_los_identificadores})

# Ruta para mostrar el formulario de login (GET)
@app.get("/index")
def login_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta para mostrar el formulario de login (GET)
@app.get("/prueba")
def login_form(request: Request):
    return templates.TemplateResponse("identificador.html", {"request": request})

# Ruta POST para manejar la búsqueda
@app.post("/buscar")
def buscar_datos_medicion(request: Request, identificador: str = Form(...), db: Session = Depends(get_db_connec)):
    # Consulta todos los identificadores para que el selector siempre esté lleno
    todos_los_identificadores = db.query(DatosMedicionPrincipal).all()

    # Lógica para la búsqueda
    if identificador == "todos":  # Mostrar todos los registros
        datos = db.query(DatosMedicionPrincipal).all()
    elif identificador:  # Mostrar solo los datos del identificador seleccionado
        datos = db.query(DatosMedicionPrincipal).filter(DatosMedicionPrincipal.identificador == identificador).all()
    else:
        datos = []

    return templates.TemplateResponse("identi.html", {"request": request, "datos": datos, "todos_los_identificadores": todos_los_identificadores})



@app.get("/detalles")
def mostrar_detalles(request: Request, id: int, db: Session = Depends(get_db_connec)):
    # Consulta los datos de DatosMedicionPrincipal usando el ID|
    dato = db.query(DatosMedicionPrincipal).filter(DatosMedicionPrincipal.id_datos_medicion == id).first()

    if not dato:    
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # Consulta los datos de StartStop usando el identificador del dato
    # Asegúrate de que tu modelo DatosMedicionPrincipal esté correctamente relacionado con StartStop
    start_stop_data = db.query(StartStop).filter(StartStop.id_start_stop == dato.id_start_stop).all()

    # Consulta los datos de VariablesAntena usando el id_variables del dato
    variables_data = db.query(VariablesAntena).filter(VariablesAntena.id_variables == dato.id_variables).first()

    # Consulta adicional de PuntosMedicion filtrando por identificador del dato
    from sqlalchemy import desc

    puntos_medicion_data = db.query(
        PuntosMedicion.scan, 
        PuntosMedicion.amplitud4, 
        PuntosMedicion.fase4
    ).join(
        Mediciones, PuntosMedicion.id_medicion == Mediciones.id_medicion
    ).filter(
        Mediciones.identificador == dato.identificador
    ).order_by(
        PuntosMedicion.amplitud4.desc()
    ).limit(3).all()


    ##############CONSULTAS DE FRECUENCIAS ############## ############## ############## ##############

    frecuencias_data = db.query(
        Frecuencias.frecuencia, 
    ).join(Mediciones, Frecuencias.id_medicion == Mediciones.id_medicion
    ).filter(Mediciones.identificador == dato.identificador).all()


    ####################################### CONSULA DATOS GRAFICAS

    grafica_data = db.query(
        PuntosMedicion.scan, 
        PuntosMedicion.amplitud4, 
        StartStop.scan_start,
        StartStop.scan_stop,
        StartStop.step_start,
        StartStop.step_stop,
        StartStop.point_scan,
        StartStop.point_step
    ).join(
        Mediciones, PuntosMedicion.id_medicion == Mediciones.id_medicion
    ).join(
        StartStop, PuntosMedicion.id_start_stop == StartStop.id_start_stop
    ).filter(
     Mediciones.identificador == dato.identificador
    ).order_by(
       PuntosMedicion.amplitud4.desc()
    ).all()
    
##########################################################    GRAFICAS 3D, AZIMUTH & ELEVATION    ##########################################################
    # Consultar datos de StartStop
    result_graficas = db.query(
        StartStop.scan_start,
        StartStop.scan_stop,
        StartStop.step_start,
        StartStop.step_stop,
        StartStop.point_scan,
        StartStop.point_step
    ).join(
        DatosMedicionPrincipal
    ).filter(
        DatosMedicionPrincipal.identificador == dato.identificador
    ).all()

    if not result_graficas:
        raise HTTPException(status_code=404, detail="Datos no encontrados para el identificador")

    # Consultar datos de PuntosMedicion
    puntos_medicion_data_graficas = db.query(
        PuntosMedicion.scan,
        PuntosMedicion.rinc,
        PuntosMedicion.amplitud4
    ).join(
        Mediciones, PuntosMedicion.id_medicion == Mediciones.id_medicion
    ).filter(
        Mediciones.identificador == dato.identificador  # Filtrado por identificador
    ).all()

    # Extraer los valores de los datos de PuntosMedicion
    amplitud4_values = [p.amplitud4 for p in puntos_medicion_data_graficas]
    rinc_values = [p.rinc for p in puntos_medicion_data_graficas]
    scan_values = [p.scan for p in puntos_medicion_data_graficas]

    # Extraer datos de `result` para los límites
    scan_start = result_graficas[0].scan_start
    scan_stop = result_graficas[0].scan_stop
    step_start = result_graficas[0].step_start
    step_stop = result_graficas[0].step_stop
    point_scan = int(result_graficas[0].point_scan)  # Asegurarse de que sea entero
    point_step = int(result_graficas[0].point_step)  # Asegurarse de que sea entero

    radiation_df = pd.DataFrame(
        {"Bin4Amptd": amplitud4_values, "Rinc": rinc_values, "Scan": scan_values}
    )

    # Limitar amplitud
    radiation_df["Bin4Amptd"] = np.where(radiation_df["Bin4Amptd"] > -10, radiation_df["Bin4Amptd"], -10)

    # Crear DataFrame 3D
    radiation3d = pd.DataFrame()
    for i in range(point_scan):
        scan_data = radiation_df[radiation_df["Scan"] == i].set_index("Rinc")
        radiation3d[i] = scan_data["Bin4Amptd"]

    # Ejes
    x = np.linspace(scan_start, scan_stop, point_scan)  # Eje X
    y = np.linspace(step_start, step_stop, point_step)  # Eje Y

    # Crear subgráficas
    fig1 = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Patrón de Radiacíon", "Perfil Azimut", "Perfil Elevación"),
        specs=[[{'type': 'surface'}, {'type': 'scatter'}, {'type': 'scatter'}]]
    )

    # Gráfico 3D (fig1)
    fig1.add_trace(
        go.Surface(
            z=radiation3d.values, 
            x=x, 
            y=y, 
            colorscale='Viridis',  # Esquema de colores mejorado
            colorbar=dict(title="", tickvals=[-40, -30, -20,-10, 0, 10, 20, 30, 40], ticktext=["-40", "-30", "-20","-10", "0", "10", "20", "30", "40"]),
            contours=dict(
                z=dict(show=True, usecolormap=True, highlightcolor="yellow", project_z=True)
            )
        ),
        row=1, col=1
    )

    # Títulos y etiquetas para el gráfico 3D
    fig1.update_layout(
        title="",
        scene=dict(
            xaxis_title="Scan (m)",
            yaxis_title="Step (m)",
            zaxis_title="Amplitud Bin4"
        ),
        height=600,
        template="plotly_dark"  # Fondo oscuro
    )

    # Gráfico Azimut
    plano = radiation3d.shape[1] // 2
    fig1.add_trace(
        go.Scatter(
            x=x, 
            y=radiation3d[plano], 
            mode='lines', 
            name='Azimut', 
            line=dict(color='royalblue', width=3)
        ),
        row=1, col=2
    )

    # Títulos y formato del gráfico Azimut
    fig1.update_xaxes(title_text="Scan (m)", row=1, col=2)
    fig1.update_yaxes(title_text="Amplitud Bin4", row=1, col=2)

    # Gráfico Elevación
    elevacion = radiation3d.T
    fig1.add_trace(
        go.Scatter(
            x=y, 
            y=elevacion[plano], 
            mode='lines', 
            name='Elevación', 
            line=dict(color='darkorange', width=3)
        ),
        row=1, col=3
    )

    # Títulos y formato del gráfico Elevación
    fig1.update_xaxes(title_text="Step (m)", row=1, col=3)
    fig1.update_yaxes(title_text="", row=1, col=3)

    # Crear otro gráfico 3D (fig2) con diferentes configuraciones
    fig2 = go.Figure(data=[go.Surface(z=radiation3d.values, x=x, y=y, colorscale='Viridis')])

    # Títulos y diseño para el segundo gráfico 3D
    fig2.update_layout(
        title="Patrón de Radisción",
        scene=dict(
            xaxis_title="Scan (m)",
            yaxis_title="Step (m)",
        ),
        template="plotly_dark",
        height=1800,  # Aumentar el tamaño del gráfico
        width=1200
    )

    # Convertir los gráficos a HTML
    graph_html1 = plotly.offline.plot(fig1, auto_open=False, output_type="div")


############################################################################################################################################################




    return templates.TemplateResponse("detalles.html", {
        "request": request,
        "dato": dato,
        "start_stop_data": start_stop_data,
        "variables_data": variables_data,
        "puntos_medicion_data": puntos_medicion_data,
        "frecuencias_data": frecuencias_data,
        "result_graficas" : result_graficas,
        "puntos_medicion_data_graficas" : puntos_medicion_data_graficas,
        "request": request,
        "x_values": x.tolist(),
        "y_values": y.tolist(),
        "z_values": radiation3d.values.tolist(),
        "graph_html1": graph_html1,

    })



# Ruta para mostrar el formulario de login (GET)
@app.get("/menu")
def login_form(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})

# Ruta para mostrar el formulario de login (GET)
@app.get("/index")
def login_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Ruta para mostrar el formulario de login (GET)
@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

###########################################################################################

###Login

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from app import database2 
from app.models import User  # Asegúrate de tener el modelo User definido

# Ruta para procesar el login (POST)
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(database2.get_db_connec)):
    # Consultar la base de datos para encontrar el usuario usando SQLAlchemy ORM
    user = db.query(User).filter(User.username == username).first()

    # Verificar si el usuario existe y si la contraseña es correcta
    if not user or user.password != password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    # Redirigir a la consola si el login es exitoso
    return RedirectResponse(url="/index", status_code=302)

################################################
##GENERAR PDF

# Ruta para mostrar el formulario de login (GET)
@app.get("/pdf")
def login_form(request: Request):
    return templates.TemplateResponse("pdfPage.html", {"request": request})

#########################################################################################


@app.post("/upload-mdb/")
async def upload_mdb(file: UploadFile = File(...)):
    try:
        # Guardar el archivo .MDB en el servidor
        file_location = f"C:/Users/pc03d/Desktop/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        # Ejecutar la lógica de procesamiento del archivo .MDB
        resultado = procesar_mdb(file_location)
        return {"mensaje": "Archivo procesado exitosamente", "resultado": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")



scan_stop_multiplicado = None
step_stop_multiplicado = None

def procesar_mdb(mdb_path):
    identificador = os.path.splitext(os.path.basename(mdb_path))[0]

    # Conectar a la base de datos MDB
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + mdb_path + ';'
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Leer los datos de la tabla RasterScan
    query_raster_scan = "SELECT * FROM RasterScan"
    df_raster_scan = pd.read_sql(query_raster_scan, conn)

    # Leer los datos de la tabla RSTimeStamp
    query_rstimestamp = "SELECT StartTime, StopTime FROM RSTimeStamp"
    df_rstimestamp = pd.read_sql(query_rstimestamp, conn)

    # Leer los datos de la tabla AcDF_MotionData
    query_rstimes = "SELECT [scan sector 1 start], [scan sector 1 stop], [scan sector 1 number], [step 1 sector 1 start], [step 1 sector 1 stop], [step 1 sector 1 number] FROM AcDF_MotionData"
    df_rstimes = pd.read_sql(query_rstimes, conn)

    ########################Tablas para llenar las tablas de frecuencias en la base de datos

    query_frequency = "SELECT [Frequency Type], Frequency, [Start Frequency], [Increment Frequency], [Stop Frequency] FROM AcDF_Frequency"
    df_frec = pd.read_sql(query_frequency, conn)
 

    query_freq_list = "SELECT Frequency FROM AcDF_FreqList"
    df_frec_list = pd.read_sql(query_freq_list, conn)


    ########################Tablas para llenar las tablas de frecuencias en la base de datos

    # Leer los datos de la tabla AcDF_InfoData
    query_rstimes = "SELECT [Created On], [Created By] FROM AcDF_InfoData"
    df_responsable = pd.read_sql(query_rstimes, conn)


    ############Dataframes tablas de frecuencias en la base de datos 
    
    ########################Tablas para llenar las tablas de frecuencias en la base de datos
    query_frequency = "SELECT [Frequency Type], Frequency, [Start Frequency], [Increment Frequency], [Stop Frequency] FROM AcDF_Frequency"
    df_frec = pd.read_sql(query_frequency, conn)
    
    query_freq_list = "SELECT Frequency FROM AcDF_FreqList"
    df_frec_list = pd.read_sql(query_freq_list, conn)

    ############Dataframes tablas de frecuencias en la base de datos 


    # Convertir la columna 'Created On' a datetime
    df_responsable['Created On'] = pd.to_datetime(df_responsable['Created On'], errors='coerce')

    # Convertir las columnas de fecha y hora Unix a datetime
    df_rstimestamp['StartTime'] = pd.to_datetime(df_rstimestamp['StartTime'], unit='s', errors='coerce')
    df_rstimestamp['StopTime'] = pd.to_datetime(df_rstimestamp['StopTime'], unit='s', errors='coerce')

    # Extraer las amplitudes y fases de los bins
    amplitudes_bin1 = df_raster_scan['Bin1Amptd'].values
    amplitudes_bin2 = df_raster_scan['Bin2Amptd'].values
    amplitudes_bin3 = df_raster_scan['Bin3Amptd'].values
    amplitudes_bin4 = df_raster_scan['Bin4Amptd'].values
    amplitudes_bin5 = df_raster_scan['Bin5Amptd'].values
    amplitudes_bin6 = df_raster_scan['Bin6Amptd'].values
    fase_bin1 = df_raster_scan['Bin1Phase'].values
    fase_bin2 = df_raster_scan['Bin2Phase'].values
    fase_bin3 = df_raster_scan['Bin3Phase'].values
    fase_bin4 = df_raster_scan['Bin4Phase'].values
    fase_bin5 = df_raster_scan['Bin5Phase'].values
    fase_bin6 = df_raster_scan['Bin6Phase'].values

    scan_r = df_raster_scan['Scan'].values
    rinc_r = df_raster_scan['Rinc'].values
    freq_r = df_raster_scan['Freq'].values

    #STOP START 
    scan_start_value = df_rstimes['scan sector 1 start'].values[0]
    scan_stop_value = df_rstimes['scan sector 1 stop'].values[0]
    step_start_value = df_rstimes['step 1 sector 1 start'].values[0]
    step_stop_value = df_rstimes['step 1 sector 1 stop'].values[0]
    number_scan_value = df_rstimes['scan sector 1 number'].values[0]
    number_step_value = df_rstimes['step 1 sector 1 number'].values[0]


    # Multiplicar los valores
    scan_stop_multiplicado = scan_stop_value * 2 if scan_stop_value is not None else None
    step_stop_multiplicado = step_stop_value * 2 if step_stop_value is not None else None

    
    #Datos principales
    fecha_hora = df_responsable['Created On'].values
    responsable_medicion = df_responsable['Created By'].values

    # Calcular la ganancia máxima global en dB
    ganancia_max_global_db = np.max(amplitudes_bin4)

    # Calcular la diferencia entre StopTime y StartTime en la tabla RSTimeStamp
    total_segundos = 0

    for _, fila in df_rstimestamp.iterrows():
        start_time = fila['StartTime']
        stop_time = fila['StopTime']

        if pd.notna(start_time) and pd.notna(stop_time):
            # Calcular la diferencia en segundos
            diferencia = (stop_time - start_time).total_seconds()
            total_segundos += diferencia

    # Convertir total_segundos a horas, minutos y segundos
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    # Formatear el tiempo en el formato requerido
    tiempo_medicion_formateado = f"{horas:.1f} hrs. {minutos:.1f} min. {segundos:.2f} seg."

    polarizacion = 10



    # Conectar a la base de datos MySQL
    conexion = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='Passw0rd',
        database='camara_anecoica'
    )
    cursor = conexion.cursor()

    try:
        # Iniciar la transacción
        conexion.begin()

        # Insertar en la tabla mediciones
        cursor.execute("INSERT INTO mediciones (identificador) VALUES (%s)", (identificador,))

        # Obtener el id_medicion generado
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_medicion_actual = cursor.fetchone()[0]

        # Insertar en la tabla frecuencias


        # Procesar y agregar frecuencias
        frequencies_processed = []
        
        for index, row in df_frec.iterrows():
            freq_type = row['Frequency Type']
            if freq_type == 0:  # Frecuencia única
                frequencies_processed.append((id_medicion_actual, row['Frequency']))

            elif freq_type == 1:  # Rango de frecuencias
                start = row['Start Frequency']
                stop = row['Stop Frequency']
                increment = row['Increment Frequency']
                current_freq = start
                while current_freq <= stop:
                    frequencies_processed.append((id_medicion_actual, current_freq))
                    current_freq += increment
                if current_freq - increment < stop:
                    frequencies_processed.append((id_medicion_actual, stop))

            elif freq_type == 2:  # Lista de frecuencias
                freq_list = [(id_medicion_actual, row['Frequency'])]
                freq_list.extend([(id_medicion_actual, freq) for freq in df_frec_list['Frequency'].tolist() if freq != row['Frequency']])
                frequencies_processed.extend(freq_list)

        # Insertar frecuencias en la tabla 'frecuencias'
        insert_query = "INSERT INTO frecuencias (id_medicion, frecuencia) VALUES (%s, %s)"
        cursor.executemany(insert_query, frequencies_processed)
    


        # Insertar en la tabla variables_antena

        cursor.execute(
            "INSERT INTO variables_antena (polarizacion, ganancia, tiempo_medicion) VALUES (%s, %s, %s)",
            (polarizacion, ganancia_max_global_db, tiempo_medicion_formateado)
              )
        
        cursor.execute(
            "INSERT INTO start_stop (scan_start, scan_stop, step_start, step_stop, total_scan, total_step, point_scan, point_step) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (scan_start_value, scan_stop_value, step_start_value, step_stop_value, scan_stop_multiplicado, step_stop_multiplicado, number_scan_value, number_step_value)
              )
        
    
        # Obtener el último id de la tabla variables_antena
        cursor.execute("SELECT id_variables FROM variables_antena ORDER BY id_variables DESC LIMIT 1")
        id_variables_antena_actual = cursor.fetchone()
        print(f"Último ID en variables_antena: {id_variables_antena_actual}")

        # Obtener el último id de la tabla variables_antena
        cursor.execute("SELECT identificador FROM mediciones ORDER BY identificador DESC LIMIT 1")
        id_dentificador = cursor.fetchone()
        print(f"Último ID en variables_antena: {id_dentificador}")

        # Obtener el último id de la tabla variables_antena
        cursor.execute("SELECT id_start_stop FROM start_stop ORDER BY id_start_stop DESC LIMIT 1")
        id_stopstart = cursor.fetchone()
        print(f"Último ID en variables_antena: {id_stopstart}")

    
        # Insertar datos en la base de datos
        for i in range(len(df_responsable)):
            fecha_hora = df_responsable['Created On'].iloc[i]
            responsable_medicion = df_responsable['Created By'].iloc[i]

            if fecha_hora and responsable_medicion:
                cursor.execute(
                    "INSERT INTO datos_medicion_principal (id_variables, identificador, id_start_stop, fecha_hora, responsable_medicion) VALUES (%s, %s, %s, %s, %s)",
                    (id_variables_antena_actual, identificador, id_stopstart, fecha_hora, responsable_medicion)
                )
            else:
                print(f"Datos no válidos en la fila {i}: fecha_hora={fecha_hora}, responsable_medicion={responsable_medicion}")

         # Insertar en la tabla puntos_medicion
        for i in range(len(amplitudes_bin4)):
            cursor.execute(
            "INSERT INTO puntos_medicion (id_medicion, id_start_stop ,scan, rinc, frecuencia, amplitud1, fase1, amplitud2, fase2, amplitud3, fase3, amplitud4, fase4, amplitud5, fase5, amplitud6, fase6) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (id_medicion_actual, id_stopstart,scan_r[i], rinc_r[i], freq_r[i], amplitudes_bin1[i], fase_bin1[i], amplitudes_bin2[i], fase_bin2[i], amplitudes_bin3[i], fase_bin3[i], amplitudes_bin4[i], fase_bin4[i], amplitudes_bin5[i], fase_bin5[i], amplitudes_bin6[i], fase_bin6[i])
               )
            
        # Confirmar los cambios
        conexion.commit()
        return {"polarizacion": polarizacion, "ganancia": ganancia_max_global_db, "tiempo_medicion": tiempo_medicion_formateado}


    except Exception as e:
        # Revertir los cambios en caso de error
        conexion.rollback()
        raise Exception(f"Error durante la transacción: {e}")
    
    #Aqui hacemos el llenado de la base de datos 
    
    finally:
        # Cerrar conexiones
        cursor.close()
        conexion.close()

    
