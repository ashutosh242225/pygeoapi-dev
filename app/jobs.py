import threading
import uuid
import logging
from shapely.geometry import shape, mapping
from app.models.process import BufferProcess, IntersectionProcess, DifferenceProcess, NearProcess

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

jobs = {}

def create_job(process_id, input_data):
    job_id = str(uuid.uuid4())
    thread = threading.Thread(target=run_job, args=(job_id, process_id, input_data))
    jobs[job_id] = {"status": "running", "result": None}
    thread.start()
    return job_id

def run_job(job_id, process_id, input_data):
    try:
        logger.debug(f"Running job {job_id} with process_id {process_id}")
        if process_id == "buffer":
            process = BufferProcess()
            feature = input_data['feature']
            distance = input_data['distance']
            result_feature = process.execute(feature, distance)
        elif process_id == "intersection":
            process = IntersectionProcess()
            feature1 = input_data['feature1']
            feature2 = input_data['feature2']
            result_feature = process.execute(feature1, feature2)
        elif process_id == "difference":
            process = DifferenceProcess()
            feature1 = input_data['feature1']
            feature2 = input_data['feature2']
            result_feature = process.execute(feature1, feature2)
        elif process_id == "near":
            process = NearProcess()
            feature = input_data['feature']
            collection = input_data['collection']
            result_feature = process.execute(feature, collection)
        else:
            raise ValueError(f"Invalid process_id {process_id}")

        jobs[job_id] = {"status": "completed", "result": result_feature}
        logger.debug(f"Job {job_id} completed successfully with result: {result_feature}")
    except Exception as e:
        jobs[job_id] = {"status": "failed"}
        logger.error(f"Job {job_id} failed with exception: {e}", exc_info=True)

def get_job_status(job_id):
    return jobs.get(job_id, {"status": "not_found"})