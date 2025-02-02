from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
import os
import requests
import logging
import schedule
import time

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LOGIN_URL = "https://urbansportsclub.com/de/login"
STORAGE_STATE = "storage_state.json"

VENUE_URL = "https://urbansportsclub.com/de/venues/"
BOOKING_URL = "https://urbansportsclub.com/de/activities?class="
VENUE_URLS = {
    "Beat81 - Lindenthal": "beat81-lindenthal-indoor-workout",
    "Beat81 - Rudolfplatz": "beat81-rudolfplatz-indoor-workout-1",
    "Beat81 - Sülz": "beat81-sulz-indoor-workout-1",
    "Rocycle": "rocycle-koln-friesenplatz",
}

def send_pushover_message(title, message, date14ahead=(datetime.now() + timedelta(days=13)).strftime("%Y-%m-%d")):
    full_message = f"Checking for date {date14ahead}\n\n{message}"
    logging.info(f"Sending Pushover message with title: {title}")
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": full_message
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        logging.info("Message sent successfully")
    else:
        logging.error(f"Failed to send message: {response.text}")

def login(page):
    logging.info("Logging in")
    page.goto(LOGIN_URL)
    page.fill('input[name="email"]', EMAIL)
    page.fill('input[name="password"]', PASSWORD)
    page.click('input[type="submit"]')
    page.wait_for_selector("span.smm-header__customer-name")
    page.context.storage_state(path=STORAGE_STATE)
    logging.info("Login successful")

def is_session_valid(page):
    logging.info("Checking if session is valid")
    try:
        page.goto(VENUE_URL)
        page.wait_for_selector("span.smm-header__customer-name", timeout=5000)
        logging.info("Session is valid")
        return True
    except PlaywrightTimeoutError:
        logging.warning("Session is not valid")
        return False

def check_new_courses():
    logging.info("Starting to check new courses")
    date_14_days_ahead = (datetime.now() + timedelta(days=13)).strftime("%Y-%m-%d")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=STORAGE_STATE if os.path.exists(STORAGE_STATE) else None)
            page = context.new_page()

            if not os.path.exists(STORAGE_STATE) or not is_session_valid(page):
                logging.info("Session state not found or invalid, logging in")
                login(page)

            for venue_name, venue_url in VENUE_URLS.items():
                logging.info(f"Checking courses for venue: {venue_name}")
                page.goto(VENUE_URL + venue_url + "?date=" + date_14_days_ahead + "&plan_type=2")
                page.wait_for_selector("div.smm-class-snippet.row")

                course_divs = page.query_selector_all("div.smm-class-snippet.row")
                results = []
                for course_div in course_divs:
                    title_div = course_div.query_selector("div.title a")
                    time_div = course_div.query_selector("div.smm-class-snippet__class-time-plans-wrapper p")
                    appointment_id = course_div.get_attribute("data-appointment-id")
                    if title_div and time_div and appointment_id:
                        result = f"{time_div.inner_text()} - {title_div.inner_text()} - {BOOKING_URL}{appointment_id}"
                        results.append(result)
                        logging.info(f"Found course: {result}")

                if results:
                    message = "\n\n".join(results)
                    send_pushover_message(venue_name, message, date_14_days_ahead)
        except PlaywrightError as e:
            logging.error(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    # Execute check_new_courses on startup
    check_new_courses()

    schedule.every().day.at("02:00").do(check_new_courses)
    while True:
        logging.info(f"Checking time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        schedule.run_pending()
        time.sleep(30)