import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from tqdm import tqdm

# Membaca file CSV yang berisi URL
urls_df = pd.read_csv("filtered_links.csv")
urls = urls_df["URL"].tolist()

# List untuk menyimpan hasil scraping
data = []
failed_urls = []

# Fungsi untuk mengambil angka dari teks
def extract_number(text):
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None

# Fungsi untuk melakukan scraping
for url in tqdm(urls, desc="Scraping URLs"):
    try:
        response = requests.get(url, headers={
            "User -Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }, timeout=30)

        # Pastikan request berhasil
        if response.status_code != 200:
            print(f"Gagal mengakses URL: {url}, status code: {response.status_code}")
            failed_urls.append(url)
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
        spesifikasi_div = soup.select_one('div.flex.flex-col.space-y-4')  # Sesuaikan selektor utama jika ada elemen induk lain
        if spesifikasi_div:
            spesifikasi_elems = spesifikasi_div.select(
                'div.mb-4.flex.items-center.gap-4.text-sm.border-0.border-b.border-solid.border-gray-200.pb-2.last\\:border-b-0'
            )
            for elem in spesifikasi_elems:
                key_elem = elem.select_one('p.w-32.text-xs.font-light.text-gray-500')
                value_elem = elem.select_one('p:nth-of-type(2)')
                if key_elem and value_elem:
                    key = key_elem.text.strip()
                    value = value_elem.text.strip()
                    # Mengambil angka dari value jika tidak ada satuan
                    if key in ["Kamar Tidur", "Kamar Mandi", "Luas Tanah", "Luas Bangunan", "Carport", "Daya Listrik", "Kamar Tidur Pembantu", "Kamar Mandi Pembantu", "Garasi", "Jumlah Lantai"]:
                        spesifikasi[key] = extract_number(value)  # Ambil angka saja
                    else:
                        spesifikasi[key] = value  # Ambil string utuh untuk Sertifikat dan Kondisi Properti

        # Simpan data ke dalam list
        data.append({
            "URL": url,
            "Harga": harga,
            "Lokasi": lokasi,
            "Kamar Tidur": spesifikasi.get("Kamar Tidur"),
            "Kamar Mandi": spesifikasi.get("Kamar Mandi"),
            "Luas Tanah": spesifikasi.get("Luas Tanah"),
            "Luas Bangunan": spesifikasi.get("Luas Bangunan"),
            "Carport": spesifikasi.get("Carport"),
            "Sertifikat": spesifikasi.get("Sertifikat"),
            "Daya Listrik": spesifikasi.get("Daya Listrik"),
            "Kamar Tidur Pembantu": spesifikasi.get("Kamar Tidur Pembantu"),
            "Kamar Mandi Pembantu": spesifikasi.get("Kamar Mandi Pembantu"),
            "Garasi": spesifikasi.get("Garasi"),
            "Jumlah Lantai": spesifikasi.get("Jumlah Lantai"),
            "Kondisi Properti": spesifikasi.get("Kondisi Properti"),
        })
        
        # Delay untuk menghindari pemblokiran
        time.sleep(15)

    except Exception as e:
        print(f"Error saat scraping URL {url}: {e}")
        failed_urls.append(url)

# Simpan hasil ke CSV
df = pd.DataFrame(data)
df.to_csv("data_harga_kabupaten_tangerang.csv", index=False)

# Simpan URL yang gagal
with open("failed_urls.txt", "w") as f:
    for failed_url in failed_urls:
        f.write(f"{failed_url}\n")

print("Scraping selesai. Data disimpan dalam 'data_harga_kabupaten_tangerang.csv'.")