
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger('ms')


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.debug("This is a debug message")
        logger.info("User accessed my_view")
        logger.warning("This is a warning")
        logger.error("An error occurred!")
        logger.critical("Critical system failure!")
