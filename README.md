Nama : Muhammad Rifky Padjri
NPM : 2506585800
Kelas : PBP A

readme yang udah diubah buat latihan branch

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
