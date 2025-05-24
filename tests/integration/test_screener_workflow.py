import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@pytest.fixture(scope="function")
def driver():
    """Selenium WebDriver Fixture"""
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def test_screener_control_workflow(driver):
    """Teste den kompletten Workflow des Screener-Controls"""
    # Frontend öffnen
    driver.get("http://localhost:3000")
    
    # Screener starten (angenommen über einen Button)
    start_button = driver.find_element(By.xpath("//button[contains(text(), 'Screener ausführen')]"))
    start_button.click()
    
    # Warten bis der Fortschrittsbalken erscheint
    progress_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.className, "MuiLinearProgress-root"))
    )
    assert progress_bar.is_displayed()
    
    # Stopp-Button testen
    stop_button = driver.find_element(By.xpath("//button[contains(text(), 'Stoppen')]"))
    assert stop_button.is_displayed()
    stop_button.click()
    
    # Warten bis der Status auf "stopping" oder "completed" wechselt
    status_text = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.xpath("//p[contains(text(), 'Status:')]"))
    )
    assert "stopping" in status_text.text.lower() or "completed" in status_text.text.lower()