from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Inisialisasi WebDriver menggunakan WebDriver Manager
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# URL awal
base_url = "https://www.rumah123.com/jual/cari/?location=tangerang"
driver.get(base_url)

# Tunggu halaman termuat
wait = WebDriverWait(driver, 10)

# Daftar untuk menyimpan semua link
filtered_links = []

# Variabel untuk membatasi scraping
page_counter = 1  # Mulai dari halaman 1
max_pages = 5     # Tentukan batas maksimum halaman

try:
    while page_counter <= max_pages:
        print(f"Scraping halaman {page_counter}...")

        # Tunggu elemen properti muncul
        properties = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[title]')))

        # Ambil link dari tiap properti di halaman
        for property_elem in properties:
            link = property_elem.get_attribute('href')
            if 'hos' in link and link not in filtered_links:  # Hanya ambil link yang mengandung 'hos'
                filtered_links.append(link)

        # Cek apakah sudah mencapai batas halaman
        if page_counter == max_pages:
            print(f"Telah mencapai batas halaman {max_pages}. Scraping selesai.")
            break

        # Cari tombol "Next page" untuk pindah halaman
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next page"]')
            ActionChains(driver).move_to_element(next_button).click(next_button).perform()
            time.sleep(2)  # Beri jeda untuk halaman berikutnya termuat
            page_counter += 1  # Tambah penghitung halaman
        except Exception:
            print("Tidak ada tombol Next, scraping selesai.")
            break

finally:
    # Tutup browser
    driver.quit()

# Simpan hasil ke CSV
df = pd.DataFrame(filtered_links, columns=["URL"])
df.to_csv("filtered_links.csv", index=False)

print(f"Scraping selesai. {len(filtered_links)} link disimpan dalam 'filtered_links.csv'.")