import logging

# Set up a basic logger for stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("llm_logger")
