from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from utils import config


class BasePage:
    path = "/"

    def __init__(self, driver, base_url=config.BASE_URL):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(self.base_url + self.path)
        return self

    # --- primitives -----------------------------------------------------
    def find(self, locator):
        return self.wait.until(ec.visibility_of_element_located(locator))

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def click(self, locator):
        self.wait.until(ec.element_to_be_clickable(locator)).click()

    def type(self, locator, text):
        """Les champs React sont 'controles' : clear() ne met pas l'etat a jour,
        on selectionne tout et on supprime au clavier."""
        el = self.find(locator)
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.DELETE)
        el.send_keys(text)

    def set_value_js(self, locator, value):
        """Pour les champs difficiles a saisir au clavier (date, couleur) dans une SPA React."""
        el = self.find(locator)
        self.driver.execute_script(
            "const [el, v] = arguments;"
            "const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;"
            "setter.call(el, v);"
            "el.dispatchEvent(new Event('input', {bubbles: true}));",
            el, value,
        )

    def text_of(self, locator):
        return self.find(locator).text

    def texts(self, locator, child_css=None):
        """Lit le texte d'une liste d'elements en tolerant les re-rendus React
        (StaleElementReference) et les etats 'chargement' / 'liste vide'."""
        def read(driver):
            try:
                elements = driver.find_elements(*locator)
                values = [(e.find_element(By.CSS_SELECTOR, child_css) if child_css else e).text for e in elements]
                return values or False
            except (StaleElementReferenceException, NoSuchElementException):
                return False
        return self.wait.until(read)

    def wait_url_contains(self, fragment):
        self.wait.until(ec.url_contains(fragment))

    @staticmethod
    def field(label, tag="input"):
        """Les labels du formulaire ne sont pas relies aux champs (pas de 'for') -> XPath par voisinage."""
        return By.XPATH, f"//label[normalize-space()='{label}']/following-sibling::{tag}"
