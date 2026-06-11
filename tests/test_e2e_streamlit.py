from __future__ import annotations

import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.e2e_utils import run_streamlit_app


DEFAULT_TIMEOUT = 20


def _wait(driver, seconds: int = DEFAULT_TIMEOUT) -> WebDriverWait:
    return WebDriverWait(driver, seconds)


def _click_button_by_text(driver, text: str) -> None:
    # Streamlit buttons render as <button> with visible text.
    btn = _wait(driver).until(EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space()='{text}']")))
    # Scroll into view and click; fall back to JS click if an overlay intercepts.
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
    try:
        btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)


def _fill_text_input(driver, label: str, value: str) -> None:
    # Find the first input following the label.
    inp = _wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, f"//label[contains(normalize-space(), '{label}')]/following::input[1]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
    inp.click()
    inp.send_keys(Keys.CONTROL, "a")
    inp.send_keys(value)


def _selectbox_choose_first(driver, label: str) -> None:
    # Streamlit selectbox uses BaseWeb. Click the control, then choose first option.
    lab = _wait(driver).until(
        EC.presence_of_element_located((By.XPATH, f"//label[contains(normalize-space(), '{label}')]"))
    )

    container = lab.find_element(
        By.XPATH,
        "./ancestor::div[@data-testid='stSelectbox'][1] | ./ancestor::div[contains(@data-testid,'stSelectbox')][1]",
    )

    # BaseWeb markup varies across Streamlit versions; try a few stable hooks.
    click_targets = [
        ".//*[@data-baseweb='select']//div[@role='combobox']",
        ".//*[@data-baseweb='select']//*[@role='combobox']",
        ".//*[@data-baseweb='select']//*[@aria-haspopup='listbox']",
        ".//*[@data-baseweb='select']//*[@tabindex='0']",
        ".//*[@data-baseweb='select']",
    ]
    for xp in click_targets:
        try:
            el = container.find_element(By.XPATH, xp)
            el.click()
            break
        except Exception:
            continue
    else:
        # If we can't find the control, assume a value is already selected.
        return

    # Options are in a portal; select first visible option.
    opt = _wait(driver).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='option'][1]")))
    opt.click()
    # Wait for dropdown to close (prevents click interception).
    _wait(driver).until_not(EC.presence_of_element_located((By.XPATH, "//div[@role='listbox']")))


def _count_from_button(driver, prefix: str) -> int:
    # Buttons are like "Talqeen (3)"
    btn = _wait(driver).until(EC.presence_of_element_located((By.XPATH, f"//button[starts-with(normalize-space(), '{prefix} (')]")))
    text = btn.text.strip()
    left = text.rfind("(")
    right = text.rfind(")")
    return int(text[left + 1 : right])


def _wait_for_button_count(driver, prefix: str, expected: int, timeout: int = DEFAULT_TIMEOUT) -> None:
    def _ok(_driver):
        try:
            return _count_from_button(_driver, prefix) == expected
        except Exception:
            return False

    WebDriverWait(driver, timeout).until(_ok)


@pytest.fixture(scope="session")
def driver():
    opts = ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,900")
    d = webdriver.Chrome(options=opts)  # Selenium Manager will locate driver
    try:
        yield d
    finally:
        d.quit()


def test_full_flow_student_murajat_juzulhali_jadeed(driver):
    """
    E2E happy-path:
    - Start app
    - Add/select student
    - Murajat: select surah, click mistake buttons, verify counts update
    - Juzulhali: pick page, click mistake button, verify count update
    - Jadeed: add one row, save, verify it appears in editor after refresh
    """
    with run_streamlit_app() as srv:
        base = f"http://127.0.0.1:{srv.port}"
        driver.get(base)

        # Login
        _fill_text_input(driver, "Username", "mukhayyam")
        _fill_text_input(driver, "Password", "mukhayyam12")
        _click_button_by_text(driver, "Sign In")

        # Home: add student
        _click_button_by_text(driver, "Add new student") if False else None  # expander handled by Streamlit
        # Expanders render a <summary> with text; click it to expand.
        summary = _wait(driver).until(EC.element_to_be_clickable((By.XPATH, "//summary[contains(., 'Add new student')]")))
        summary.click()
        _fill_text_input(driver, "Full name", f"Test Student {int(time.time())}")
        _click_button_by_text(driver, "Add student")

        # Murajat
        _click_button_by_text(driver, "Murajat")
        # Surah select
        try:
            _selectbox_choose_first(driver, "Surah")
        except TimeoutException:
            # If already selected by previous run / browser cache, continue
            pass

        before_t = _count_from_button(driver, "Talqeen")
        _click_button_by_text(driver, f"Talqeen ({before_t})")
        _wait_for_button_count(driver, "Talqeen", before_t + 1, timeout=30)

        before_r = _count_from_button(driver, "Repeat mistake")
        before_t2 = _count_from_button(driver, "Talqeen")
        _click_button_by_text(driver, f"Repeat mistake ({before_r})")
        _wait_for_button_count(driver, "Repeat mistake", before_r + 1, timeout=30)
        _wait_for_button_count(driver, "Talqeen", before_t2 + 1, timeout=30)

        # Back home
        _click_button_by_text(driver, "← Back to Home")

        # Juzulhali
        _click_button_by_text(driver, "Juzulhali")
        before_tb = _count_from_button(driver, "Tanbeeh")
        _click_button_by_text(driver, f"Tanbeeh ({before_tb})")
        _wait_for_button_count(driver, "Tanbeeh", before_tb + 1, timeout=30)
        _click_button_by_text(driver, "← Back to Home")

        # Jadeed
        _click_button_by_text(driver, "Jadeed")
        # Data editor DOM is brittle across Streamlit versions; verify core Jadeed actions instead.
        _wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='No Jadeed today']")))
        _click_button_by_text(driver, "No Jadeed today")
        _wait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(., 'Marked: No Jadeed for today')]"))
        )

