import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from .base_page import BasePage


class DashboardPage(BasePage):
    path = "/admin"

    TITLE = (By.CSS_SELECTOR, "h1.page-title")
    METRICS = (By.CSS_SELECTOR, ".metric")
    EVENT_ROWS = (By.CSS_SELECTOR, "table.table tbody tr")
    PROMOS_LINK = (By.PARTIAL_LINK_TEXT, "Codes promo")
    NEW_EVENT_LINK = (By.PARTIAL_LINK_TEXT, "Nouvel evenement")

    def title(self):
        return self.text_of(self.TITLE)

    def metric(self, label):

        wait = WebDriverWait(self.driver, timeout=10)
        wait.until(ec.visibility_of_element_located(self.METRICS))
        
        # time.sleep(1)  # attendre que les stats soient chargees
        for m in self.find_all(self.METRICS):
            if m.find_element(By.CSS_SELECTOR, ".m-label").text == label:
                return m.find_element(By.CSS_SELECTOR, ".m-value").text
        raise ValueError(f"Metrique introuvable : {label}")

    def event_titles(self):
        return self.texts(self.EVENT_ROWS, "td div")

    def open_promos(self):
        self.click(self.PROMOS_LINK)
        self.wait_url_contains("/admin/promos")

    def open_new_event_form(self):
        self.click(self.NEW_EVENT_LINK)
        self.wait_url_contains("/admin/events/new")
