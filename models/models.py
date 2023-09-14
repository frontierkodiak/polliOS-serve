# PolliOS.backend.models.models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class PodRecord(Base):
    __tablename__ = 'pod_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), index=True)
    # type = Column(String(64), index=True)
    address = Column(String(64))
    address_type = Column(String(64))
    swarm_name = Column(String(64), index=True)
    retry_connection_period = Column(Integer)
    
    # Stream params
    stream_type = Column(String(64))
    downsample_fps = Column(Integer)
    connection_type = Column(String(64))
    rtsp_port = Column(Integer)
    buffer_size = Column(Integer)
    stream_address = Column(String(64))
    snapshot_address = Column(String(64))
    get_snapshot_interval = Column(Float)
    
    # Pod status
    connection_status = Column(String(64), index=True)
    last_seen = Column(DateTime)
    queue_length = Column(Integer)
    total_frames = Column(Integer)
    last_L1_class = Column(String(64))
    last_L2_class = Column(String(64))
    # last_N_L1_classes = Column(String(1024))  # Stored as comma-separated string. Consider using a related table.
    # last_N_L2_classes = Column(String(1024))  # Stored as comma-separated string. Consider using a related table.
    total_specimens = Column(Integer)
    last_specimen_created_time = Column(DateTime)
    
    # PodOS advanced features (0.4.x+)
    get_config_endpoint = Column(String(64))
    restart_endpoint = Column(String(64))
    get_sensor_status_endpoint = Column(String(64))
    sensors_endpoint = Column(String(64))
    update_GPS_endpoint = Column(String(64))
    naptime_endpoint = Column(String(64))
    bedtime_endpoint = Column(String(64))
    shutdown_GPS_endpoint = Column(String(64))
    wakeup_GPS_endpoint = Column(String(64))
    
    # Update intervals
    get_config_interval = Column(Integer)
    get_sensor_status_interval = Column(Integer)
    get_sensors_interval = Column(Integer)
    get_update_GPS_interval = Column(Integer)
    get_snapshot_interval = Column(Float)
    
    # PodOS sensors
    camera_available = Column(Boolean)
    bme280_available = Column(Boolean)
    gps_available = Column(Boolean)
    gps_awake = Column(Boolean)
    battery_reader_available = Column(Boolean)
    
    # Sensor config
    bme280_scl_pin = Column(Integer)
    bme280_sda_pin = Column(Integer)
    gps_rx_pin = Column(Integer)
    gps_tx_pin = Column(Integer)
    gps_pwrctl_available = Column(Boolean)
    gps_pwrctl_pin = Column(Integer)
    battery_reader_pin = Column(Integer)
    jpg_quality = Column(Integer)
    
    # Sensor data
    location_name = Column(String(64), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    temperature = Column(Float)
    pressure = Column(Float)
    humidity = Column(Float)
    battery_level = Column(Float)
    rssi = Column(Integer)
    
    # PodOS management
    naptime_enabled = Column(Boolean)
    naptime_baseline = Column(Integer)
    bedtime_active = Column(Boolean, index=True)
    bedtime_enabled = Column(Boolean, index=True)
    bedtime_max_wait = Column(Integer)
    bedtime_start = Column(DateTime)
    bedtime_end = Column(DateTime)
    
    # PodOS metadata
    pod_name = Column(String(64), index=True)
    firmware_name = Column(String(64))
    firmware_version = Column(String(64))

    
class SpecimenRecord(Base):
    __tablename__ = 'specimen_record'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    ## Stage 1 (detection)
    bboxLL_x = Column(Integer)
    bboxLL_y = Column(Integer)
    bboxUR_x = Column(Integer)
    bboxUR_y = Column(Integer)
    S1_score = Column(Float, index=True)
    S1_tag = Column(String(64), index=True)
    S1_class = Column(String(255))

    ## Stage 2: (classification)
    S2_tag = Column(String(64), index=True)
    S2_taxonID = Column(String(64), index=True)
    S2_taxonID_str = Column(String(255), index=True)
    S2_taxonID_score = Column(Float, index=True)
    S2_taxonRank = Column(String(64), index=True)
    
    ## Taxa
    L10_taxonID = Column(String(64), index=True)
    L10_taxonID_str = Column(String(255), index=True)
    L10_taxonScore = Column(Float, index=True)
    
    L20_taxonID = Column(String(64), index=True)
    L20_taxonID_str = Column(String(255))
    L20_taxonScore = Column(Float, index=True)
    
    L30_taxonID = Column(String(64), index=True)
    L30_taxonID_str = Column(String(255))
    L30_taxonScore = Column(Float, index=True)
    
    L40_taxonID = Column(String(64), index=True)
    L40_taxonID_str = Column(String(255))
    L40_taxonScore = Column(Float)
    
    L50_taxonID = Column(String(64), index=True)
    L50_taxonID_str = Column(String(255))
    L50_taxonScore = Column(Float, index=True)
    
    ## Plausibility / anomaly detection
    S2a_score = Column(Float, index=True)
    S2a_tag = Column(String(64), index=True)
    
    ## Media
    mediaID = Column(String(255))
    mediaPath = Column(String(255))
    mediaType = Column(String(64))
    height_px = Column(Integer)
    width_px = Column(Integer)
    media_persist_policy = Column(String(64))
    
    ## Frame    
    timestamp = Column(DateTime, index=True)
    run_name = Column(String(64), index=True)
    podID = Column(String(64), index=True)
    swarm_name = Column(String(64), index=True)
    
    ## Location
    lat = Column(Float, index=True)
    lon = Column(Float, index=True)
    loc_name = Column(String(64), index=True)


class FrameRecord(Base):
    # NOTE: These are only used in PolliOS Lite. 
    # Base PolliOS sticks to pure python FrameCard objects.
    __tablename__ = 'frame_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mediaID = Column(String(255))
    mediaType = Column(String(64))
    height_px = Column(Integer)
    width_px = Column(Integer)
    persist_policy = Column(String(64))
    timestamp = Column(DateTime, index=True)
    run_name = Column(String(64), index=True)
    podID = Column(String(64), index=True)
    swarm_name = Column(String(64), index=True)
    lat = Column(Float, index=True)
    lon = Column(Float, index=True)
    loc_name = Column(String(64), index=True)
    processed = Column(Boolean, index=True)
    queued = Column(Boolean, index=True)

class SensorRecord(Base):
    __tablename__ = 'sensor_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, index=True)
    podID = Column(String(64), index=True)
    # GPS
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    altitude = Column(Float, index=True)
    # BME280
    temperature = Column(Float, index=True)
    humidity = Column(Float, index=True)
    pressure = Column(Float, index=True)
    # Battery
    battery_level = Column(Float, index=True)
    # RSSI
    rssi = Column(Float, index=True)