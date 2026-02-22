# ProjectAkhir_pythonLVL3
Chatbot Manhwa!! Kamu bisa meminta rekomendasi manhwa lewat bot ini!!

**Description**

Bot Discord dengan Database manhwa adalah bot yang bisa kalian gunakan untuk mencari judul manhwa, mencari rekomendasi manhwa berdasarkan genre, mengetahui skor manhwa tertinggi saat ini, dan meminta rekomendasi acak dari bot ini.


## Fitur Bot
- Mencari manhwa berdasarkan judul nya
- mencari manhwa dengan berdasarkan (Pagination)
- Top manhwa berdasarkan score
- Rekomendasi Manhwa acak
- Impor data CSV ke dalam basis data SQLite(khusus admin)


## Teknologi yang dipakai dalam project ini
- Python 3.12
- discord.py
- SQLite3


## Instalasi

1. Clone repository:
   git clone https://github.com/taroo2425/ProjectAkhir_pythonLVL3.git

2. Install dependencies:
   pip install -r requirements.txt

3. convert manhwa.csv menjadi SQLite database di python 'manhwa.db'

4. Atur Token bot kamu di config.py

5. Jalankan bot nya:
   python bot.py

   
## Commands

!start  
!manhwa <title>  
!genre <genre> 
!top [number]  
!random_manhwa  

## Author
Created by Kiasatina Tunggawijaya(kias)

noted! (project ini untuk kelulusan di kursus programming)


