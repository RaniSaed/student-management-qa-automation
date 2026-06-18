"""
Step 3 — Selenium UI Tests for the Students App
Tests run against a live Flask server (auto-started by the live_server fixture).
MySQL must be running. Chrome must be installed (Selenium Manager downloads ChromeDriver).

Run:
    uv run pytest tests/ui_test_students.py -v
"""
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(5)
    yield d
    d.quit()


@pytest.fixture
def app_page(driver, live_server):
    """Opens the app and waits until the page is fully interactive."""
    driver.get(live_server)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "btAdd"))
    )
    return driver


def accept_alert(driver, timeout=5):
    alert = WebDriverWait(driver, timeout).until(EC.alert_is_present())
    text = alert.text
    alert.accept()
    return text


# ---------------------------------------------------------------------------
# Page structure
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-301")
def test_page_title(app_page):
    # Arrange / Act / Assert
    assert app_page.title == "Students App"


@pytest.mark.jira_key("STUDENT-302")
def test_h1_heading(app_page):
    h1 = app_page.find_element(By.TAG_NAME, "h1")
    assert h1.text == "Students Application"


@pytest.mark.jira_key("STUDENT-303")
def test_table_has_correct_headers(app_page):
    headers = [th.text for th in app_page.find_elements(By.TAG_NAME, "th")]
    assert "ID" in headers
    assert "Name" in headers
    assert "Age" in headers
    assert "X" in headers


@pytest.mark.jira_key("STUDENT-304")
def test_buttons_are_visible(app_page):
    assert app_page.find_element(By.ID, "btAdd").is_displayed()
    assert app_page.find_element(By.ID, "btUpdate").is_displayed()
    assert app_page.find_element(By.ID, "btDelete").is_displayed()


# ---------------------------------------------------------------------------
# Add student — validation / alerts
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-305")
def test_add_with_empty_fields_shows_alert(app_page):
    # Arrange — ensure inputs are empty
    app_page.find_element(By.ID, "nameBox").clear()
    app_page.find_element(By.ID, "ageBox").clear()

    # Act
    app_page.find_element(By.ID, "btAdd").click()

    # Assert
    alert_text = accept_alert(app_page)
    assert "Enter name and age" in alert_text


@pytest.mark.jira_key("STUDENT-306")
def test_add_invalid_age_below_18_shows_error_alert(app_page):
    # Arrange
    app_page.find_element(By.ID, "nameBox").clear()
    app_page.find_element(By.ID, "nameBox").send_keys("Underage Student")
    app_page.find_element(By.ID, "ageBox").clear()
    app_page.find_element(By.ID, "ageBox").send_keys("5")

    # Act
    app_page.find_element(By.ID, "btAdd").click()

    # Assert
    alert_text = accept_alert(app_page)
    assert "Add student failed" in alert_text


# ---------------------------------------------------------------------------
# Add student — happy path
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-307")
def test_add_valid_student_appears_in_table(app_page, live_server):
    unique_name = "UITestStudent_Add"

    # Arrange
    app_page.find_element(By.ID, "nameBox").clear()
    app_page.find_element(By.ID, "nameBox").send_keys(unique_name)
    app_page.find_element(By.ID, "ageBox").clear()
    app_page.find_element(By.ID, "ageBox").send_keys("25")

    # Act
    app_page.find_element(By.ID, "btAdd").click()

    # Assert — wait for the student to appear in the table
    WebDriverWait(app_page, 10).until(
        EC.text_to_be_present_in_element((By.ID, "tbody"), unique_name)
    )
    assert unique_name in app_page.find_element(By.ID, "tbody").text

    # Cleanup — find the row and delete via API
    for row in app_page.find_elements(By.CSS_SELECTOR, "#tbody tr"):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) > 1 and cells[1].text == unique_name:
            requests.delete(f"{live_server}/students/{cells[0].text}")
            break


# ---------------------------------------------------------------------------
# Delete student — validation / alert
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-308")
def test_delete_with_no_id_shows_alert(app_page):
    # Arrange — clear the ID box
    app_page.find_element(By.ID, "idBox").clear()

    # Act
    app_page.find_element(By.ID, "btDelete").click()

    # Assert
    alert_text = accept_alert(app_page)
    assert "Enter ID" in alert_text


# ---------------------------------------------------------------------------
# Delete student — happy path via X button in table row
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-309")
def test_delete_student_via_x_button_removes_row(app_page, live_server):
    # Arrange — create a student via API so we have a known row to delete
    response = requests.post(
        f"{live_server}/students",
        json={"name": "UITestStudent_Del", "age": 28},
    )
    student_id = response.json()["id"]

    # Reload the page so the new student appears in the table
    app_page.get(live_server)
    WebDriverWait(app_page, 10).until(
        EC.text_to_be_present_in_element((By.ID, "tbody"), "UITestStudent_Del")
    )

    # Act — click the X button for this specific student
    x_btn = app_page.find_element(
        By.CSS_SELECTOR, f"button.delete-btn[data-id='{student_id}']"
    )
    x_btn.click()

    # Assert — the row disappears from the table
    WebDriverWait(app_page, 10).until(
        lambda d: "UITestStudent_Del" not in d.find_element(By.ID, "tbody").text
    )
    assert "UITestStudent_Del" not in app_page.find_element(By.ID, "tbody").text
