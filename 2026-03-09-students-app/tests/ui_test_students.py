"""UI tests for the Students App using Selenium + pytest.

Requirements:
- Flask server running at http://127.0.0.1:5000
- Chrome browser installed
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="module")
def driver():
    """Create a Chrome WebDriver for the test session."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # run without visible browser
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture(autouse=True)
def cleanup_students():
    """Delete all students before each test."""
    resp = requests.get(f"{BASE_URL}/students")
    if resp.status_code == 200:
        for student in resp.json():
            requests.delete(f"{BASE_URL}/students/{student['id']}")
    yield


@pytest.fixture
def page(driver):
    """Navigate to the students app page."""
    driver.get(BASE_URL)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    return driver


@pytest.mark.jira_key("SAQC-1")
def test_page_title(page):
    """The page title should be 'Students App'."""
    assert page.title == "Students App"


@pytest.mark.jira_key("SAQC-1")
def test_page_heading(page):
    """The page should have an h1 with 'Students Application'."""
    h1 = page.find_element(By.TAG_NAME, "h1")
    assert h1.text == "Students Application"


@pytest.mark.jira_key("SAQC-1")
def test_table_exists(page):
    """The page should have a students table."""
    table = page.find_element(By.TAG_NAME, "table")
    assert table.is_displayed()


@pytest.mark.jira_key("SAQC-1")
def test_table_headers(page):
    """The table should have the correct header columns."""
    headers = page.find_elements(By.CSS_SELECTOR, "thead th")
    header_texts = [h.text for h in headers]
    assert "ID" in header_texts
    assert "Name" in header_texts
    assert "Age" in header_texts
    assert "X" in header_texts


@pytest.mark.jira_key("SAQC-1")
def test_buttons_exist(page):
    """The page should have Add, Update, and Delete buttons."""
    add_btn = page.find_element(By.ID, "btAdd")
    update_btn = page.find_element(By.ID, "btUpdate")
    delete_btn = page.find_element(By.ID, "btDelete")
    assert add_btn.is_displayed()
    assert update_btn.is_displayed()
    assert delete_btn.is_displayed()
    assert add_btn.get_attribute("value") is None  # button not input
    assert "Add" in add_btn.text


@pytest.mark.jira_key("SAQC-1")
def test_add_student_appears_in_table(page):
    """Adding a student should make them appear in the table."""
    # fill the form
    name_input = page.find_element(By.ID, "nameBox")
    age_input = page.find_element(By.ID, "ageBox")
    name_input.send_keys("UI Test Student")
    age_input.send_keys("28")

    # click Add
    add_btn = page.find_element(By.ID, "btAdd")
    add_btn.click()

    # wait for table to update
    WebDriverWait(page, 5).until(
        EC.text_to_be_present_in_element((By.ID, "tbody"), "UI Test Student")
    )

    # verify in table
    rows = page.find_elements(By.CSS_SELECTOR, "#tbody tr")
    assert len(rows) == 1
    cells = rows[0].find_elements(By.TAG_NAME, "td")
    assert cells[1].text == "UI Test Student"
    assert cells[2].text == "28"


@pytest.mark.jira_key("SAQC-1")
def test_add_student_invalid_shows_error(page):
    """Adding a student with invalid age should show an error alert."""
    name_input = page.find_element(By.ID, "nameBox")
    age_input = page.find_element(By.ID, "ageBox")
    name_input.send_keys("Bad Age")
    age_input.send_keys("17")

    add_btn = page.find_element(By.ID, "btAdd")
    add_btn.click()

    # wait for alert dialog
    WebDriverWait(page, 5).until(EC.alert_is_present())
    alert = page.switch_to.alert
    alert_text = alert.text
    assert "age" in alert_text.lower() or "illegal" in alert_text.lower()
    alert.accept()


@pytest.mark.jira_key("SAQC-1")
def test_delete_student(page):
    """Deleting a student should remove them from the table."""
    # add a student via API
    resp = requests.post(f"{BASE_URL}/students", json={"name": "To Delete", "age": 22})
    student_id = resp.json()["id"]

    # refresh the page
    page.get(BASE_URL)
    WebDriverWait(page, 5).until(
        EC.text_to_be_present_in_element((By.ID, "tbody"), "To Delete")
    )

    # click the X delete button for this student
    delete_btn = page.find_element(By.CSS_SELECTOR, f"button.delete-btn[data-id='{student_id}']")
    delete_btn.click()

    # wait for table to update
    WebDriverWait(page, 5).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, f"button.delete-btn[data-id='{student_id}']"))
    )

    # verify student is gone
    rows = page.find_elements(By.CSS_SELECTOR, "#tbody tr")
    assert len(rows) == 0


@pytest.mark.jira_key("SAQC-1")
def test_update_student(page):
    """Updating a student should refresh the table."""
    # add a student via API
    resp = requests.post(f"{BASE_URL}/students", json={"name": "Before Update", "age": 20})
    student = resp.json()

    # refresh page
    page.get(BASE_URL)
    WebDriverWait(page, 5).until(
        EC.text_to_be_present_in_element((By.ID, "tbody"), "Before Update")
    )

    # fill the form with the student ID and new data
    id_input = page.find_element(By.ID, "idBox")
    name_input = page.find_element(By.ID, "nameBox")
    age_input = page.find_element(By.ID, "ageBox")

    id_input.send_keys(str(student["id"]))
    name_input.clear()
    name_input.send_keys("After Update")
    age_input.clear()
    age_input.send_keys("35")

    # click Update
    update_btn = page.find_element(By.ID, "btUpdate")
    update_btn.click()

    # wait for the table to reflect the update
    WebDriverWait(page, 5).until(
        EC.text_to_be_present_in_element((By.ID, "tbody"), "After Update")
    )

    rows = page.find_elements(By.CSS_SELECTOR, "#tbody tr")
    cells = rows[0].find_elements(By.TAG_NAME, "td")
    assert cells[1].text == "After Update"
    assert cells[2].text == "35"
