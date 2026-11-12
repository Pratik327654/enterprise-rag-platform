from app.core.logging_config import logger


def test_logging():
    logger.info("Enterprise RAG Platform logging test successful.")
    logger.warning("This is a sample warning.")
    logger.error("This is a sample error.")


if __name__ == "__main__":
    test_logging()