import logging
import requests
import manufacturer as manufacturer_module

DNS_URL = "http://127.0.0.1:5000/registry"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_agent(query):
    logger.debug("get_agent: query=%s", query)
    try:
        resp = requests.post(DNS_URL + "/discover", json=query, timeout=5)
        resp.raise_for_status()
        try:
            result = resp.json()
            logger.debug("get_agent: response json=%s", result)
            return result
        except ValueError:
            logger.debug("get_agent: non-json response: %s", resp.text)
            return None
    except Exception:
        logger.exception("get_agent: request failed")
        return None


def receive_from_sourcing(data):
    logger.debug("receive_from_sourcing: data=%s", data)
    if "ranked_suppliers" not in data or data["ranked_suppliers"] is None:
        logger.debug("receive_from_sourcing: missing ranked_suppliers")
        failed_to_negotiate()
        return

    manufacturer_agent = get_agent({"role": "manufacturer"})
    if not manufacturer_agent or manufacturer_agent.get("endpoint") is None:
        logger.debug("receive_from_sourcing: manufacturer agent not found")
        failed_to_negotiate()
        return

    for supplier in data["ranked_suppliers"]:
        try:
            if negotiate_with_manufacturer(supplier, manufacturer_agent):
                success(supplier, manufacturer_agent)
                break
        except Exception:
            logger.exception("Error negotiating with supplier %s", supplier)


def negotiate_with_manufacturer(supplier, manufacturer):
    logger.debug("negotiate_with_manufacturer: supplier=%s manufacturer=%s", supplier, manufacturer)
    payload = "Can I buy it?"
    try:
        # TODO: change to a valid request -- keep emailing behavior for now
        email = manufacturer_module.main.send_email(payload)
        status = getattr(email, "status_code", None)
        logger.debug("negotiate_with_manufacturer: email status=%s", status)
        if status != 200:
            return False
        return True
    except Exception:
        logger.exception("negotiate_with_manufacturer: emailing failed")
        return False


def success(supplier, manufacturer):
    logger.debug("success: supplier=%s manufacturer=%s", supplier, manufacturer)
    planner = get_agent({"role": "planner"})
    if not planner or planner.get("endpoint") is None:
        logger.error("success: planner agent not found")
        return

    try:
        req = requests.post(planner["endpoint"] + "/success", json={"supplier": supplier})
        logger.debug("success: planner responded status=%s", getattr(req, "status_code", None))
    except Exception:
        logger.exception("success: failed to notify planner")


def failed_to_negotiate():
    logger.debug("failed_to_negotiate called")
    planner = get_agent({"role": "planner"})
    if not planner or planner.get("endpoint") is None:
        logger.error("failed_to_negotiate: planner agent not found")
        return
    try:
        req = requests.post(planner["endpoint"] + "/failed")
        logger.debug("failed_to_negotiate: planner responded status=%s", getattr(req, "status_code", None))
    except Exception:
        logger.exception("failed_to_negotiate: request failed")