import logging


# Ratio of concurrent calls per agent
DIAL_RATIO = 2

# Ratio of succesful to failed calls
SUCCESS_RATIO = 0.5

NUMBER_OF_AGENTS = 2

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
