import polars as pl
from fastapi import FastAPI, Header,Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import jwt
import datetime


app = FastAPI()

TOKEN_HS256 = "HS256"
TOKEN_KEY = "cheil_token" 

jwtTokenG=""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_file():
    save_route = "data/parquet/vehicles.parquet"
    df = pl.read_csv("data/vehicle.csv")
    df.write_parquet(save_route)

    df_lz = pl.scan_parquet(save_route)
    df_limpio = df_lz.drop_nulls()

    campos_calculos = [
        "compactness", "circularity", "distance_circularity", "radius_ratio",
        "pr.axis_aspect_ratio", "max.length_aspect_ratio", "scatter_ratio",
        "elongatedness", "pr.axis_rectangularity", "max.length_rectangularity",
        "scaled_variance", "scaled_variance.1", "scaled_radius_of_gyration",
        "scaled_radius_of_gyration.1", "skewness_about", "skewness_about.1",
        "skewness_about.2", "hollows_ratio"
    ]

    # if "compactness" in df_limpio:
    desviacion_estandar_df = (
                df_limpio.groupby("class")
                .agg( **{campo: pl.col(campo).std() for campo in campos_calculos})
    )

    promedio_df = (
                df_limpio.groupby("class")
                .agg(
                    **{campo: pl.col(campo).mean() for campo in campos_calculos}
                )
    )
    return df_limpio,desviacion_estandar_df, promedio_df         

#decode token to get claims
def secure(token):
    decoded_token = jwt.decode(token, TOKEN_KEY, algorithms=TOKEN_HS256)
    # this is often used on the client side to encode the user's email address or other properties
    return decoded_token
    


@app.post("/signIn")
def login(email, password):
    global jwtTokenG
    if email == "user@cheil.com" and password == "superadmin":
        # Create a JWT token with a subject claim "admin" and an expiration time of 1 hour
        payload = {"email": email, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}
        jwtTokenG = jwt.encode(payload, TOKEN_KEY, algorithm=TOKEN_HS256)
        response = {"status":"200","token":jwtTokenG}
        return response
    else:
        return {"message":"please login again","status":"400"}

@app.post("/SignOut")
def logout():
    global jwtTokenG
    jwtTokenG=""
    response = {"status":"200","message":"Logged out with succesfull!"}
    return response

@app.get("/getVehicles")
async def getVehicles(token: str = Header(None)):
    global jwtTokenG, df_limpio
    try:
        # change the token bytes to str
        token_bytes_str = jwtTokenG.decode('utf-8')

        if token == token_bytes_str:
            # using lazyFrames of polars convert to query and show results
            df_limpio,desviacion_estandar_df, promedio_df = process_file()
            df_limpio_result = df_limpio.collect().to_dicts()
            desviacion_estandar_df_result = desviacion_estandar_df.collect().to_dicts()
            promedio_df_result = promedio_df.collect().to_dicts()
            response = {"status":"200","vehicles_data": df_limpio_result, "std_data": desviacion_estandar_df_result,"avg_data":promedio_df_result}
            return response
        else:
            return {"message": "Invalid token", "status": "400"}
    except:
        return {"message": "Unauthorized Access, please login!", "status": "404"}