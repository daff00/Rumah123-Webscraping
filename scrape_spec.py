import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import time
import re
from tqdm import tqdm
from datetime import timedelta
import os
import winsound

# Baca URL dari file CSV
input_file = "filtered_links.csv"
urls = pd.read_csv(input_file)["URL"].tolist()
start_index = 1401  # Indeks awal untuk scraping, error di url 505
urls = urls[start_index:1500]  # Scrape sampai URL ke-n

# Nama file output CSV
output_file = "hasil_scraping_rumah123.csv"

# Jika file hasil scraping sudah ada, baca URL yang sudah di-scrape
if os.path.exists(output_file):
    existing_data = pd.read_csv(output_file)
    scraped_urls = existing_data["URL"].tolist()
else:
    scraped_urls = []

# Filter URL yang belum di-scrape
urls_to_scrape = [url for url in urls if url not in scraped_urls]

# Rotasi User-Agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edge/96.0.1054.62",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 4.2.2; en-gb; Nexus 4 Build/JDQ39) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
]

# Simulasi delay manusiawi
def human_like_delay():
    time.sleep(random.uniform(10, 45))  # Delay antara 3 hingga 15 detik

# Fungsi scraping untuk setiap URL
def scrape_url(url, session, max_retries=3):
    for attempt in range(max_retries):
        headers = {
            "User-Agent": random.choice(user_agents),
            "Referer": "https://www.google.com/",
            "Accept-Language": "en-US,en;q=0.9"
        }

        try:
            response = session.get(url, headers=headers, timeout=30)

            # Pastikan request berhasil
            if response.status_code == 429:
                print(f"Error 429: Terlalu banyak permintaan. Menunggu 10 menit sebelum mencoba lagi...")
                time.sleep(600)  # Jeda 10 menit untuk error 429
                continue
            elif response.status_code != 200:
                print(f"Gagal mengakses URL: {url}, status code: {response.status_code}")
                time.sleep(2 ** attempt)  # Exponential backoff
                continue

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
            print(f"Error saat scraping URL {url} pada percobaan ke-{attempt + 1}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

    print(f"Gagal mengambil data setelah {max_retries} percobaan: {url}")
    return None

# Main scraping process
start_time = time.time()  # Mulai timer
all_data = []

try:
    with requests.Session() as session:
        for i, url in enumerate(tqdm(urls_to_scrape, desc="Scraping progress")):
            # Scrape URL
            data = scrape_url(url, session)
            if data:
                all_data.append(data)
            else:
                print(f"Error mengambil data di URL ke-{start_index + i}")
                print("Proses scraping dihentikan.")
                break

            # Delay manusiawi
            human_like_delay()

        # Jeda tambahan setiap 50 URL untuk menghindari deteksi bot
        if i > 0 and i % 50 == 0:
            print("Jeda tambahan 5 menit untuk menghindari deteksi bot...")
            time.sleep(300)  # Jeda 5 menit

    # Simpan hasil scraping ke CSV jika ada data yang berhasil diambil
    if all_data:
        # Jika file sudah ada, gabungkan data baru dengan data lama
        if os.path.exists(output_file):
            new_data = pd.DataFrame(all_data)
            combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=["URL"])
        else:
            combined_data = pd.DataFrame(all_data)

        # Simpan ke file
        combined_data.to_csv(output_file, index=False)
        print(f"Scraping selesai. {len(all_data)} data baru ditambahkan. Total {len(combined_data)} data disimpan dalam '{output_file}'.")
    else:
        print("Tidak ada data baru yang ditemukan.")
except Exception as e:
    print(f"Proses scraping dihentikan karena error: {e}")
    winsound.Beep(440, 1000)  # Bunyi notifikasi saat error

# Hitung durasi waktu scraping
end_time = time.time()
elapsed_time = end_time - start_time

# Format durasi
if elapsed_time < 3600:
    formatted_time = str(timedelta(seconds=int(elapsed_time)))  # Format MM:SS
else:
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))  # Format HH:MM:SS

print(f"Durasi scraping: {formatted_time}")
winsound.Beep(660, 1000)  # Bunyi notifikasi saat selesai