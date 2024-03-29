# PolliServer.server.py
import os
import signal
import subprocess
from typing import Optional, List
from aiohttp import ClientSession, ClientTimeout
from fastapi import HTTPException
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func
import traceback
import datetime


from PolliServer.constants import *
from PolliServer.backend.get_db import get_db
from PolliServer.helpers.grabbers import *
from PolliServer.helpers.getters import get_frame_counts, get_specimen_counts
from PolliServer.helpers.stat_getters import get_frame_log_stats, get_specimen_log_stats
from models.models import SpecimenRecord
from PolliServer.logger.logger import LoggerSingleton

logger = LoggerSingleton().get_logger()


app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StripAPIPrefixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if debug mode is active
        if os.getenv("DEBUG_MODE") == "true":
            if request.url.path.startswith("/api/"):
                # Modify the path to strip '/api/'
                path = request.url.path[len("/api/"):]
                request.scope["path"] = "/" + path
        response = await call_next(request)
        return response

app.add_middleware(StripAPIPrefixMiddleware)

time = datetime.datetime.now()
print(f"Server started at {time.strftime('%Y-%m-%d %H:%M:%S')}")

# --- Management API endpoints --- #

@app.get("/shutdown")
async def shutdown_server():
    os.kill(os.getpid(), signal.SIGINT)
    return {"message": "Server shutting down"}

@app.get("/restart")
async def restart_server():
    os.kill(os.getpid(), signal.SIGHUP)
    return {"message": "Server restarting"}

@app.get("/debug")
async def set_debug_mode():
    os.environ["DEBUG"] = "true"
    os.kill(os.getpid(), signal.SIGHUP)
    return {"message": "Debug mode set and server restarting"}

# --- Minor (utility) API endpoints --- #

@app.get("/check_hub_connection")
async def check_hub_connection(hub_address: Optional[str] = "hub0"):
    url = f"http://{hub_address}/"
    timeout = ClientTimeout(total=5)  # 5 seconds timeout
    async with ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return {"status": "online"}
                else:
                    return {"status": "offline"}
        except Exception as e:
            logger.server_error(f"Error in check_hub_connection endpoint: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

# --- Minor (getter) API endpoints --- #

# @app.get("/podIDs")
# async def get_pod_ids(db: AsyncSession = Depends(get_db)):
#     try:
#         values = await db.execute(select(SpecimenRecord.podID).distinct())
#         values_list = [item for item in values.scalars().all()]
#         return sorted(values_list)
#     except SQLAlchemyError as e:
#         logger.server_error(f"Getter /podIDs SQLAlchemyError: {e}")
#         print(f"Getter /podIDs SQLAlchemyError: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

@app.get("/podIDs")
async def get_pod_ids(db: AsyncSession = Depends(get_db)):
    try:
        values = await db.execute(select(SpecimenRecord.podID).distinct())
        values_list = [item for item in values.scalars().all() if item is not None]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /podIDs SQLAlchemyError: {e}")
        print(f"Getter /podIDs SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/locations")
# async def get_locations(db: AsyncSession = Depends(get_db)):
#     try:
#         values = await db.execute(select(SpecimenRecord.loc_name).distinct())
#         values_list = [item[0] for item in values.scalars().all()]
#         return sorted(values_list)
#     except SQLAlchemyError as e:
#         logger.server_error(f"Getter /locations SQLAlchemyError: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

@app.get("/swarms")
async def get_swarms(db: AsyncSession = Depends(get_db)):
    try:
        values = await db.execute(select(SpecimenRecord.swarm_name).distinct())
        values_list = [item for item in values.scalars().all()]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /swarms SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/runs")
async def get_runs(db: AsyncSession = Depends(get_db)):
    try:
        values = await db.execute(select(SpecimenRecord.run_name).distinct())
        values_list = [item for item in values.scalars().all()]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /runs SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    


@app.get("/dates")
async def get_dates(db: AsyncSession = Depends(get_db)):
    try:
        # Extract distinct dates (ignoring time)
        dates = await db.execute(select(func.date(SpecimenRecord.timestamp)).distinct())
        # Convert datetime.date objects to string and sort them
        dates_list = sorted([date_obj.strftime('%Y-%m-%d') for date_obj in dates.scalars().all()])
        return dates_list
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /dates SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
    
@app.get("/frame_counts")
async def frame_counts_endpoint(podIDs: Optional[List[str]] = Query(None), 
                                hours: Optional[int] = Query(24),
                                db: AsyncSession = Depends(get_db)):
    try:
        # Initialize an empty dictionary to store the frame counts
        frame_counts = {}

        # Iterate over each podID
        for podID in podIDs:
            # Get the frame count for this podID
            count = await get_frame_counts(db, podID, hours)
            # Store the count in the dictionary
            frame_counts[podID] = count

        # Return the dictionary of frame counts
        return frame_counts
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /frame_counts SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))


        
# --- Major (grabber) API endpoints --- #

# Returns a swarm_status JSON swarm_status list
@app.get("/swarm-status")
async def swarm_status(db: AsyncSession = Depends(get_db)):
    try:
        return await grab_swarm_status(db)
    except Exception as e:
        logger.server_error(f"Error in swarm_status endpoint: {e}")
        traceback.print_exc()  # This will print the traceback to the console.
        raise HTTPException(status_code=500, detail="Internal server error")

# For SpecimenDetailHorizon
@app.get("/specimen-detail-timeline")
async def specimen_detail_timeline(start_date: Optional[str] = Query(None),
                        end_date: Optional[str] = Query(None),
                        podID: Optional[List[str]] = Query(None),
                        species_only: Optional[bool] = Query(False),
                        S1_score_thresh: Optional[float] = Query(0.0),
                        S2_score_thresh: Optional[float] = Query(0.0),
                        location: Optional[str] = Query(None),
                        S2a_score_thresh: Optional[float] = Query(0.0),
                        incl_images: Optional[bool] = Query(False),
                        db: AsyncSession = Depends(get_db)):

    try:
        specimen_detail_timeline = await grab_specimen_detail_timeline(db, start_date=start_date, end_date=end_date, podID=podID, 
                                                 location=location, species_only=species_only, 
                                                 S1_score_thresh=S1_score_thresh, S2_score_thresh=S2_score_thresh, 
                                                 S2a_score_thresh=S2a_score_thresh, incl_images=incl_images)
        return specimen_detail_timeline
    except Exception as e:
        logger.server_error(f"Error in specimen_detail_timeline endpoint: {e}")
        traceback.print_exc()  # This will print the traceback to the console.
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/clade-activity-array-data")
async def clade_activity_array_data(clade: str,
                                    start_date: Optional[str] = Query(None),
                                    end_date: Optional[str] = Query(None),
                                    taxonRank: Optional[int] = Query(10),
                                    S1_score_thresh: Optional[float] = Query(0.0),
                                    S2_score_thresh: Optional[float] = Query(0.0),
                                    S2a_score_thresh: Optional[float] = Query(0.0),
                                    n_bins: Optional[int] = Query(10),
                                    db: AsyncSession = Depends(get_db)):
    try:
        return await grab_clade_activity_array_data(db, clade, start_date, end_date, taxonRank, S1_score_thresh, S2_score_thresh, S2a_score_thresh, n_bins)
    except Exception as e:
        logger.server_error(f"Error in clade_activity_array_data endpoint: {e}")
        traceback.print_exc()  # This will print the traceback to the console.
        raise HTTPException(status_code=500, detail="Internal server error")
    
    
# For FrameLogHorizon
## Get the frame activity for a swarm for a given time span. Optionally filter by swarm_name and run_name.
### Frame log contains all frames generated by the swarm. FrameRecords has more metadata, but FrameRecords can be deleted by PolliOS if a specimen or event record isn't produced for that frame.
## Params: span (int, hours), n_bins (int, default=10), swarm_name (str, default=None), run_name (str, default=None)
## Returns: frame_log_array_data (list of lists). Each list contains: [time_bin_midpoint, count, podID]
@app.get("/frame-log-array-data")
async def frame_log_array_data(span: int = 24, n_bins: int = 10, swarm_name: Optional[str] = None, run_name: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    try:
        return await grab_frame_log_array_data(db, span, n_bins, swarm_name, run_name)
    except Exception as e:
        logger.server_error(f"Error in frame_log_array_data endpoint: {e}")
        traceback.print_exc()
        

# For FrameLogStats
## Get the total no. frames for a given time span and the previous time span. Optionally filter by swarm_name and run_name.
## Also return percentage change in frame count.
## Params: span (int, hours), swarm_name (str, default=None), run_name (str, default=None)
## Returns: frame_log_stats (dict): {'current': frame_count, 'previous': frame_count, 'change': percentage_change}
@app.get("/frame-log-stats")
async def frame_log_stats(span: int, swarm_name: Optional[str] = None, run_name: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    try:
        stats = await get_frame_log_stats(db, span, swarm_name, run_name)
        return stats
    except Exception as e:
        logger.server_error(f"Error in frame_log_stats endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
    
    
# For SpecimenLogHorizon
## Get total no. specimens for a given time span. Optionally filter by swarm_name and run_name.
## Params: span (int, hours), n_bins (int, default =10), swarm_name (str, default=None), run_name (str, default=None)
## Returns: specimen_log_array_data (list of lists). Each list contains: [time_bin_midpoint, count, podID]
@app.get("/specimen-log-array-data")
async def specimen_log_array_data(span: int = 24, n_bins: int = 10, swarm_name: Optional[str] = None, run_name: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    try:
        return await grab_specimen_log_array_data(db, span, n_bins, swarm_name, run_name)
    except Exception as e:
        logger.server_error(f"Error in specimen_log_array_data endpoint: {e}")
        traceback.print_exc()

# For SpecimenLogStats
## Get the total no. specimens for a given time span and the previous time span. Optionally filter by swarm_name and run_name.
## Also return percentage change in specimen count.
## Params: span (int, hours), swarm_name (str, default=None), run_name (str, default=None)
## Returns: specimen_log_stats (dict): {'current': specimen_count, 'previous': specimen_count, 'change': percentage_change}
@app.get("/specimen-log-stats")
async def specimen_log_stats(span: int, swarm_name: Optional[str] = None, run_name: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    try:
        stats = await get_specimen_log_stats(db, span, swarm_name, run_name)
        return stats
    except Exception as e:
        logger.server_error(f"Error in specimen_log_stats endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
    
# For WeatherLogHorizon
## Get the weather data for a given time span. Optionally filter by swarm_name.
## Params: span (int, hours), n_bins (int, default=10), swarm_name (str, default=None)
## Returns: weather_log_array_data (list of lists). Each list contains: [time_bin_midpoint, cloud_coverage, rain_last_3h, wind_degree, wind_speed, humidity, pressure, temperature, aqi, coi, nh3i, noi, no2i, o3i, so2i, pm2_5i, pm10i, uv_index]
@app.get("/weather-log-array-data")
async def weather_log_array_data(span: int = 24, n_bins: int = 10, swarm_name: Optional[str] = None, lite: bool = False, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to fetch weather log data, aggregated into time bins, optionally filtered by swarm_name.
    If 'lite' is True, only returns a subset of the weather data.

    Args:
        span (int): Time span in hours for which to fetch data.
        n_bins (int): Number of bins to divide the time span into.
        swarm_name (Optional[str]): Name of the swarm to filter by. Default is None.
        lite (bool): Whether to return a lite version of the data. Default is False.
    
    Returns:
        JSON response containing the weather data for each time bin.
    """
    try:
        weather_data = await grab_weather_log_array_data(db, span, n_bins, swarm_name, lite)
        return weather_data
    except Exception as e:
        logger.server_error(f"Error in weather_log_array_data endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")   
    
# NOTE: We are splitting this into frame-log-stats and specimen-log-stats
@app.get("/swarm-stats")
async def swarm_stats(podID: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    print("swarm_stats")
    try:
        # Initialize an empty dictionary to store the results
        results = {'podID': podID, 'frames': {}, 'specimens': {}}

        # Get the frame counts for the 24 and 72 hour spans
        for hours in [24, 72]:
            frame_counts = await get_frame_counts(db, hours, podID, compare=True)
            results['frames'][f'{hours}_hours'] = frame_counts

        # Get the specimen counts for the 24 and 72 hour spans
        for hours in [24, 72]:
            specimen_counts = await get_specimen_counts(db, hours, podID, compare=True)
            results['specimens'][f'{hours}_hours'] = specimen_counts

        # Return the results
        return results
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /api/swarm-stats SQLAlchemyError: {e}")
        print(f"Getter /api/swarm-stats SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
#### --- Asset download endpoints --- ####

@app.get("/models/{framework}/{model_name}")
async def download_model(model_name: str, framework: str):
    file_path = ""
    if framework == "torchserve":
        file_path = f"/models/ts/{model_name}.gz"
    elif framework == "onnx":
        file_path = f"/models/onnx/{model_name}.gz"
    elif framework == "tensorflow":
        file_path = f"/models/tf/{model_name}.gz"
    elif framework == "pkl":
        file_path = f"/models/pkl/{model_name}.gz"
    return FileResponse(file_path, media_type="application/gzip", filename=f"{model_name}.gz")


@app.get("/assets/{asset_name}")
async def download_asset(asset_name: str):
    file_path = f"/assets/{asset_name}.gz"
    return FileResponse(file_path, media_type="application/gzip", filename=f"{asset_name}.gz")