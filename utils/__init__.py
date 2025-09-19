import os

from loguru import logger as lg

# Create .cache folder
if not os.path.exists(".cache"):
    os.makedirs(".cache")
    lg.info("Created .cache folder")
