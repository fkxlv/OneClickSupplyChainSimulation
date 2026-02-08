import logging
import requests

import os
import json
import google.generativeai as genai

DNS_URL = "http://127.0.0.1:5000/registry"
genai.configure(api_key="AIzaSyAbeTivu3l0VBxX52fsnRjzTli-s98aNvo")
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
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    logger.debug("receive_from_sourcing: data=%s", data)
    if "ranked_suppliers" not in data or data["ranked_suppliers"] is None:
        logger.debug("receive_from_sourcing: missing ranked_suppliers")
        failed_to_negotiate()
        return

    manufacturer_agent = get_agent({"role": "manufacturer"})['matches'][0]
    if not manufacturer_agent or manufacturer_agent.get("endpoint") is None:
        logger.debug("receive_from_sourcing: manufacturer agent not found")
        failed_to_negotiate()
        return

    print("going through supplies")
    for supplier in data["ranked_suppliers"]:
        try:
            if negotiate_with_manufacturer(supplier, manufacturer_agent, model):
                print("success")
                success(supplier, manufacturer_agent)
                break
        except Exception:
            logger.exception("Error negotiating with supplier %s", supplier)

def create_email(supplier, model):
    prompt = f"""
    SYSTEM
    You are a procurement specialist writing professional supplier emails.
    Return ONLY the email body text.
    No subject line. No markdown. No JSON. No explanations.

    USER
    Write a clean, concise, and professional email to the supplier below.
    We want to purchase from them and request a formal quotation.
    Mention the supplier name, the capabilities, and ask for:

    total price for the order
    lead time
    payment terms
    shipping terms (Incoterms)
    certifications / QA details

    Keep it short, polite, and business-like. The information about supplier:
    {supplier}
    """

    try:
        response = model.generate_content(prompt)
    
        text = response.text.strip()

        print("___THE EMAIL____")
        print(text)
        
        return text

    except Exception as e:
        print(f"!!! LLM FAIL: {e}")
        return """
            Dear {supplier["name"]},
            We would like to purschase your product. Can you send us the agreement details and costs please.
            Best regards
        """

def negotiate_with_manufacturer(supplier, manufacturer, model):
    logger.debug("negotiate_with_manufacturer: supplier=%s manufacturer=%s", supplier, manufacturer)
    
    email = create_email(supplier, model)

    try:
        # TODO: change to a valid request -- keep emailing behavior for now
        response = requests.get(manufacturer["endpoint"] + "/email", json=email)
        status = getattr(response, "status_code", None)
        logger.debug("negotiate_with_manufacturer: email status=%s", status)
        if status != 200:
            return False
        return True
    except Exception:
        logger.exception("negotiate_with_manufacturer: emailing failed")
        return False

def success(supplier, manufacturer):
    logger.debug("success: supplier=%s manufacturer=%s", supplier, manufacturer)


def failed_to_negotiate():
    logger.debug("failed_to_negotiate called")