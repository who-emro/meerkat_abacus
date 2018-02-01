import logging
from celery import Celery
import time

from meerkat_abacus.consumer import celeryconfig
from meerkat_abacus.consumer import database_setup
from meerkat_abacus.consumer import get_data
from meerkat_abacus.config import get_config
from meerkat_abacus import util
from meerkat_abacus.pipeline_worker.processing_tasks import process_data


config = get_config()

logging.getLogger().setLevel(logging.INFO)

app = Celery()
app.config_from_object(celeryconfig)


# Initial Setup

database_setup.set_up_database(False, True, config)


logging.info("Starting initial setup")
engine, session = util.get_db_engine(config.DATABASE_URL)


if config.initial_data_source == "AWS_S3":
    get_data.download_data_from_s3(config)
    get_function = util.read_csv_filename
elif config.initial_data_source == "LOCAL_CSV":
    get_function = util.read_csv_filename
elif config.initial_data_source == "FAKE_DATA":
    get_function = util.read_csv_filename
    util.create_fake_data.create_fake_data(session,
                                           config,
                                           write_to="file")
elif config.initial_data_source in ["AWS_RDS", "LOCAL_RDS"]:
    get_function = util.get_data_from_rds_persistent_storage
else:
    raise AttributeError(f"Invalid source {config.initial_data_source}")

get_data.read_stationary_data(get_function, session, engine, config)
session.close()
engine.dispose()


# Real time

while True:
    if config.stream_data_source == "AWS_S3":
        get_data.download_data_from_s3(config)
        get_data.read_stationary_data(util.read_csv_filename,
                                      session, engine, config)
        time.sleep(config.data_stream_interval)
    elif config.stream_data_source == "FAKE_DATA":
        logging.info("Sending fake data")
        if config.fake_data_generation == "INTERNAL":
            new_data = []
            for form in config.country_config["tables"]:
                data = util.create_fake_data.get_new_fake_data(form=form,
                                                                    session=session, N=10,
                                                                    param_config=config,
                                                                    dates_is_now=True)
                new_data = [{"form": form, "data": d[0]} for d in data]
            process_data.delay(new_data)
        else:
            raise NotImplementedError("Not yet implemented")
        logging.info("Sleeping")
        time.sleep(config.fake_data_interval)
