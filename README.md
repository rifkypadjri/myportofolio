# My Portfolio

Aplikasi portofolio berbasis Django untuk menampilkan profil, proyek, dan pengalaman. Proyek ini dikembangkan untuk tugas Pemrograman Berbasis Platform (PBP), dengan autentikasi, izin berdasarkan role, star/unstar Project, serta daftar Experience dan penambahan data melalui AJAX.

- **Nama:** Muhammad Rifky Padjri
- **NPM:** 2506585800
- **Kelas:** PBP A

## Menjalankan secara lokal

Prasyarat: Python 3.10 atau lebih baru dan pip. Jalankan perintah berikut dari direktori repository yang berisi `manage.py`.

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Pada Linux/macOS, gunakan `source env/bin/activate` untuk aktivasi. Jika PowerShell tidak mengizinkan aktivasi, gunakan `.\env\Scripts\python.exe` sebagai pengganti `python` pada perintah berikutnya.

Database lokal menggunakan SQLite secara default; PostgreSQL tidak diperlukan. Jika sudah memiliki file `.env`, pastikan `PRODUCTION=False` untuk penggunaan lokal. File `.env` tidak wajib ketika variabel tersebut belum diatur.

```powershell
python manage.py migrate
python manage.py check
python manage.py createsuperuser
python manage.py runserver
```

Buka [halaman utama](http://127.0.0.1:8000/) atau [daftar Experience](http://127.0.0.1:8000/experience/). Pembuatan superuser bersifat opsional untuk melihat daftar, tetapi diperlukan untuk mencoba modal tambah Experience. Login dengan akun tersebut melalui aplikasi atau [Django Admin](http://127.0.0.1:8000/admin/). Database baru belum berisi data; tambahkan melalui modal atau admin. Hentikan server dengan `Ctrl+C`.

Untuk menjalankan pengujian backend yang tersedia:

```powershell
python manage.py test main
```

## Dokumentasi tugas

### Tugas 1

1. Dalam struktur HTML yang saya buat, saya menggunakan beberapa elemen semantik HTML5 seperti <header>, <nav>, <section>, dan <footer>, misalnya pada pembagian <section id="about">, <section id="education">, <section id="skills">, <section id="projects">, dan <section id="contact">. Elemen-elemen ini membantu saya memecah halaman menjadi blok-blok konten yang jelas batasannya secara struktural, sehingga navigasi dengan anchor link (href="#about", href="#education", dst.) menjadi lebih sesuai dengan maknanya karena setiap target memang merepresentasikan satu unit konten yang berdiri sendiri.
   Pada awalnya, saya sempat membungkus kartu proyek (.project-card) dan item pendidikan (.timeline-item) hanya dengan <div>. Namun setelah mengevaluasi ulang, saya menyadari kedua jenis konten ini sebenarnya cocok menggunakan <article>, karena masing-masing memuat informasi yang bisa berdiri sendiri secara utuh misalnya satu kartu proyek berisi judul, deskripsi, dan tag teknologi yang tetap bermakna meski dilepas dari konteks section Projects, begitu juga satu item timeline yang memuat riwayat pendidikan atau organisasi secara mandiri. Karena itu saya mengubahnya menjadi <article class="project-card"> dan <article class="timeline-item">, tanpa perlu mengubah styling CSS sama sekali karena menggunakan nama class yang sama
   saya tidak menggunakan <aside> maupun <article> pada bagian .story-col di section About, karena keempat kolom cerita di sana ("Well, here is my story...", "My background was in Mathematics", dst.) saling bergantung secara naratif dan urutannya penting, tidak masuk akal jika salah satu kolom dibaca terpisah dari alur cerita keseluruhan, sehingga <div> sudah tepat digunakan di sana. <aside> juga tidak saya pakai karena halaman portofolio ini tidak memiliki konten sekunder seperti sidebar yang terpisah dari alur utama.

2. Tantangan utama yang saya temui ada pada tiga bagian: navigasi dan grid dua kolom di section About. Untuk navigasi, saya menggunakan pola "floating pill navigation" dengan .nav-links yang berbentuk kapsul melengkung berisi lima link. Di layar laptop atau pc, kelima link ini muat sejajar secara horizontal, tapi begitu dibuka lewat hp, kapsul tersebut menjadi terpotong. Saya mengevaluasinya dengan mengubah flex-direction pada nav menjadi column dan menambahkan flex-wrap: wrap pada .nav-links di breakpoint 768px, sekaligus mengecilkan padding dan font-size pada .nav-links a agar tetap proporsional di layar kecil.
   Tantangan kedua ada pada .story-grid di section About, yang saya desain dengan kolom dan dibaca dari kanan ke kiri. Pola kolom ini terlihat baik di desktop, tapi di layar hp kolom nya ditampilkan secara vertikal sehingga malah kolom kedua yang tampil paling atas dan urutan narasinya menjadi tidak sesuai, sehingga balik alur baca kontennya dari kiri ke kanan dengan urutan gambar-teks tetap mengikuti urutan HTML aslinya secara vertikal. S

3. salah satu batasannya yaitu di section Contact. Karena website ini murni statis, saya tidak bisa membuat form kontak yang benar-benar mengirim pesan; yang saya sediakan hanyalah link mailto: dan tautan ke GitHub serta LinkedIn, sehingga pengunjung harus keluar dari website dan membuka aplikasi email sendiri untuk menghubungi email saya. Batasan lain adalah seluruh data, daftar skill, item pendidikan, dan proyek dimasukkan langsung sebagai teks statis di HTML, sehingga setiap kali saya ingin menambah proyek baru atau memperbarui pengalaman organisasi, saya harus mengedit dan mendeploy ulang file HTML-nya secara manual, bukan cukup menambahkan data ke suatu sumber terpisah. Saya juga sempat menyiapkan class .active untuk nav-links a di CSS, namun karena tidak ada JavaScript, highlight otomatis pada link navigasi sesuai section yang sedang dilihat pengguna saat scroll belum bisa berfungsi. Berdasarkan batasan-batasan ini, fungsionalitas dinamis yang paling ingin saya tambahkan pada pengembanagn berikutnya adalah form kontak yang benar-benar fungsional dengan backend sederhana sehingga pesan bisa dikirim langsung dari website tanpa membuka aplikasi email lain, serta page lain yang spesifik membahas proyek proyek uang sudah saya kerjakan.

AI disclosure:
Dalam pengerjaan tugas ini, saya menggunakan bantuan AI (Claude) pada bagian-bagian berikut:

1. sebelum memulai pekerjaan saya berdiskusi dengan ai mengenai color palette dan tips tips agar website terlihat menarik namun tetap profesional
2. bertanya terkait cara menggunakan beberapa sintaks html/css
3. memperbaiki beberapa bagian yang saya rasa belum sesuai seoerti memperbaiki tombol nacvigasi yang terpotong saat di mobile
4. selain penggunaan ai saya juga banyak mendapatkan inspirasi dari website website berikut:
   a. https://www.marco.fyi/
   b. https://perryw-2023.webflow.io/
   c. https://www.dotconor.com/
   d. https://www.gabrielvaldivia.com/

berikut saya lampirkan juga link chat dengan ai:
https://claude.ai/share/1d58728a-834a-4cb9-881a-4b3392389238
https://share.gemini.google/M1SJOyx168q0

### Tugas 2

1. pertama browser akan mengirimkan http request ke server. Django akan menerima requestnya dan mengecek pada urls pada tingkat proyek, yaitu pada /portofolio/urls.py karena pada file tersebut kita menuliskan kode path("", include("main.urls")), request tersebut akan diteruskan ke urls milik app main yaitu pada /main/urls.py. berkas urls.py milik main akan mencocokkan url dengan daftar yang ada, saat pola ditemukan, django memanggil fungsi pada view.py yang terasosiasi. view bertindak sebagai pengendali utama, ketika mendapatkan request main mengambil data yang diperlukan dari model.py (bagian yang berkomunikasi langsung dengan database) kemudian memasukkannya ke tamplate html yang ada. setelah itu view membungkus kode HTML akhir yang sudah terisi data ke dalam objek HttpResponse dan mengembalikannya ke browser untuk ditampilkan kepada pengguna.

2. Menyimpan data portofolio pada Model (database) daripada menuliskannya langsung (hardcoding) di dalam berkas HTML template memberikan beberapa keuntungan. Pertama kemudahan oemeliharaan dan managemen data. Menambah, mengubah, atau menghapus item portofolio dapat dilakukan dengan mudah melalui Django Admin atau antarmuka lain tanpa perlu menyentuh kode program atau merestart aplikasi. Jika ditulis langsung di template, setiap perubahan data mengharuskan developer mengubah berkas HTML dan melakukan re-deploy aplikasi. Kemudian penggunaan Model memungkinkan fitur lanjutan seperti filter kata kunci, kategori, fitur pencarian, serta pengurutan data berdasarkan tanggal. Hal ini mustahil dilakukan secara fleksibel jika data bersifat statis di HTML, terakhir data portofolio yang tersimpan di Model dapat digunakan kembali di berbagai tempat lain, misalnya ditampilkan sebagai ringkasan di dashboard admin, dibuatkan API (misalnya dengan Django REST Framework), semua ini dapat dilakukan tanpa perlu menduplikasi tulisan.

3. Perintah makemigrations dan migrate pada Django memiliki fungsi yang saling melengkapi dalam mengelola perubahan skema database. Perintah makemigrations bertugas untuk membaca perubahan yang terjadi pada struktur tabel di file models.py lalu menerjemahkannya ke dalam bentuk berkas cetak biru (_blueprint_) Python di dalam folder /migrations/, tanpa mengubah database secara langsung. Sementara itu, perintah migrate berfungsi untuk mengeksekusi berkas migrasi tersebut dan menerapkan instruksi perintah SQL secara nyata ke dalam tabel database.

AI Disclosure:
penggunaan ai dilakukan untuk:

- membuat file html dan css untuk halaman baru yang ditambahkan menggunakan ai agent pada cursor
- bertanya terkait beberapa masalah teknis yang terjadi seperti tidak bisa menampilkan thumbnail gambar melalui link gdrive
- membuatkan kalimat narasi dalam bahasa inggris yang menjelaskan tentang pengalaman dan projek yang saya miliki

berikut juga saya lampirkan:

1. https://share.gemini.google/zlOlVJy8BieR
2. https://share.gemini.google/A6fGP72bzH1c
3. https://share.gemini.google/ZQoK8cS8gmVF
4. https://drive.google.com/file/d/12EcNLDJ1YtgdOL5P9TbUPAlC8NCOGPh9/view?usp=sharing


### tugas 3

1. ModelForm pada Django digunakan untuk mempermudah pembuatan form yg terkait suatu model. Dengan ModelForm, field pada form dapat dibuat berdasarkan field yang terdapat pada model sehingga kita tidak perlu mendefinisikan setiap input secara manual menggunakan HTML. Selain mengurangi kode yang berulang, ModelForm juga menyediakan validasi data secara otomatis berdasarkan tipe dan aturan field pada model. Data yang telah tervalidasi juga dapat disimpan ke database menggunakan method seperti form.save(). Hal ini membuat implementasi fitur create maupun update menjadi lebih sederhana dan konsisten dengan struktur model yang digunakan.

Sementara itu, {% csrf_token %} digunakan untuk melindungi form dari serangan Cross-Site Request Forgery (CSRF). Serangan CSRF terjadi ketika pengguna yang sudah terautentikasi dibuat mengirimkan request ke suatu aplikasi tanpa sepengetahuannya. Django menghasilkan token unik yang kemudian disertakan pada form dan diverifikasi ketika request, khususnya request POST, diterima oleh server. Dengan demikian, server dapat memastikan bahwa request tersebut berasal dari form yang sah pada aplikasi dan bukan request yang dibuat oleh pihak lain.

2. JSON (JavaScript Object Notation) lebih sering digunakan dalam pengembangan aplikasi web modern karena formatnya lebih sederhana dan ringkas dibandingkan XML. JSON merepresentasikan data menggunakan struktur seperti object dan array sehingga lebih mudah dibaca serta diproses oleh aplikasi. Sebaliknya, XML menggunakan tag pembuka dan penutup sehingga representasi data yang sama umumnya membutuhkan struktur yang lebih panjang.

Selain itu, struktur JSON sangat sesuai dengan struktur data yang digunakan pada JavaScript. JSON dapat diubah menjadi object JavaScript menggunakan JSON.parse() dan sebaliknya dapat dikonversi menggunakan JSON.stringify(). Hal tersebut membuat JSON praktis digunakan dalam komunikasi antara client dan server, terutama pada REST API dan aplikasi web yang melakukan pertukaran data secara dinamis. Ukurannya yang relatif lebih ringkas juga mengurangi data tambahan yang perlu dikirimkan dibandingkan XML. Walaupun XML tetap berguna pada sistem tertentu yang membutuhkan fitur seperti namespaces atau skema dokumen yang kompleks, JSON umumnya lebih praktis untuk kebutuhan pertukaran data pada aplikasi web modern.

3. Ketika client mengakses endpoint JSON pada aplikasi, Django terlebih dahulu menerima HTTP request dan mencocokkan URL tersebut dengan pola yang terdapat pada urls.py. URL kemudian mengarahkan request menuju fungsi view yang sesuai. Di dalam view, data yang diperlukan diambil dari database melalui Django ORM, misalnya menggunakan Model.objects.all(). Hasil operasi tersebut masih berupa QuerySet yang berisi instance model Python dan belum dapat langsung dikirimkan sebagai JSON.

Oleh karena itu, diperlukan proses serialization, yaitu proses mengubah object atau instance model Django menjadi representasi data yang dapat dikirimkan, seperti JSON. Serializer akan mengubah data model beserta field-field yang diperlukan menjadi struktur yang dapat direpresentasikan dalam format JSON. Setelah proses serialization selesai, view mengembalikan data tersebut melalui HTTP response dengan content type JSON. Data tersebut kemudian dapat diterima oleh client, diubah kembali atau di-deserialize menjadi struktur data yang dapat digunakan, lalu ditampilkan pada halaman web.

4. AI Disclosure
Dalam pengerjaan Tugas 3, saya menggunakan ChatGPT (OpenAI) sebagai alat bantu dalam proses pembelajaran dan pengembangan. AI digunakan terutama untuk membantu memahami requirement tugas, menyusun strategi implementasi berdasarkan rubrik penilaian, menjelaskan konsep yang berkaitan dengan Django seperti ModelForm, CRUD, template inheritance, CSRF, serialization, dan JSON data delivery, serta membantu menyusun jawaban pertanyaan reflektif pada README.

Strategi prompting yang saya gunakan adalah memberikan konteks tugas dan requirement terlebih dahulu, kemudian meminta AI untuk menjelaskan atau memberikan saran terhadap bagian tertentu secara spesifik. Saya tidak langsung menggunakan seluruh keluaran AI sebagai implementasi akhir, tetapi menggunakannya sebagai referensi untuk memahami pendekatan yang dapat digunakan dan kemudian menyesuaikannya dengan struktur proyek yang telah saya buat.


### Tugas 4

#### Implemented Features

1. **Authentication**

   Aplikasi menggunakan sistem autentikasi bawaan Django, yaitu `User`, `AuthenticationForm`, `UserCreationForm`, `login`, `logout`, session middleware, serta decorator `login_required`. User dapat melakukan registrasi, login, dan logout. Logout hanya menerima request POST dan dilindungi CSRF.

2. **Role dan authorization**

   - **Guest** dapat membaca halaman portfolio dan endpoint JSON, tetapi harus login untuk melakukan operasi yang mengubah data atau memberikan star.
   - **Regular User** dapat membaca data dan melakukan star/unstar, tetapi tidak dapat melakukan create, update, atau delete.
   - **Editor** merupakan user yang tergabung dalam Django Group bernama `Editor`. Editor memiliki seluruh hak Regular User dan dapat melakukan update, tetapi tidak dapat melakukan create atau delete.
   - **Superuser** dapat membaca, memberikan star, serta melakukan create, update, dan delete.

   Pemeriksaan authorization diterapkan pada server melalui helper dan decorator di `main/permissions.py`. Conditional rendering pada template hanya digunakan untuk menyesuaikan tampilan tombol dan bukan sebagai pengganti pemeriksaan server-side. Policy yang sama juga diterapkan pada Django Admin untuk model portfolio.

3. **Role-based CRUD**

   Operasi create dan delete hanya dapat dilakukan superuser. Operasi update dapat dilakukan Editor dan superuser. Guest diarahkan ke halaman login, sedangkan authenticated user yang tidak memiliki role yang sesuai memperoleh respons HTTP 403 Forbidden. Delete hanya menerima request POST.

4. **Star dan unstar Project**

   Model `Project` memiliki relasi `ManyToManyField` terhadap Django User melalui field `starred_by`. User yang sudah login, termasuk Regular User, Editor, dan superuser, dapat menambah atau menghapus star melalui endpoint POST `toggle_star`. Relasi Many-to-Many menjaga agar pasangan Project dan User tidak tersimpan secara duplikat. Guest melihat link login, bukan form POST star.

   Halaman Project menampilkan jumlah star dan status apakah current user sudah memberi star. Jumlah star dihitung dengan anotasi `Count`, sedangkan status current user ditentukan dengan anotasi `Exists` agar template tidak melakukan query relasi berulang untuk setiap Project.

5. **Session dan cookie**

   Django session digunakan untuk mempertahankan status autentikasi. Project juga memiliki cookie `last_login` dari implementasi tutorial sebelumnya. Cookie tersebut diatur setelah login, ditampilkan pada halaman utama, dan dihapus saat logout. Cookie `last_login` bukan pengganti session autentikasi Django.

6. **Kompatibilitas endpoint JSON**

   Endpoint berikut tetap tersedia sebagai endpoint read-only:

   - `/api/projects/`
   - `/api/experiences/`

   Penambahan relasi star tidak mengubah format dasar serializer dan tidak mengekspos relasi `starred_by`. Field JSON dibatasi secara eksplisit sehingga password, session, credential autentikasi, dan informasi sensitif user tidak ikut dikirimkan.

#### AI Disclosure

Dalam pengerjaan Tugas 4, OpenAI Codex digunakan sebagai alat bantu pengembangan. Bantuan AI mencakup implementasi dan pengujian role-based CRUD, integrasi star/unstar, pengamanan endpoint JSON dan CSRF, dan membuat readme bagian implemented feature.

Strategi prompting dilakukan secara bertahap. Setiap prompt memberikan konteks repository, satu fokus pekerjaan, matriks role atau requirement yang eksplisit, batasan seperti tidak melakukan refactor besar dan tidak membuat commit, serta permintaan verifikasi melalui Django system check dan test suite. Tahapan dipisahkan antara fondasi role, authorization server-side, conditional UI, model star, backend toggle, integrasi template, security audit, dan dokumentasi akhir.

Jawaban AI tidak dianggap pasti benar dan digunakan mentah mentah. Selama sesi pengembangan, perubahan selalu diperiksa melalui pengecekan perubahan, `python manage.py check`, dan pengujian akses URL langsung. 

Keterbatasan AI yang saya temukan adalah AI tidak dapat menggantikan pengujian visual/interaksi browser oleh developer, sehingga masih sangat dibutuhkan manusia untuk mengecek hasil tampilan dari web yang dibuat

### Tugas 5

#### Ringkasan implementasi

- **Daftar AJAX:** template awal menampilkan struktur halaman. JavaScript mengambil JSON dengan `fetch()`, lalu `renderExperienceItems()` membangun kartu di DOM, termasuk jumlah star dan status star pengguna. Daftar dapat dibaca tanpa login.
- **Pencarian:** judul dan deskripsi difilter melalui Django ORM menggunakan `icontains`. Debounce 300 ms mengurangi request; pembatalan dan versi request mencegah hasil lama menimpa hasil terbaru. Query kosong mengembalikan seluruh daftar.
- **Tambah melalui modal:** hanya superuser melihat tombol tambah. POST menggunakan `FormData`, token CSRF dari form, dan validasi `ExperienceForm`. Authorization tetap diperiksa di view. Setelah berhasil, modal direset/ditutup dan daftar diambil ulang dengan pencarian aktif, tanpa reload halaman.
- **Umpan balik:** tersedia state loading, kosong, dan error, pesan validasi per field, serta toast melalui `showToast()` yang sudah ada. Tombol menampilkan "Menyimpan..." dan dinonaktifkan selama submit. Pencarian dilengkapi tombol hapus dan jumlah hasil.
- **Keamanan dan pemeliharaan:** rendering teks memakai `textContent`, URL thumbnail divalidasi, dan judul/deskripsi disanitasi dengan `strip_tags()`. Fungsi fetch, rendering, pencarian, dan penanganan form dipisahkan tanpa mengubah aturan role maupun star/unstar Project dari Tugas 4.

| Metode | Endpoint | Perilaku |
| --- | --- | --- |
| GET | `/api/experiences/?q=keyword` | Daftar JSON publik; `q` opsional untuk pencarian. |
| POST | `/experiences/add-ajax/` | `201` berhasil, `400` validasi gagal, `403` akses ditolak; membutuhkan superuser dan CSRF yang valid. |

Alur halaman: **template struktur → fetch JSON → pemeriksaan respons → rendering DOM**. Kegagalan request menampilkan state error; hasil kosong menampilkan pesan kosong. Logika utama tersedia di [experience.js](static/js/experience.js), [views.py](main/views.py), dan [forms.py](main/forms.py). Penjelasan tambahan: [pencarian](docs/experience-search.md), [perlindungan XSS](docs/experience-xss.md), dan [modal tambah](docs/experience-create.md).

#### Jawaban refleksi

1. Apa itu debouncing dan mengapa penting untuk pencarian AJAX?

   Debouncing adalah teknik menunda pemanggilan fungsi sampai tidak ada event baru selama interval tertentu. Pada pencarian Experience di `static/js/experience.js`, fungsi `debounce()` menggunakan `setTimeout()` dan membatalkan timer sebelumnya dengan `clearTimeout()`. Pencarian dijalankan setelah pengguna berhenti mengetik selama **300 ms**. Jadi, mengetik beberapa karakter dengan cepat biasanya menghasilkan satu request setelah jeda, bukan satu request untuk setiap karakter.

   Teknik ini mengurangi request yang tidak diperlukan, beban server, dan perubahan tampilan yang terlalu sering. Request menuju `/api/experiences/?q=keyword` untuk mencari judul atau deskripsi. Implementasi juga menggunakan `AbortController` dan pemeriksaan versi request agar hasil pencarian lama tidak menimpa hasil terbaru. Debouncing mengurangi frekuensi request, sedangkan kedua mekanisme tersebut mencegah race condition.

2. Apa fungsi `await` pada `fetch()` dan apa yang terjadi jika tidak digunakan?

   `fetch()` bekerja secara asynchronous dan langsung mengembalikan **Promise**, bukan objek `Response`. Dalam fungsi `async`, `await fetch()` menunda kelanjutan fungsi tersebut sampai Promise selesai dan memberikan objek `Response`. Proses ini tidak memblokir antarmuka browser. Selanjutnya, `await response.json()` diperlukan untuk menunggu pembacaan dan parsing body respons menjadi data JavaScript. Pada `fetchExperienceData()`, data yang sudah tersedia kemudian diteruskan ke renderer.

   Tanpa `await`, variabel hasil `fetch()` masih berupa Promise. Mengaksesnya seolah-olah sudah menjadi `Response`, misalnya memanggil `.json()`, akan gagal. Alternatif yang benar adalah menangani Promise menggunakan `.then()` dan `.catch()`. Dengan `await`, penolakan Promise dapat ditangani melalui `try/catch`. Respons HTTP seperti 400 atau 500 tidak otomatis membuat `fetch()` menolak Promise, sehingga aplikasi tetap perlu memeriksa `response.ok` atau `response.status`.

3. Apa itu XSS dan mengapa rendering melalui AJAX/JavaScript perlu perhatian lebih?

   XSS (*Cross-Site Scripting*) terjadi ketika input tidak tepercaya ditafsirkan sebagai kode yang dapat berjalan di browser pengguna. Contohnya, `<img src="x" onerror="alert('XSS!')">` dapat menjalankan event handler jika dimasukkan sebagai HTML tanpa perlindungan.

   Django secara default melakukan **auto-escaping** pada variabel template seperti `{{ experience.title }}`, sehingga karakter khusus HTML ditampilkan sebagai teks. Data JSON yang diterima JavaScript tidak otomatis melewati auto-escaping template tersebut. Jika developer memasukkannya langsung ke `innerHTML` melalui template string, browser akan mem-parsing isinya sebagai HTML. AJAX sendiri tidak menyebabkan XSS; risikonya muncul dari cara data dimasukkan ke DOM.

   Proyek ini menggunakan `escapeHtml()` pada rendering berbasis HTML string di Projects. Experience menggunakan `textContent` melalui helper `element()`, sehingga input ditampilkan sebagai teks tanpa diparsing sebagai HTML. URL thumbnail juga diperiksa agar hanya memakai HTTP/HTTPS. Di server, `ExperienceForm.clean_title()` dan `clean_description()` menggunakan `strip_tags()` untuk menghapus tag sebelum data disimpan; input yang menjadi kosong ditolak. Sanitasi input ini melengkapi perlindungan output, bukan menggantikannya: `strip_tags()` tidak menjamin suatu string aman untuk dimasukkan sebagai HTML.

#### AI Disclosure

- **Alat:** OpenAI Codex digunakan untuk membantu pengembangan Tugas 5, termasuk menghasilkan/mengubah kode dan dokumentasi serta menjalankan pemeriksaan. 
- **Bagian yang dibantu:** rendering AJAX Experience, audit XSS, pencarian dengan debounce, endpoint create dan ModelForm, sanitasi input, modal, toast, refactoring, pengujian fungsional, perbaikan UX kecil
- **Strategi prompting:** pekerjaan dibagi menjadi prompt bertahap dengan satu fokus, konteks file/repository, requirement, batasan, dan skenario uji. Prompt meminta penggunaan pola Tutorial 05 yang sudah ada, pemeliharaan fungsi Tugas 4, dan verifikasi role, status HTTP, CSRF, XSS, serta kegagalan request. Tahap dokumentasi secara eksplisit melarang perubahan kode aplikasi.
- **Verifikasi yang dapat dirujuk:** [pengujian Django](main/tests.py) mencakup izin akses, validasi/sanitasi ModelForm, pencarian, dan endpoint AJAX. Catatan XSS dan modal menjelaskan pengujian DOM serta batasannya. Pengujian otomatis oleh AI tidak dianggap sebagai bukti pemeriksaan manual oleh pengembang. **[DIISI MANUAL: bagian yang diimplementasikan/dikoreksi sendiri, hasil review perubahan, dan pengujian manual yang benar-benar dilakukan; sertakan tanggal atau bukti.]**
- **Keterbatasan:** pengujian DOM yang dicatat menggunakan simulasi popover dan tidak membuktikan tampilan atau interaksi modal pada browser nyata. Pemeriksaan visual, fokus keyboard, toast, dan console browser perlu dikonfirmasi oleh pengembang. **[DIISI MANUAL: contoh saran AI yang keliru dan koreksi manual jika benar-benar terjadi; belum ada bukti yang cukup untuk mengklaim contoh tertentu.]**
- **Referensi prompt:** **[DIISI MANUAL: tautan berbagi percakapan, ekspor, atau log prompt Tugas 5 sesuai ketentuan mata kuliah.]** Tautan AI pada bagian tugas sebelumnya bukan log Tugas 5.
