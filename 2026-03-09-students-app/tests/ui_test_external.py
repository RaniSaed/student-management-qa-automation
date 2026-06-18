"""
Step 3 Bonus — Selenium UI Tests on an external website.
Target: https://www.selenium.dev/selenium/web/web-form.html
This is Selenium's own official test form — stable and always available.

Requires internet access.
Run:
    uv run pytest tests/ui_test_external.py -v
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

FORM_URL = "https://www.selenium.dev/selenium/web/web-form.html"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(5)
    yield d
    d.quit()


@pytest.fixture(scope="module", autouse=True)
def open_form(driver):
    """Navigate to the test form once for the whole module."""
    driver.get(FORM_URL)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "form"))
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("EXT-001")
def test_page_title_contains_web_form(driver):
    # Act / Assert
    assert "Web form" in driver.title


@pytest.mark.jira_key("EXT-002")
def test_text_input_accepts_typed_value(driver):
    # Arrange
    text_input = driver.find_element(By.NAME, "my-text")
    text_input.clear()

    # Act
    text_input.send_keys("Hello Selenium")

    # Assert
    assert text_input.get_attribute("value") == "Hello Selenium"


@pytest.mark.jira_key("EXT-003")
def test_dropdown_select_option_two(driver):
    # Arrange
    select = Select(driver.find_element(By.NAME, "my-select"))

    # Act
    select.select_by_visible_text("Two")

    # Assert
    assert select.first_selected_option.text == "Two"


@pytest.mark.jira_key("EXT-004")
def test_checkbox_can_be_checked(driver):
    # Arrange
    checkbox = driver.find_element(By.ID, "my-check-1")
    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
    if checkbox.is_selected():
        driver.execute_script("arguments[0].click();", checkbox)  # uncheck first

    # Act — use JS click to avoid element-intercept issues
    driver.execute_script("arguments[0].click();", checkbox)

    # Assert
    assert checkbox.is_selected()


@pytest.mark.jira_key("EXT-005")
def test_submit_button_is_visible_and_labelled(driver):
    # Act
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

    # Assert
    assert submit_btn.is_displayed()
    assert submit_btn.text == "Submit"
