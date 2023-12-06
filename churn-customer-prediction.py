# -*- coding: utf-8 -*-
"""Final Project Data 1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ciju89kTmGVzQImg6v8x1I6Jwnh8nUxQ

# **Business Understanding**

**Project Description**

Final Project ini memiliki tujuan yaitu untuk memprediksi apakah customer akan menggunakan layanan lagi atau tidak pada suatu perusahaan e-commerce. Proyek ini akan menghasilkan model yang penting untuk dapat mengidentifikasi customer yang berhenti menggunakan layanan sehingga dapat mengurangi resiko bisnis dan membantu dalam pembuat keputusan menyusun strategi penjualan.

**Manfaat**

- Meningkatkan keputusan strategi penjualan dengan bantuan model prediksi, menghindari kerugian dari hilangnya loyalitas customer.
- Efisiensi operasional dengan memanfaatkan model prediksi, sehingga berfokus pada customer yang tepat.


**Tantangan**

- Ukuran data yang besar (4.33 Gb data uncompressed)
- Merge dataset
- Dealing dengan missing data
- Imbalanced datasets

**Dataset**

Terdapat 3 dataset yang digunakan untuk mengerjakan proyek.
- **customer.csv**

  File ini berisi data dari pelanggan seperti nama, email, data demografi, hingga device yang dimiliki.

- **product.csv**

  Dataset product berisi informasi tentang produk yang dijual, seperti nama, kategori, harga, dan warna.

- **transactions.csv**

  File ini memuat data transaksi yang dilakukan pelanggan seperti produk yang dibeli, total harga, tujuan alamat, hingga metode pembayaran. Dataset ini memberikan informasi tentang riwayat transaksi dari pelanggan.

- **click_stream**

  File ini berisi data kumpulan data yang berisi informasi tentang halaman web yang dikunjungi oleh pelanggan seperti, waktu, traffic yang digunakan dan aktivitas yang dilakukan

# **Exploratory Data Analysis (EDA)**

## Import Package
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import json

"""##Data Collection (Load Data)"""

from google.colab import drive
drive.mount('/content/drive')

customer = pd.read_csv('/content/drive/MyDrive/dataset/customer.csv')
product = pd.read_csv('/content/drive/MyDrive/dataset/product.csv',error_bad_lines=False)
transactions = pd.read_csv('/content/drive/MyDrive/dataset/transactions.csv')
stream = pd.read_csv('/content/drive/MyDrive/dataset/click_stream.csv')

"""##Data Preparation"""

customer.info()

product.info()

transactions.info()

stream.info()

"""###Merge Datasets"""

# Melakukan merge antara transactions - customer - click_stream dengan left join
df = (transactions.merge(customer, how='left', on='customer_id')).merge(stream, how='left', on='session_id')

# Mengganti kutip tunggal dengan kutip ganda
df['product_metadata'] = df['product_metadata'].str.replace("'", '"')

# Apply json pada kolom product_metadata
df['product_metadata'] = df['product_metadata'].apply(json.loads)

# Extrack product metadata
df['product_id'] = df['product_metadata'].apply(lambda x: [item['product_id'] for item in x])
df['quantity'] = df['product_metadata'].apply(lambda x: [item['quantity'] for item in x])
df['item_price'] = df['product_metadata'].apply(lambda x: [item['item_price'] for item in x])

#drop product_metadata
df.drop(columns='product_metadata', inplace=True)

# Extrack event metadata untuk search keyword
df['search_keywords'] = df['event_metadata'].apply(lambda x: json.loads(x.replace("'", "\"")).get('search_keywords') if isinstance(x, str) and 'search_keywords' in json.loads(x.replace("'", "\"")) else np.nan)

#drop product_metadata
df.drop(columns='event_metadata', inplace=True)

#Explode kolom yang berisi list menjadi baris baru
df = df.explode(['product_id', 'quantity', 'item_price'], ignore_index=True)

# Melakukan merge antara df dan product dengan left join
data = df.merge(product, left_on='product_id', right_on='id', how='left')

# Menampilkan Dataframe
data

data.info()

"""###Feature Engginering

####Convert Datetime
"""

# Mengubah kolom event_time dan shipment_date_limit menjadi tipe data datetime
data['event_time'] = pd.to_datetime(data['event_time'])
data['shipment_date_limit'] = pd.to_datetime(data['shipment_date_limit'])

# Mengubah format menjadi tahun - bulan - tanggal
data['event_time'] = data['event_time'].dt.strftime('%Y-%m-%d')
data['shipment_date_limit'] = data['shipment_date_limit'].dt.strftime('%Y-%m-%d')

# Mengubah kolom event_time dan shipment_date_limit menjadi tipe data datetime
data['event_time'] = pd.to_datetime(data['event_time'])
data['shipment_date_limit'] = pd.to_datetime(data['shipment_date_limit'])

"""####Fitur Churn"""

# Mengindeks DataFrame berdasarkan kolom 'Tanggal' dan menyaring baris sebelum tanggal tertentu
cut_date = pd.to_datetime('2021-08-01')
data = data[data['event_time'] >= cut_date]

# Descriptive statistic dari kolom event_time
data['event_time'].describe()

# Menghitung waktu 3 bulan sejak batas waktu tertentu
cutoff_date = pd.to_datetime('2022-08-01')
month_ago = cutoff_date - pd.DateOffset(months=3)

# Membuat kolom 'churn' berdasarkan kondisi
data['churn'] = (data['event_time'] <= month_ago).astype(int)

# Menampilkan jumlah value dari kolom 'churn'
data[['churn']].value_counts()

"""#### Fitur age"""

# Mengonversi kolom 'birthdate' menjadi objek datetime
data['birthdate'] = pd.to_datetime(data['birthdate'])

# Menghitung umur dan membuat kolom baru 'age'
current_date = datetime.now()
data['age'] = current_date.year - data['birthdate'].dt.year

data.drop(columns='birthdate', inplace=True)

"""#### Fitur age_join"""

# Mengonversi kolom 'first_join_date' menjadi objek datetime
data['first_join_date'] = pd.to_datetime(data['first_join_date'])

# Menghitung waktu pertama join dan membuat kolom baru 'age_join'
current_date = datetime.now()
data['age_join'] = current_date.year - data['first_join_date'].dt.year

data.drop(columns='first_join_date', inplace=True)

"""#### Search Keyword"""

# Menampilkan jumlah value dari kolom 'search_keyword'
data['search_keywords'].value_counts()

# Mengganti value NaN dengan value 'tidak melakukan search' dalam kolom search_keyword
data['search_keywords'].fillna("tidak melakukan search", inplace=True)

# Mengganti nilai selain 'tidak melakukan search' dengan 'melakukan search' dalam kolom 'search_keywords'
data['search_keywords'] = data['search_keywords'].apply(lambda x: 'melakukan search' if x != 'tidak melakukan search' else x)

# Menampilkan jumlah value dari kolom 'search_keyword'
data['search_keywords'].value_counts()

"""#### Promo Code"""

# Menampilkan jumlah value dari kolom 'promo_code'
data['promo_code'].value_counts()

# Mengganti value NaN dengan value 'tidak melakukan search' dalam kolom search_keyword
data['promo_code'].fillna("tidak menggunakan promo code", inplace=True)

# Mengganti nilai selain 'tidak menggunakan promo code' dengan 'menggunakan promo' dalam kolom 'promo_code'
data['promo_code'] = data['promo_code'].apply(lambda x: 'menggunakan promo' if x != 'tidak menggunakan promo code' else x)

# Menampilkan jumlah value dari kolom 'promo_code'
data['promo_code'].value_counts()

"""#### Payment Methode"""

# Menampilkan jumlah value dari kolom 'payment_method'
data['payment_method'].value_counts()

# Mengganti beberapa value menjadi 'Dompet Digital'
data['payment_method'] = data['payment_method'].replace({'Gopay': 'Dompet digital', 'OVO': 'Dompet digital', 'LinkAja': 'Dompet digital'})

# Menampilkan jumlah value dari kolom 'payment_method'
data['payment_method'].value_counts()

"""#### Provinsi"""

# Mengelompokan lokasi tempat tinggal customer menjadi 3 provinsi
data['provinsi'] = data['home_location'].replace({
    'Jakarta Raya': 'Barat', 'Jawa Barat': 'Barat', 'Jawa Tengah': 'Barat', 'Yogyakarta': 'Barat', 'Jawa Timur': 'Barat',
    'Lampung': 'Barat', 'Sumatera Barat': 'Barat', 'Sumatera Utara': 'Barat', 'Riau': 'Barat', 'Bengkulu': 'Barat', 'Banten': 'Tengah', 'Jambi': 'Tengah',
    'Bangka Belitung': 'Barat', 'Aceh': 'Barat', 'Kepulauan Riau': 'Timur', 'Sumatera Selatan': 'Barat',

    'Kalimantan Barat': 'Tengah', 'Kalimantan Tengah': 'Tengah', 'Kalimantan Selatan': 'Tengah', 'Kalimantan Timur': 'Tengah',
    'Sulawesi Utara': 'Tengah', 'Sulawesi Barat': 'Tengah', 'Sulawesi Tengah': 'Tengah', 'Sulawesi Tenggara': 'Tengah', 'Bali': 'Tengah',
    'Gorontalo': 'Tengah', 'Sulawesi Selatan': 'Tengah',

    'Maluku': 'Timur',   'Nusa Tenggara Barat': 'Timur', 'Papua': 'Timur', 'Papua Barat': 'Timur',  'Nusa Tenggara Timur': 'Timur', 'Maluku Utara': 'Timur'
})

# Menampilkan jumlah value dari kolom 'provinsi'
data['provinsi'].value_counts()

"""#### Hapus kolom yang tidak diperlukan"""

# Membuat list kolom yang akan dihapus
kolom_yang_dihapus = ['created_at', 'username', 'device_id', 'device_version', 'home_country', 'event_id', 'id','booking_id', 'email', 'last_name', 'first_name', 'productDisplayName', 'customer_id', 'session_id',
                      'shipment_location_long', 'shipment_location_lat', 'home_location_long', 'home_location_lat', 'product_id', 'subCategory', 'articleType', 'baseColour']
data = data.drop(kolom_yang_dihapus, axis=1)

data.shape

"""#### Mengubah tipe data"""

# Mengubah tipe data pada kolom quantity dan item_price menjadi int64
data['quantity'] = data['quantity'].astype(int)
data['item_price'] = data['item_price'].astype(int)

data.info()

"""### Missing Value"""

# Cek missing value (>0%)
data_missing_value = data.isnull().sum().reset_index()
data_missing_value.columns = ['feature','total_missing_value']
data_missing_value['percentage'] = round((data_missing_value['total_missing_value']/len(data))*100,2)
data_missing_value = data_missing_value.sort_values('percentage', ascending=False).reset_index(drop=True)
data_missing_value = data_missing_value[data_missing_value['percentage']>0]
data_missing_value

"""Terdapat 5 kolom yang memiliki missing value

Handling missing value:

*   Apabila data numeric, missing value bisa diisi dengan mean atau median, tergantung dengan skew nya
*   Apabila data categoric, missing value bisa diisi dengan modus
"""

# Mengisi missing value pada data Categoric
col_object = data.select_dtypes(include = ["object"]).columns
for col in col_object :
  data[col] = data[col].fillna(data[col].mode().iloc[0])

# Mengisi missing value pada data numerik
col_numeric = data.select_dtypes(exclude=["object", "datetime64"]).columns
for i in col_numeric :
  if data[i].skew() > 0:
    data[i] = data[i].fillna(data[i].mean())
  else :
    data[i] = data[i].fillna(data[i].median())

# Mengecek ulang missing value
data.isnull().sum()

data.shape

"""### Duplicate"""

# Cek duplikat data
data.duplicated().sum()

"""Terdapat 2946419 baris yang terindikasi duplikat, sehingga baris tersebut bisa didrop (dihapus)"""

# Drop data yang terindikasi duplikat
data = data.drop_duplicates()

# Recheck duplikat data
data.duplicated().sum()

data.shape

# Mengubah tipe data kolom 'year'
data['year'] = data['year'].astype(int)

"""### Outlier"""

# Menampilkan boxplot untuk mengecek outlier
fig, ax = plt.subplots(figsize=(40,40))
sns.boxplot(data=data)

"""Terdapat outlier pada kolom total_amount dan item_price, namun adanya outlier ini akan dianggap sebagai kewajaran

###Export Data
"""

#Copy data
df_bi = data.copy()
df_bi.head()

# Export Clean Data
df_bi.to_csv('/content/drive/MyDrive/dataset/eiren_clean.csv', index=False)
df_bi.shape

"""##Data Analysis & Visualizing

###Univariate Analysis

####Gender Customer
"""

# Jumlah setiap gender customer
plt.title("Tipe Gender Customer", fontsize=14, weight="bold")
df_bi["gender_x"].value_counts().plot.bar();

# Jumlah setiap gender customer
df_bi["gender_x"].value_counts()

"""Interpretasi : dari barplot, mayoritas customer adalah bergender perempuan dibandinkan laki-laki

####Lokasi Tempat Tinggal
"""

# Jumlah wilayah tempat tinggal customer
plt.title("Wilayah Tempat Tinggal Customer", fontsize=14, weight="bold")
df_bi["provinsi"].value_counts().plot.bar();

# Jumlah wilayah tempat tinggal customer
df_bi["provinsi"].value_counts()

"""Interpretasi : mayoritas customer memiliki tempat tinggal pada wilayah Barat dibandingkan pada wilayah Tengah dan Timur

####Device Type
"""

# Jumlah tipe perangkat customer
plt.title("Tipe Perangkat Customer", fontsize=14, weight="bold")
df_bi["device_type"].value_counts().plot.bar();

# Jumlah masing-masing tipe perangkat customer
df_bi["device_type"].value_counts()

"""Interpretasi : Mayoritas customer memiliki device dengan tipe Android dibandingkan iOS

####Traffic Source
"""

# Jumlah tipe traffic customer
plt.title("Tipe Traffic Customer", fontsize=14, weight="bold")
df_bi["traffic_source"].value_counts().plot.bar();

# Jumlah masing-masing tipe traffic customer
df_bi["traffic_source"].value_counts()

"""Interpretasi : Mayoritas customer mengakses layanan e-commerce menggunakan aplikasi berbasis mobile dibandingkan melalui aplikasi berbasis web

####Payment Method
"""

# Jummlah metode pembayaran
plt.title("Tipe Metode Pembayaran Customer", fontsize=14, weight="bold")
df_bi["payment_method"].value_counts().plot.bar();

# Jummlah maisng-masing metode pembayaran
df_bi["payment_method"].value_counts()

"""Interpretasi : Mayoritas customer melakukan pembayaran menggunakan Dompet Digital dibandingkan menggunakan Credit Card dan Debit Card

#### Promo
"""

# Jumlah penggunaan promo
plt.title("Penggunaan Promo", fontsize=14, weight="bold")
df_bi["promo_code"].value_counts().plot.bar();

# Jumlah penggunaan promo
df_bi["promo_code"].value_counts()

"""Interpretasi : Mayoritas customer melakukan transaksi pada e-commerce dengan tidak menambahkan code promo dibandingkan dengan menambahkan code promo untuk memperoleh potongan harga ketika melakukan transaksi

####Season Article
"""

# Jumlah jenis season article yang dibeli customer
plt.title("Season Article", fontsize=14, weight="bold")
df_bi["season"].value_counts().plot.bar();

# Jumlah masing-masing jenis season article yang dibeli customer
df_bi["season"].value_counts()

"""Interpretasi : Mayoritas customer melakukan transaksi pada product yang digunakan pada summer atau musim panas dengan jumlah yang signifikan dibandingkan pada product kedua yaitu product yang digunakan pada musim gugur

####Usage
"""

# Jumlah usage article yang dibeli customer
plt.title("Usage Article", fontsize=14, weight="bold")
df_bi["usage"].value_counts().plot.bar();

# Jumlah masing-masing usage article yang dibeli customer
df_bi["usage"].value_counts()

"""Interpretasi : Mayoritas customer membeli product casual

####Gender Artikel
"""

# Jumlah jenis gender pada article yang dibeli customer
plt.title("Gender Article", fontsize=14, weight="bold")
df_bi["gender_y"].value_counts().plot.bar();

# Jumlah jenis gender pada article yang dibeli customer
df_bi["gender_y"].value_counts()

"""Interpretasi : Mayoritas customer membeli produk untuk laki-laki dewasa dan perempuan dewasa

####Search Keyword
"""

# Jumlah kegiatan search customer
plt.title("Search Keyword", fontsize=14, weight="bold")
df_bi["search_keywords"].value_counts().plot.bar();

from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Menentukan batas minimum frekuensi yang lebih tinggi dari 41275
minimum_freq = 56352

# Filter word_freq untuk kata-kata yang memiliki frekuensi lebih besar dari minimum_freq
filtered_word_freq = {key: val for key, val in word_freq.items() if val >= minimum_freq}

# Membuat WordCloud dengan kata-kata yang difilter
wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='magma').generate_from_frequencies(filtered_word_freq)

# Plotting WordCloud
plt.figure(figsize=(10, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# Jumlah kegiatan search custome
df["search_keywords"].value_counts()

"""###Bivariate Analysis

####Churn Berdasarkan Gender
"""

plt.figure(figsize=(10, 6))
sns.countplot(x='gender_x', hue='churn', data=df_bi, palette=['#C80F2E', 'grey'])
plt.title('Churn Berdasarkan Gender Customer')
plt.ylabel('jumlah')
plt.xticks(rotation=0)
plt.legend(['tidak churn', 'churn'])
plt.show()

"""Interpretasi: dari grafik atas, diketahui bahwa mayoritas customer churn. Mayoritas customer yang terindikasi churn adalah perempuan"""

# Menghitung jumlah data churn dan non-churn berdasarkan gender
churn_by_gender = df_bi.groupby(['gender_x', 'churn']).size().reset_index(name='jumlah')

# Menampilkan hasil
print(churn_by_gender)

"""####Churn Berdasarkan Tempat Tinggal"""

plt.figure(figsize=(10, 6))
sns.countplot(x='provinsi', hue='churn', data=df_bi, palette=['#C80F2E', 'grey'])
plt.title('Churn Berdasarkan Tempat Tinggal Customer')
plt.ylabel('jumlah')
plt.xticks(rotation=0)
plt.legend(['tidak churn', 'churn'])
plt.show()

"""Interpretasi : dari grafik di atas, dapat disimpulkan bahwa mayoritas customer berasal dari Barat memiliki tingkat churn yang tinggi. Diketahui juga mayoritas customer memiliki tempat tinggal di wilayah Barat"""

# Menghitung jumlah data churn dan non-churn berdasarkan provinsi
churn_by_province = df_bi.groupby(['provinsi', 'churn']).size().reset_index(name='jumlah')

# Menampilkan hasil
print(churn_by_province)

"""####Churn Berdasarkan Metode Pembayaran"""

plt.figure(figsize=(10, 6))
sns.countplot(x='payment_method', hue='churn', data=df_bi, palette=['#C80F2E', 'grey'])
plt.title('Churn Berdasarkan Metode Pembayaran')
plt.ylabel('jumlah')
plt.xticks(rotation=0)
plt.legend(['tidak churn', 'churn'])
plt.show()

"""Interpretasi : Mayoritas customer yang menggunakan dompet digital sebagai metode pembayaran lebih banyak yang mengalami churn."""

# Menghitung jumlah data churn dan non-churn berdasarkan metode pembayaran
churn_by_payment_method = df_bi.groupby(['payment_method', 'churn']).size().reset_index(name='jumlah')

# Menampilkan hasil
print(churn_by_payment_method)

"""#### Churn Berdasarkan Penggunaan Promo"""

plt.figure(figsize=(10, 6))
sns.countplot(x='promo_code', hue='churn', data=df_bi, palette=['#C80F2E', 'grey'])
plt.title('Churn Berdasarkan Penggunaan Promo')
plt.ylabel('jumlah')
plt.xticks(rotation=0)
plt.legend(['tidak churn', 'churn'])
plt.show()

"""Interpretasi : Mayoritas customer yang menggunakan tidak menggunakan promo untuk bertransaksi lebih banyak yang mengalami churn."""

# Menghitung jumlah data churn dan non-churn berdasarkan metode pembayaran
churn_by_promo = df_bi.groupby(['promo_code', 'churn']).size().reset_index(name='jumlah')

# Menampilkan hasil
print(churn_by_promo)

"""####Churn Berdasarkan Search Keyword"""

plt.figure(figsize=(10, 6))
sns.countplot(x='search_keywords', hue='churn', data=df_bi, palette=['#C80F2E', 'grey'])
plt.title('Churn Berdasarkan Search Keyword')
plt.ylabel('jumlah')
plt.xticks(rotation=0)
plt.legend(['tidak churn', 'churn'])
plt.show()

"""Interpretasi : Mayoritas customer yang tidak melakukan pencarian produk lebih banyak yang mengalami churn secara signifikan dibandikan tidak churn."""

# Menghitung jumlah data churn dan non-churn berdasarkan keyword pencarian
churn_by_search_keywords = df_bi.groupby(['search_keywords', 'churn']).size().reset_index(name='jumlah')

# Menampilkan hasil
print(churn_by_search_keywords)

"""####Churn Berdasarkan Status Pembayaran"""

plt.figure(figsize=(10, 6))
sns.countplot(x='payment_status', hue='churn', data=df_bi, palette=['#C80F2E', 'grey'])
plt.title('Churn Berdasarkan Status Pembayaran')
plt.ylabel('jumlah')
plt.xticks(rotation=0)
plt.legend(['tidak churn', 'churn'])
plt.show()

"""Interpretasi : Mayoritas customer mengalami pembayaran yang berhasil dibandingkan tidak berhasil secara signifikan. Customer yang mengalami pembayaran berhasil memiliki jumlah churn paling banyak."""

# Menghitung jumlah data churn dan non-churn berdasarkan status pembayaran
churn_by_payment_status = df_bi.groupby(['payment_status', 'churn']).size().reset_index(name='jumlah')

# Menampilkan hasil
print(churn_by_payment_status)

"""# **Modelling**

Untuk meminimalisir tingkat error, maka bagian modeling dan evaluation dikerjakan pada notebook ini

https://colab.research.google.com/drive/1ZwA95vF9BKZZrvJi6qIuDqKFIVzLH5Dw?usp=sharing
"""