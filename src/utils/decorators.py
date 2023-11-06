import sys
import time
from functools import wraps


class SendSQSError(Exception):
    def __init__(self, message_attributes):
        self.message_attribute = message_attributes

    def __str__(self):
        return f"Send SQS failed on {self.message_attribute}"


class MaxRetriesExceededError(Exception):
    pass


def retry(max_retries=3, wait=1):
    def decorator_retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    retries += 1
                    time.sleep(wait)

            raise MaxRetriesExceededError(
                f"Maximum retries ({max_retries}) reached for {func.__name__}."
            )

        return wrapper

    return decorator_retry


def boto_error_handler(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except SendSQSError as error:
                logger.critical(error)

            except Exception as error:
                message = error.response["Error"]["Message"]

                error_messages = {
                    "AccessDenied": (
                        "Double check the IAM user used in the server. "
                        "Ensure it has sufficient permission"
                    ),
                    "ReceiptHandle": "Message receipt handle is expired.",
                    "ContentBasedDeduplication": (
                        "ContentBasedDeduplication is disabled in queue."
                        " Kindly coordinate with devops team to enable."
                    ),
                }

                for error_message in error_messages.keys():
                    if error_message in message:
                        logger.critical(
                            "Unable to perform %s. %s",
                            func.__name__,
                            message,
                            exec_info=True,
                        )
                        sys.exit(0)

                logger.critical(
                    "An error occured in %s, message: %s",
                    func.__name__,
                    message,
                    exc_info=True,
                )

        return wrapper

    return decorator
