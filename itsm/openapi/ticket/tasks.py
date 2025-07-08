from celery import shared_task
from common.log import logger


@shared_task
def openapi_start_ticket(ticket, fields, from_ticket_id=None):
    try:
        logger.info(
            "[openapi_start_ticket] Start ticket, ticket id = {}".format(ticket.id)
        )
        ticket.do_after_create(fields, from_ticket_id)
        ticket.start()
    except Exception as e:
        logger.exception(
            "[openapi_start_ticket_error] Exception occurred, error message: {}, fields={}".format(
                e, fields
            )
        )
