import time
import requests

import config
import log

logger = log.get_logger(__name__)

logger.info("Restarting Dynos")

api_url = f"https://api.heroku.com/apps/{config.settings.heroku_app_name}/dynos"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/vnd.heroku+json; version=3",
    "Authorization": f"Bearer {config.settings.heroku_oauth_token}",
}

r = requests.get(api_url, headers=headers)
dynos = r.json()

dyno_names = [d["name"] for d in dynos]
logger.info(f"Restarting {len(dynos)} dynos: {dyno_names}")

for d_name in dyno_names:
    logger.info(f"Restarting Dyno[{d_name}]")
    dyno_api_url = f"{api_url}/{d_name}"

    time.sleep(2)
    deleted_r = requests.delete(dyno_api_url, headers=headers)
    response_status = "OK" if deleted_r.status_code == 202 else "FAILED"
    logger.info(f"Dyno[{d_name}] restart response status = {response_status}")
    if response_status == "FAILED":
        break

    logger.info(f"Waiting for Dyno[{d_name}] to restart")
    for _ in range(10):
        time.sleep(5)
        info = requests.get(dyno_api_url, headers=headers).json()
        dyno_state = info["state"]
        if dyno_state == "up":
            logger.info(f"Dyno[{d_name}] was successfully restarted")
            break
        else:
            logger.info(f"Dyno[{d_name}] state is `{dyno_state}`")
    else:
        logger.info(f"Dyno[{d_name}] didn't restart in the allotted time period")

logger.info("Restarts completed")
