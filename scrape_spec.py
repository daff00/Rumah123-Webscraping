import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import time
import re
from tqdm import tqdm
from datetime import timedelta

# Baca URL dari file CSV
input_file = "filtered_links.csv"
urls = pd.read_csv(input_file)["URL"]
# urls = urls[0:200]  # Untuk contoh, hanya mengambil 200 URL pertama

# Rotasi User-Agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

# Simulasi delay manusiawi
def human_like_delay():
    time.sleep(random.uniform(3, 15))  # Delay antara 3 hingga 15 detik

# Fungsi scraping untuk setiap URL
def scrape_url(url, session):
    headers = {"User-Agent": random.choice(user_agents)}

    try:
        response = session.get(url, headers=headers, timeout=30)

        # Pastikan request berhasil
        if response.status_code != 200:
            print(f"Gagal mengakses URL: {url}, status code: {response.status_code}")
            return None

        # Parse HTML menggunakan BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Mengambil harga rumah
        harga_elem = soup.select_one('div.flex.items-baseline.gap-x-1 span.text-primary.font-bold')
        harga = harga_elem.text.strip() if harga_elem else None

        # Mengambil lokasi
        lokasi_elem = soup.select_one('p.text-xs.text-gray-500.mb-2')
        lokasi = lokasi_elem.text.strip() if lokasi_elem else None

        # Mengambil spesifikasi
        spesifikasi = {}
        spesifikasi_elems = soup.find_all('div', class_=re.compile(r'flex.*gap-4.*'))
        if spesifikasi_elems:
            for elem in spesifikasi_elems:
                key_elem = elem.select_one('p.w-32.text-xs.font-light.text-gray-500')
                value_elem = elem.select_one('p:nth-of-type(2)')
                if key_elem and value_elem:
                    key = key_elem.text.strip()
                    value = value_elem.text.strip()
                    spesifikasi[key] = value

        # Menambahkan informasi tambahan jika tidak tersedia
        if "Lainnya" not in spesifikasi:
            spesifikasi["Lainnya"] = "Informasi tambahan tidak tersedia"

        # Membuat dictionary hasil scraping
        data = {
            "URL": url,
            "Harga": harga,
            "Lokasi": lokasi,
            **spesifikasi
        }
        return data

    except Exception as e:
        print(f"Error saat scraping URL {url}: {e}")
        return None

# Main scraping process
start_time = time.time()  # Mulai timer
all_data = []

with requests.Session() as session:
    for url in tqdm(urls, desc="Scraping progress"):
        # Scrape URL
        data = scrape_url(url, session)
        if data:
            all_data.append(data)

        # Delay manusiawi
        human_like_delay()

# Simpan hasil scraping ke file CSV
output_file = "hasil_scraping_rumah123.csv"
df = pd.DataFrame(all_data)
df.to_csv(output_file, index=False)
print(f"Data scraping telah disimpan ke {output_file}")

# Hitung durasi waktu scraping
end_time = time.time()
elapsed_time = end_time - start_time

# Format durasi
if elapsed_time < 3600:
    formatted_time = str(timedelta(seconds=int(elapsed_time)))  # Format MM:SS
else:
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))  # Format HH:MM:SS

print(f"Durasi scraping: {formatted_time}")