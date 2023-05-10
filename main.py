# File utama program ini
from flask import Flask, flash, session, render_template,\
    request, redirect, url_for
from flask_session import Session
from datetime import datetime, date
import pymysql.cursors
import re

app = Flask(__name__)
app.secret_key = "Smansa"

#Session disimpan pada sistem dan tidak permanen
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = cursor = None

# Deklarasi variabel global status berhasil/error untuk diakses beberapa fungsi
Stat = True
lanjut = True
# Variabel dummy untuk menguji jika gender = P maka perempuan, sebaliknya laki-laki
gend = "P"

#Akses database
def openDb():
    global conn, cursor
    conn = pymysql.connect(
        host= 'localhost',
        user= 'root',
        password= "",
        db= 'smansa'
    )
    cursor = conn.cursor()

#Keluar database
def closeDb():
    global conn, cursor
    cursor.close()
    conn.close()

#Verifikasi login berdasarkan hak akses
def verifLogin(a):
    if not 'login' in session: #Jika belum login
        logout()
        flash('Silahkan login terlebih dahulu')
        return False
    elif not session["akses"]==a: #Jika sudah login tapi beda akses
        logout()
        flash('Akun ini tidak memiliki akses')
        flash('Silahkan login kembali')
        return False
    return True

#Penamaan hari berdasarkan angka
def cekHari(dow):
    nmHr = ("","Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu")
    return nmHr[dow];

#Penamaan bulan berdasarkan angka
def cekBulan(mm):
    bln = ("","Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember")
    return bln[mm];

#Fungsi untuk membersihkan session ketika logout
@app.route('/logout')
def logout():
    session.pop('login', None)
    session.pop('nama', None)
    session.pop('id', None)
    session.pop('akses', None)
    return redirect('/')

#Halaman login
@app.route('/', methods = ['GET', 'POST'])
def index():
    #Jika user menekan tombol login
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        openDb()
        #Verifikasi login
        #Username bisa id atau email, bebas
        username = request.form['username']
        password = request.form['password']
        #Cek jika akun benar ada atau tidak
        sql = "SELECT * FROM user where (username = %s OR email = %s) AND password= %s"
        cursor.execute(sql, (username, username, password))
        login = cursor.fetchone()
        #Jika akun ditemukan dan cocok
        if login:
            #Simpan semua data user yang login ke session
            session['login'] = True
            session['nama'] = login[1]
            session['id'] = login[0]
            session['akses'] = login[4]
            #Login berhasil, lanjut ke pengecekan hak akses
            if login[4] == 1:
                return redirect(url_for('admin')) #Login admin
            elif login[4] == 2:
                return redirect(url_for('guru')) #Login guru
            elif login[4] == 3:
                return redirect(url_for('siswa')) #Login siswa
            elif login[4] == 4:
                return redirect(url_for('perpus')) #Login perpustakaan
            else:
                flash('Akun tidak valid') #Hak akses tidak ditemukan atau tidak valid, antisipasi error
                return redirect(request.url)
        #Login gagal karena username atau password kosong
        elif username == "" or password == "":
            flash('Username atau password tidak boleh kosong!')
        #Login gagal karena username atau password salah
        else:
            flash('Username atau password salah')
        closeDb()
    return render_template('index.html')


''' Akses Admin '''
@app.route('/dashboard_admin', methods = ['GET', 'POST'])
def admin():
    if verifLogin(1):
        openDb()
        # Fetch hari & tanggal saat ini
        tanggal = date.today()
        d = tanggal.strftime("%d")
        m = cekBulan(tanggal.month)
        y = tanggal.strftime("%Y")
        # dt = tanggal
        dt = d + " " + m + " " + y
        dow = tanggal.isoweekday()
        # numHari = hari
        numHari = cekHari(dow)

        # Fetch jumlah guru
        sql = "SELECT COUNT(*) FROM guru"
        cursor.execute(sql)
        res = cursor.fetchone()
        numGuru = res[0]

        # Fetch jumlah siswa
        sql = "SELECT COUNT(*) FROM siswa"
        cursor.execute(sql)
        res = cursor.fetchone()
        numSiswa = res[0]

        # Fetch jumlah kelas
        sql = "SELECT COUNT(*) FROM kelas"
        cursor.execute(sql)
        res = cursor.fetchone()
        numKelas = res[0]

        # Fetch jumlah staf
        sql = "SELECT COUNT(*) FROM user WHERE username NOT IN('admin') AND access = 1 OR access = 4"
        cursor.execute(sql)
        res = cursor.fetchone()
        numStaf = res[0]

        closeDb()
        return render_template('admin/dashboard_admin.html', guru=numGuru, siswa=numSiswa, hari=numHari, tanggal=dt, kelas=numKelas, staf=numStaf)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_guru', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_admin/data_guru/<int:page>', methods = ['GET', 'POST'])
def dataguru(page):
    if verifLogin(1):
        openDb()
        global lanjut, Stat
        pencarian = ""
        prev = page-1
        next = page+1
        counter = prev*10
        #Ambil daftar guru dari database
        sql = "SELECT * FROM guru ORDER BY nama"
        cursor.execute(sql)
        guruAll = cursor.fetchall()
        # Slice data yang akan ditampilkan sebanyak 10 baris
        guru = guruAll[counter:page * 10]
        # Data slice halaman selanjutnya
        nextPage = guruAll[page * 10:next * 10]
        # Jika halaman selanjutnya kosong
        if not nextPage:
            lanjut = False
        if request.method == 'POST':
            # Jika user melakukan searching
            if request.form['search']:
                # Searching dengan mencocokkan nama guru
                try:
                    pencarian = request.form['search']
                    sql = "SELECT * FROM guru WHERE nama LIKE '%" + request.form['search'] + "%' ORDER BY nama"
                    cursor.execute(sql)
                    guru = cursor.fetchall()
                    lanjut = False
                except Exception as err:
                    Stat = False
                    flash('Terjadi kesalahan')
                    flash(err)
        # Jika databasenya kosong
        if not guru:
            guru = False
        closeDb()
        return render_template('admin/data_guru.html', count=counter, guru=guru, prev=prev, next=next, lanjut=lanjut, status=Stat, pencarian=pencarian)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/edit_guru/<id>', methods = ['GET', 'POST'])
def editguru(id):
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat
        cursor.execute('SELECT * FROM guru WHERE nuptk = %s', (id))
        data = cursor.fetchone()

        # Ambil list agama untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT * FROM agama')
        agam = cursor.fetchall()

        # Jika user menekan tombol submit, maka mengumpulkan semua data yang ada di form
        if request.method == 'POST':
            try:
                nuptk = request.form['nuptk']
                nama = request.form['nama']
                # Username = nama tanpa spasi ataupun simbol, hanya alphanumeric
                username = ''.join(us for us in nama if us.isalnum()).lower()
                jk = request.form['gender']
                agama = request.form['aga']
                email = request.form['email']
                telp = request.form['tel']
                detail = (nama, jk, agama, email, telp, nuptk)
                detail2 = (username, email, nuptk)
                # Update data guru
                cursor.execute(
                    'UPDATE guru SET nama = %s, jeniskelamin = %s, agama = %s, email = %s, telepon = %s WHERE nuptk = %s',
                    detail)
                conn.commit()
                # Update data user guru
                cursor.execute('UPDATE user SET username = %s, email = %s WHERE userid = %s', detail2)
                conn.commit()
                Stat = True
                flash('Data berhasil diubah')
                closeDb()
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('dataguru'))
        closeDb()
        return render_template('admin/edit_guru.html', data=data, ag=agam, gend=gend)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/hapus_guru/<id>', methods = ['GET', 'POST'])
def hapusguru(id):
    if verifLogin(1):
        openDb()
        global Stat
        cursor.execute('SELECT * FROM guru WHERE nuptk = %s', (id))
        data = cursor.fetchone()

        # Jika user mengkonfirm hapusdata
        if request.method == 'POST':
            try:
                # Hapus guru dari daftar guru
                cursor.execute('DELETE FROM guru WHERE nuptk = %s', (id))
                conn.commit()
                # Hapus guru dari daftar user
                cursor.execute('DELETE FROM user WHERE userid = %s', (id))
                conn.commit()
                Stat = True
                flash('Data berhasil dihapus')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('dataguru'))
        closeDb()
        return render_template('admin/hapus_guru.html', data=data, gend=gend)
    else:
        return redirect(url_for('index'))
@app.route('/dashboard_admin/tambah_guru', methods = ['GET', 'POST'])
def tambahguru():
    if verifLogin(1):
        openDb()
        # Untuk masuk ke form upload guru
        tipe="guru"

        # Ambil list agama untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT * FROM agama')
        aga = cursor.fetchall()

        # Jika user mensubmit form
        if request.method == 'POST':
            try:
                nuptk = request.form['nuptk']
                nama = request.form['nama']
                # Username = nama tanpa spasi ataupun simbol, hanya alphanumeric
                username = ''.join(nama.split()).lower()
                print(username)
                jk = request.form.get('gender')
                ag = request.form.get('agama')
                em = request.form['email']
                tele = request.form['tel']
                detail = (nuptk, nama, jk, ag, em, tele)
                detail2 = (nuptk, username, em, tele, 2)
                # Tambahkan data ke table guru
                cursor.execute('INSERT INTO guru VALUES (%s, %s, %s, %s, %s, %s)', detail)
                conn.commit()

                # Tambahkan data ke table user sebagai guru
                cursor.execute('INSERT INTO user VALUES (%s, %s, %s, %s, %s)', detail2)
                conn.commit()
                Stat = True
                flash('Data berhasil ditambahkan')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('dataguru'))
        closeDb()
        return render_template('admin/tambah_guru.html', tipe=tipe, aga=aga)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_siswa', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_admin/data_siswa/<int:page>', methods = ['GET', 'POST'])
def datasiswa(page):
    if verifLogin(1):
        openDb()
        global lanjut, Stat
        prev = page - 1
        next = page + 1
        counter = prev*10
        # Ambil daftar siswa dari database
        sql = "SELECT s.nis, s.nama, s.jeniskelamin, s.agama, s.email, s.telepon, k.namakelas FROM siswa s LEFT JOIN rombel r ON s.nis = r.anggota LEFT JOIN kelas k ON r.kelas = k.kelas ORDER BY s.nama"
        cursor.execute(sql)
        siswaAll = cursor.fetchall()
        # Slice data yang akan ditampilkan sebanyak 10 baris
        siswa = siswaAll[counter:page*10]
        # Data slice halaman selanjutnya
        nextPage = siswaAll[page*10:next*10]
        # Jika halaman selanjutnya kosong
        if not nextPage:
            lanjut = False
        if request.method == 'POST':
            # Jika user melakukan searching
            if request.form['search']:
                # Searching dengan mencocokkan nama siswa
                try:
                    sql = "SELECT s.nis, s.nama, s.jeniskelamin, s.agama, s.email, s.telepon, k.namakelas FROM siswa s LEFT JOIN rombel r ON s.nis = r.anggota LEFT JOIN kelas k ON r.kelas = k.kelas WHERE s.nama LIKE '%" + request.form['search'] + "%' ORDER BY s.nama"
                    cursor.execute(sql)
                    siswa = cursor.fetchall()
                    lanjut = False
                except Exception as err:
                    Stat = False
                    flash('Terjadi kesalahan')
                    flash(err)
        # Jika databasenya kosong
        if not siswa:
            siswa = False
        return render_template('admin/data_siswa.html', count=counter, siswa=siswa, prev=prev, next=next, lanjut=lanjut, status=Stat)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/edit_siswa/<id>', methods = ['GET', 'POST'])
def editsiswa(id):
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat
        # Ambil data siswa yang akan diedit
        sql = "SELECT s.nis, s.nama, s.jeniskelamin, s.agama, s.email, s.telepon, k.kelas, k.namakelas FROM siswa s LEFT JOIN rombel r ON s.nis = r.anggota LEFT JOIN kelas k ON r.kelas = k.kelas WHERE s.nis = %s"
        cursor.execute(sql, id)
        data = cursor.fetchone()

        # Ambil list agama untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT * FROM agama')
        agam = cursor.fetchall()

        # Ambil list kelas untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT kelas, namakelas FROM kelas')
        kls = cursor.fetchall()

        # Jika user menekan tombol submit, maka mengumpulkan semua data yang ada di form
        if request.method == 'POST':
            try:
                nis = request.form['nis']
                nama = request.form['nama']
                # Username = nama tanpa spasi ataupun simbol, hanya alphanumeric
                username = ''.join(us for us in nama if us.isalnum()).lower()
                jk = request.form['gender']
                agama = request.form['aga']
                email = request.form['email']
                telp = request.form['tel']
                kelas = request.form.get('kls')
                detail = (nama, jk, agama, email, telp, nis)
                detail2 = (kelas, nis)
                detail3 = (username, email, nis)
                # Update data siswa
                cursor.execute(
                    'UPDATE siswa SET nama = %s, jeniskelamin = %s, agama = %s, email = %s, telepon = %s WHERE nis = %s',
                    detail)
                conn.commit()
                # Update data kelas siswa
                cursor.execute('UPDATE rombel SET kelas = %s WHERE anggota = %s', detail2)
                conn.commit()
                # Update data user siswa
                cursor.execute('UPDATE user SET username = %s, email = %s WHERE userid = %s', detail3)
                conn.commit()
                Stat = True
                flash('Data berhasil diubah')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('datasiswa'))
        return render_template('admin/edit_siswa.html', data=data, ag=agam, kls=kls, gend=gend)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/hapus_siswa/<id>', methods = ['GET', 'POST'])
def hapussiswa(id):
    if verifLogin(1):
        openDb()
        global Stat
        # Ambil data siswa yang akan dihapus
        sql = "SELECT s.nis, s.nama, s.jeniskelamin, s.agama, s.email, s.telepon, k.kelas, k.namakelas FROM siswa s LEFT JOIN rombel r ON s.nis = r.anggota LEFT JOIN kelas k ON r.kelas = k.kelas WHERE s.nis = %s"
        cursor.execute(sql, id)
        data = cursor.fetchone()

        # Jika user mengkonfirm hapusdata
        if request.method == 'POST':
            try:
                # Hapus siswa dari daftar siswa
                cursor.execute('DELETE FROM siswa WHERE nis = %s', (id))
                conn.commit()
                # Hapus siswa dari daftar rombel kelas
                cursor.execute('DELETE FROM rombel WHERE anggota = %s', (id))
                conn.commit()
                # Hapus siswa dari daftar user
                cursor.execute('DELETE FROM user WHERE userid = %s', (id))
                conn.commit()
                Stat = True
                flash('Data berhasil dihapus')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('datasiswa'))
        return render_template('admin/hapus_siswa.html', data=data, gend=gend)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/tambah_siswa', methods = ['GET', 'POST'])
def tambahsiswa():
    if verifLogin(1):
        openDb()
        # Untuk masuk ke form upload siswa
        tipe="siswa"

        # Ambil list agama untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT * FROM agama')
        aga = cursor.fetchall()

        # Ambil list kelas untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT kelas, namakelas FROM kelas')
        kls = cursor.fetchall()

        # Jika user mensubmit form
        if request.method == 'POST':
            try:
                nis = request.form['nis']
                nama = request.form['nama']
                # Username = nama tanpa spasi ataupun simbol, hanya alphanumeric
                username = ''.join(us for us in nama if us.isalnum()).lower()
                jk = request.form.get('gender')
                ag = request.form.get('agama')
                em = request.form['email']
                tele = request.form['tel']
                kelas = request.form.get('kls')
                detail = (nis, nama, jk, ag, em, tele)
                detail2 = (nis, username, em, tele, 3)
                detail3 = (kelas, nis)
                # Tambahkan data ke table siswa
                cursor.execute('INSERT INTO siswa VALUES (%s, %s, %s, %s, %s, %s)', detail)
                conn.commit()

                # Tambahkan data ke table user sebagai siswa
                cursor.execute('INSERT INTO user VALUES (%s, %s, %s, %s, %s)', detail2)
                conn.commit()

                # Tambahkan data siswa ke table rombel
                cursor.execute('INSERT INTO rombel VALUES (%s, %s)', detail3)
                conn.commit()
                Stat = True
                flash('Data berhasil ditambahkan')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('datasiswa'))
        closeDb()
        return render_template('admin/tambah_siswa.html', tipe=tipe, aga=aga, kls=kls)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/upload_file/<tipe>', methods = ['GET', 'POST'])
def formupload(tipe):
    if verifLogin(1):
        openDb()
        # Klasifikasi tipe file yang diupload
        if tipe == 'siswa':
            siswa = True
            guru = False
        elif tipe == 'guru':
            guru = True
            siswa = False

        # Jika user menekan tombol upload guru
        if request.method == 'POST' and guru:
            try:
                Stat = True
                flash('Data berhasil ditambahkan')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('dataguru'))
        # Jika user menekan tombol upload siswa
        elif request.method == 'POST' and siswa:
            try:
                Stat = True
                flash('Data berhasil ditambahkan')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('datasiswa'))
        closeDb()
        return render_template('admin/form_upload.html', siswa=siswa, guru=guru, tipe=tipe)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_kelas', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_admin/data_kelas/<int:page>', methods = ['GET', 'POST'])
def datakelas(page):
    if verifLogin(1):
        openDb()
        global Stat, lanjut
        prev = page - 1
        next = page + 1
        counter = prev * 10
        # Ambil daftar kelas, nama wali kelas, dan jumlah siswa dari database
        sql = "SELECT k.kelas, k.namakelas, g.nama, COUNT(r.anggota) FROM kelas k LEFT JOIN guru g ON k.walikelas = g.nuptk LEFT JOIN rombel r ON k.kelas = r.kelas GROUP BY k.kelas ORDER BY k.kelas ASC"
        cursor.execute(sql)
        kelasAll = cursor.fetchall()
        # Slice data yang akan ditampilkan sebanyak 10 baris
        kelas = kelasAll[counter:page * 10]
        # Data slice halaman selanjutnya
        nextPage = kelasAll[page * 10:next * 10]
        # Jika halaman selanjutnya kosong
        if not nextPage:
            lanjut = False
        # Jika databasenya kosong
        if not kelas:
            kelas = False
        closeDb()
        return render_template('admin/data_kelas.html', count=counter, kelas=kelas, prev=prev, next=next, lanjut=lanjut, status=Stat)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/edit_kelas/<kode>', methods = ['GET', 'POST'])
def editkelas(kode):
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat

        # Ambil data yang akan diedit
        cursor.execute(
            'SELECT k.kelas, k.namakelas, g.nama FROM kelas k LEFT JOIN guru g ON k.walikelas = g.nuptk WHERE k.kelas = %s',
            (kode))
        data = cursor.fetchone()

        # Ambil list guru yang belum menjabat sebagai wali kelas untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT nuptk, nama FROM guru WHERE NOT EXISTS (SELECT walikelas FROM kelas WHERE guru.nuptk = kelas.walikelas)')
        wali = cursor.fetchall()

        # Konfirm edit kelas
        if request.method == 'POST':
            try:
                namakelas = request.form['kelas']
                kodekelas = namakelas.replace(" ", "_")
                namawali = request.form['wali']
                # Cek id wali yang dipilih
                cursor.execute('SELECT nuptk FROM guru WHERE nama = %s', namawali)
                kodeguru = cursor.fetchone()
                info = (kodekelas, namakelas, kodeguru[0], kode)
                print(info)
                # Update data kelas
                cursor.execute('UPDATE kelas SET kelas = %s, namakelas = %s, walikelas = %s WHERE kelas = %s', info)
                conn.commit()
                Stat = True
                flash('Data berhasil diubah')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('datakelas'))
        return render_template('admin/edit_kelas.html', data=data, wali=wali)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/hapus_kelas/<kode>', methods=['GET', 'POST'])
def hapuskelas(kode):
    if verifLogin(1):
        openDb()
        global Stat
        cursor.execute('SELECT k.kelas, k.namakelas, g.nama FROM kelas k LEFT JOIN guru g ON k.walikelas = g.nuptk WHERE k.kelas = %s', (kode))
        kelas = cursor.fetchone()

        # Jika user mengkonfirm hapusdata
        if request.method == 'POST':
            try:
                cursor.execute('DELETE FROM kelas WHERE kelas = %s', (kode))
                conn.commit()
                '''cursor.execute('DELETE FROM rombel WHERE kelas = %s', (kode))
                conn.commit()'''
                Stat = True
                flash('Data berhasil dihapus')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('datakelas'))
        return render_template('admin/hapus_kelas.html', data=kelas)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/tambah_kelas', methods = ['GET', 'POST'])
def tambahkelas():
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat
        # Ambil list guru yang belum menjabat sebagai wali kelas untuk ditampilkan pada pilihan dropdown
        cursor.execute(
            'SELECT nuptk, nama FROM guru WHERE NOT EXISTS (SELECT walikelas FROM kelas WHERE guru.nuptk = kelas.walikelas)')
        wali = cursor.fetchall()
        if request.method == 'POST':
            try:
                namakelas = request.form['kelas']
                kodekelas = namakelas.replace(" ", "_")
                walikelas = request.form.get('wali')
                detail = (kodekelas, namakelas, walikelas)
                cursor.execute('INSERT INTO kelas VALUES (%s, %s, %s)', detail)
                conn.commit()
                Stat = True
                flash('Data berhasil ditambahkan')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('datakelas'))
        closeDb()
        return render_template('admin/tambah_kelas.html', wali=wali)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_rombel/<kode>', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_admin/data_rombel/<kode>/<int:page>', methods = ['GET', 'POST'])
def datarombel(kode, page):
    if verifLogin(1):
        openDb()
        global Stat, lanjut
        prev = page - 1
        next = page + 1
        counter=prev*10
        # Ambil nama kelas dari kode kelas
        sql = "SELECT kelas, namakelas FROM kelas WHERE kelas = %s"
        cursor.execute(sql, kode)
        kelas = cursor.fetchone()
        # Ambil daftar siswa kelas tersebut dari database
        sql = "SELECT s.nis, s.nama FROM siswa s LEFT JOIN rombel r ON s.nis = r.anggota WHERE r.kelas = %s ORDER BY s.nama"
        cursor.execute(sql, kode)
        rombelAll = cursor.fetchall()
        # Slice data yang akan ditampilkan sebanyak 10 baris
        rombel = rombelAll[counter:page * 10]
        # Data slice halaman selanjutnya
        nextPage = rombelAll[page * 10:next * 10]
        # Jika halaman selanjutnya kosong
        if not nextPage:
            lanjut = False
        # Jika databasenya kosong
        if not rombel:
            rombel = False
        closeDb()
        return render_template('admin/data_rombel.html', kode=kode, kelas=kelas, count=counter, rombel=rombel, prev=prev, next=next, lanjut=lanjut, status=Stat)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/edit_rombel/<id>', methods = ['GET', 'POST'])
def editrombel(id):
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat
        # Ambil data siswa yang akan diedit
        sql = "SELECT s.nis, s.nama, k.kelas, k.namakelas FROM siswa s LEFT JOIN rombel r ON s.nis = r.anggota LEFT JOIN kelas k ON r.kelas = k.kelas WHERE s.nis = %s"
        cursor.execute(sql, id)
        data = cursor.fetchone()

        # Ambil list kelas untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT kelas, namakelas FROM kelas')
        kls = cursor.fetchall()

        # Jika user menekan tombol submit, maka mengumpulkan semua data yang ada di form
        if request.method == 'POST':
            try:
                nis = request.form['nis']
                kelas = request.form.get('kls')
                detail = (kelas, nis)

                # Update data kelas siswa
                cursor.execute('UPDATE rombel SET kelas = %s WHERE anggota = %s', detail)
                conn.commit()

                Stat = True
                flash('Data berhasil diubah')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('datarombel', kode=data[2]))
        return render_template('admin/edit_rombel.html', data=data, kls=kls)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_jadwal', methods = ['GET', 'POST'])
def datajadwal():
    if verifLogin(1):
        openDb()
        # Ambil daftar kelas dari database
        sql = "SELECT kelas, namakelas FROM kelas ORDER BY namakelas"
        cursor.execute(sql)
        listKelas = cursor.fetchall()
        closeDb()
        return render_template('admin/data_jadwal.html', kelas=listKelas)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/jadwal/<kode>', methods = ['GET', 'POST'], defaults={'hari':"Senin"})
@app.route('/dashboard_admin/jadwal/<kode>/<string:hari>', methods = ['GET', 'POST'])
def jadwal(kode, hari):
    if verifLogin(1):
        openDb()
        global Stat
        tambah = True
        # Ambil nama kelas dari kode kelas
        sql = "SELECT kelas, namakelas FROM kelas WHERE kelas = %s"
        cursor.execute(sql, kode)
        kelas = cursor.fetchone()

        # Ambil data jadwal menurut kelas yang dipilih
        sql = "SELECT j.jam, DATE_ADD(j.jam, interval 45 minute), j.mapel, p.namamapel, g.nama FROM jadwal j LEFT JOIN guru g ON j.pengajar = g.nuptk LEFT JOIN mapel p ON j.mapel = p.kodemapel WHERE j.kelas = %s AND j.hari = %s ORDER BY j.jam"
        detail=(kode, hari)
        cursor.execute(sql, detail)
        jadwal = cursor.fetchall()

        # Ambil daftar hari belajar
        sql = "SELECT * FROM haribelajar ORDER BY hari DESC"
        cursor.execute(sql)
        listHari = cursor.fetchall()

        # Jika jadwal kelas tersebut kosong
        if not jadwal:
            jadwal = False;

        # Jika jadwal kelas tersebut sudah penuh
        if len(jadwal) >= 8:
            tambah = False
        closeDb()
        return render_template('admin/detail_jadwal.html', kode=kode, hari=hari, kelas=kelas, jadwal=jadwal, listHari=listHari, status=Stat, tambah=tambah)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/tambah_jadwal', methods = ['GET', 'POST'])
def tambahjadwal():
    if verifLogin(1):
        openDb()
        global Stat
        # Ambil daftar kelas
        sql = "SELECT kelas, namakelas FROM kelas ORDER BY namakelas DESC"
        cursor.execute(sql)
        kls = cursor.fetchall()

        # Ambil daftar hari belajar
        sql = "SELECT * FROM haribelajar ORDER BY hari DESC"
        cursor.execute(sql)
        days = cursor.fetchall()

        if request.method == 'POST':
            try:
                Stat = True
                kode = request.form.get('kelas')
                hari = request.form.get('hari')
                # Cek juga jika jadwal yang ingin ditambah sudah penuh
                sql = "SELECT j.jam, DATE_ADD(j.jam, interval 45 minute), j.mapel, p.namamapel, g.nama FROM jadwal j LEFT JOIN guru g ON j.pengajar = g.nuptk LEFT JOIN mapel p ON j.mapel = p.kodemapel WHERE j.kelas = %s AND j.hari = %s ORDER BY j.jam"
                detail = (kode, hari)
                cursor.execute(sql, detail)
                jadwal = cursor.fetchall()
                if len(jadwal) >= 8:
                    Stat = False
                    flash('Jadwal kelas ini sudah penuh dan tidak bisa ditambah')
                    return redirect(url_for('jadwal', kode=kode, hari=hari))
                return redirect(url_for('addjadwal', kode=kode, hari=hari))
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('tambahjadwal'))
        return render_template('admin/tambah_jadwal.html', kls=kls, days=days)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/jadwal_baru/<kode>/<hari>', methods = ['GET', 'POST'])
def addjadwal(kode, hari):
    if verifLogin(1):
        openDb()
        global Stat
        # Ambil detail kelas jadwal yang akan ditambah
        sql = "SELECT kelas, namakelas FROM kelas WHERE kelas = %s"
        cursor.execute(sql, kode)
        kls = cursor.fetchone()

        # Ambil daftar jam belajar dari jadwal kelas bersangkutan yang belum ada mapelnya
        sql = "SELECT j.jam, DATE_ADD(j.jam, interval 45 minute) FROM jambelajar j WHERE NOT EXISTS (SELECT w.jam FROM jadwal w WHERE j.jam = w.jam AND kelas = %s AND hari = %s)"
        a = (kode, hari)
        cursor.execute(sql, a)
        jam = cursor.fetchall()

        # Ambil daftar mapel
        sql = "SELECT kodemapel, namamapel FROM mapel ORDER BY namamapel"
        cursor.execute(sql)
        mapel = cursor.fetchall()

        # Ambil daftar guru pengajar biasa yang bukan staf admin/perpus
        sql = "SELECT g.nuptk, g.nama FROM guru g LEFT JOIN user u ON g.nuptk = u.userid WHERE u.access = 2"
        cursor.execute(sql)
        guru = cursor.fetchall()

        if request.method == 'POST':
            try:
                jm = request.form.get('jam')
                mp = request.form.get('mapel')
                gr = request.form.get('guru')
                jdwl = (kode, hari, jm, mp, gr)
                sql = "INSERT INTO jadwal VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, jdwl)
                conn.commit()
                Stat = True
                flash('Jadwal berhasil ditambahkan')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return (redirect(url_for('jadwal', kode=kode, hari=hari)))
        return render_template('admin/jadwal_baru.html', kelas=kls, hari=hari, jam=jam, mapel=mapel, guru=guru)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/edit_jadwal/<kode>/<hari>/<jam>', methods = ['GET', 'POST'])
def editjadwal(kode, hari, jam):
    if verifLogin(1):
        openDb()
        global Stat
        # Ambil detail kelas jadwal yang akan diedit
        sql = "SELECT kelas, namakelas FROM kelas WHERE kelas = %s"
        cursor.execute(sql, kode)
        kls = cursor.fetchone()

        # Ambil detail jam berdasarkan jadwal yang akan diedit
        sql = "SELECT jam, DATE_ADD(jam, interval 45 minute) FROM jambelajar WHERE jam = %s"
        cursor.execute(sql, jam)
        infojam = cursor.fetchone()

        # Ambil detail jadwal yang akan diedit
        sql = "SELECT kelas, hari, jam, mapel, pengajar FROM jadwal WHERE kelas = %s AND hari = %s AND jam = %s"
        detail = (kode, hari, jam)
        cursor.execute(sql, detail)
        jdw = cursor.fetchone()

        # Ambil daftar mapel
        sql = "SELECT kodemapel, namamapel FROM mapel ORDER BY namamapel"
        cursor.execute(sql)
        listmapel = cursor.fetchall()

        # Ambil daftar guru pengajar biasa yang bukan staf admin/perpus
        sql = "SELECT g.nuptk, g.nama FROM guru g LEFT JOIN user u ON g.nuptk = u.userid WHERE u.access = 2"
        cursor.execute(sql)
        listguru = cursor.fetchall()

        if request.method == 'POST':
            try:
                mp = request.form.get('mapel')
                gr = request.form.get('guru')
                jdwl = (mp, gr, jam, kode, hari)
                sql = "UPDATE jadwal SET mapel = %s, pengajar = %s WHERE jam = %s AND kelas = %s AND hari = %s"
                cursor.execute(sql, jdwl)
                conn.commit()
                Stat = True
                flash('Jadwal berhasil diubah')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return (redirect(url_for('jadwal', kode=kode, hari=hari)))
        return render_template('admin/edit_jadwal.html', data=jdw, kelas=kls, hari=hari, listmapel=listmapel, listguru=listguru, jam=infojam)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/hapus_jadwal/<kode>/<hari>/<jam>', methods = ['GET', 'POST'])
def hapusjadwal(kode, hari, jam):
    if verifLogin(1):
        openDb()
        global Stat
        # Ambil detail kelas jadwal yang akan dihapus
        sql = "SELECT kelas, namakelas FROM kelas WHERE kelas = %s"
        cursor.execute(sql, kode)
        kls = cursor.fetchone()

        # Ambil detail jadwal yang akan dihapus
        sql = "SELECT j.kelas, j.hari, j.jam, DATE_ADD(j.jam, interval 45 minute), p.namamapel, g.nama FROM jadwal j LEFT JOIN mapel p ON j.mapel = p.kodemapel LEFT JOIN guru g ON j.pengajar = g.nuptk WHERE j.kelas = %s AND j.hari = %s AND j.jam = %s"
        detail = (kode, hari, jam)
        cursor.execute(sql, detail)
        jdw = cursor.fetchone()

        if request.method == 'POST':
            try:
                jdwl = (jam, kode, hari)
                sql = "DELETE FROM jadwal WHERE jam = %s AND kelas = %s AND hari = %s"
                cursor.execute(sql, jdwl)
                conn.commit()
                Stat = True
                flash('Jadwal berhasil dihapus')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return (redirect(url_for('jadwal', kode=kode, hari=hari)))
        return render_template('admin/hapus_jadwal.html', data=jdw, kelas=kls)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_mapel', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_admin/data_mapel/<int:page>', methods = ['GET', 'POST'])
def datamapel(page):
    if verifLogin(1):
        openDb()
        global Stat, lanjut
        pencarian = ""
        prev = page - 1
        next = page + 1
        counter = prev*10
        # Ambil daftar mapel dari database
        sql = "SELECT * FROM mapel ORDER BY namamapel"
        cursor.execute(sql)
        mapelAll = cursor.fetchall()
        # Slice data yang akan ditampilkan sebanyak 10 baris
        mapel = mapelAll[counter:page * 10]
        # Data slice halaman selanjutnya
        nextPage = mapelAll[page * 10:next * 10]
        # Jika halaman selanjutnya kosong
        if not nextPage:
            lanjut = False
        if request.method == 'POST':
            # Jika user melakukan searching
            if request.form['search']:
                # Searching dengan nama atau kode mapel
                try:
                    pencarian = request.form['search']
                    sql = "SELECT * FROM mapel WHERE kodemapel LIKE '%" + \
                          request.form['search'] + "%' OR namamapel LIKE '%" + request.form[
                              'search'] + "%' ORDER BY namamapel"
                    cursor.execute(sql)
                    mapel = cursor.fetchall()
                    lanjut = False
                except Exception as err:
                    Stat = False
                    flash('Terjadi kesalahan')
                    flash(err)
        # Jika databasenya kosong
        if not mapel:
            mapel = False
        closeDb()
        return render_template('admin/data_mapel.html', count=counter, mapel=mapel, prev=prev, next=next, lanjut=lanjut, status=Stat, pencarian=pencarian)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/edit_mapel/<kode>', methods = ['GET', 'POST'])
def editmapel(kode):
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat
        cursor.execute('SELECT * FROM mapel WHERE kodemapel = %s', (kode))
        mapel = cursor.fetchone()

        # Jika user menekan tombol submit, maka mengumpulkan semua data yang ada di form
        if request.method == 'POST':
            try:
                nKode = request.form['kodemapel']
                nama = request.form['namamapel']
                detail = (nKode, nama, kode)
                print(detail)
                cursor.execute('UPDATE mapel SET kodemapel = %s, namamapel = %s WHERE kodemapel = %s', detail)
                conn.commit()
                Stat = True
                flash('Data berhasil diubah')
                closeDb()
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('datamapel'))
        closeDb()
        return render_template('admin/edit_mapel.html', data=mapel)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/hapus_mapel/<kode>', methods = {'GET', 'POST'})
def hapusmapel(kode):
    if verifLogin(1):
        openDb()
        global Stat
        cursor.execute('SELECT * FROM mapel WHERE kodemapel = %s', (kode))
        mapel = cursor.fetchone()

        # Jika user mengkonfirm hapusdata
        if request.method == 'POST':
            try:
                cursor.execute('DELETE FROM mapel WHERE kodemapel = %s', (kode))
                conn.commit()
                Stat = True
                flash('Data berhasil dihapus')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('datamapel'))
        closeDb()
        return render_template('admin/hapus_mapel.html', data=mapel)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/tambah_mapel', methods = ['GET', 'POST'])
def tambahmapel():
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat
        if request.method == 'POST':
            try:
                kodemapel = request.form['kodemapel']
                namamapel = request.form['namamapel']
                detail = (kodemapel, namamapel)
                cursor.execute('INSERT INTO mapel VALUES (%s, %s)', detail)
                conn.commit()
                Stat = True
                flash('Data berhasil ditambahkan')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('datamapel'))
        return render_template('admin/tambah_mapel.html')
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_staf', methods = ['GET', 'POST'])
def datastaf():
    if verifLogin(1):
        openDb()
        # Ambil daftar staf dari database, left join dengan nama hak akses & nama guru
        sql = "SELECT u.userid, g.nama, u.email, h.accessname FROM user u LEFT JOIN hakakses h ON u.access = h.accessid LEFT JOIN guru g ON u.userid = g.nuptk WHERE u.username NOT IN('admin') AND u.access = 1 OR u.access = 4"
        cursor.execute(sql)
        staf = cursor.fetchall()
        # Jika data staf kosong
        if not staf:
            staf = False
        return render_template('admin/data_staf.html', staf=staf, status=Stat)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/edit_staf/<id>', methods = ['GET', 'POST'])
def editstaf(id):
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat

        # Ambil data yang akan diedit
        cursor.execute('SELECT u.userid, g.nama, u.email FROM user u LEFT JOIN hakakses h ON u.access = h.accessid LEFT JOIN guru g ON u.userid = g.nuptk WHERE u.userid = %s', (id))
        data = cursor.fetchone()

        # Ambil list hak akses untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT accessname FROM hakakses WHERE accessid = 1 OR accessid = 4')
        role = cursor.fetchall()

        # Konfirm edit staf
        if request.method == 'POST':
            try:
                nuptk = request.form['nuptk']
                peran = request.form['role']
                # Cek id hak akses berdasarkan yang dipilih di form
                cursor.execute('SELECT accessid FROM hakakses WHERE accessname = %s', peran)
                rl = cursor.fetchone()
                info = (rl[0], nuptk)
                # Update data user dengan role staf yang dipilih
                cursor.execute('UPDATE user SET access = %s WHERE userid = %s', info)
                conn.commit()
                Stat = True
                flash('Data berhasil diubah')
                closeDb()
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('datastaf'))
        closeDb()
        return render_template('admin/edit_staf.html', data=data, role=role)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/hapus_staf/<id>', methods = ['GET', 'POST'])
def hapusstaf(id):
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat
        # Ambil data dari staf yang dipilih untuk dihapus
        cursor.execute('SELECT u.userid, g.nama, u.email, h.accessname FROM user u LEFT JOIN hakakses h ON u.access = h.accessid LEFT JOIN guru g ON u.userid = g.nuptk WHERE u.userid = %s',(id))
        data = cursor.fetchone()

        # Jika user mengkonfirm hapusdata
        if request.method == 'POST':
            try:
                # Di hapus dari staf, artinya hak akses dikembalikan menjadi guru biasa
                temp = (2, id)
                cursor.execute('UPDATE user SET access = %s WHERE userid = %s', temp)
                conn.commit()
                Stat = True
                flash('Data berhasil dihapus dari staf')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('datastaf'))
        closeDb()
        return render_template('admin/hapus_staf.html', data=data)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/tambah_staf', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_admin/tambah_staf/<int:page>', methods = ['GET', 'POST'])
def tambahstaf(page):
    if verifLogin(1):
        openDb()
        global Stat, lanjut
        pencarian = ""
        prev = page - 1
        next = page + 1
        counter = prev * 10
        # Ambil daftar guru dari database yang bukan staf admin/perpus
        sql = "SELECT u.userid, g.nama, g.email FROM user u LEFT JOIN guru g ON u.userid = g.nuptk WHERE u.access = 2 ORDER BY nama"
        cursor.execute(sql)
        stafAll = cursor.fetchall()
        # Slice data yang akan ditampilkan sebanyak 10 baris
        staf = stafAll[counter:page * 10]
        # Data slice halaman selanjutnya
        nextPage = stafAll[page * 10:next * 10]
        # Jika halaman selanjutnya kosong
        if not nextPage:
            lanjut = False
        if request.method == 'POST':
            # Jika user melakukan searching
            if request.form['search']:
                # Searching dengan mencocokkan nama guru
                try:
                    pencarian = request.form['search']
                    sql = "SELECT u.userid, g.nama, g.email FROM user u LEFT JOIN guru g ON u.userid = g.nuptk WHERE u.access = 2 AND g.nama LIKE '%" + request.form[
                    'search'] + "%' ORDER BY nama"
                    cursor.execute(sql)
                    staf = cursor.fetchall()
                    lanjut = False
                except Exception as err:
                    Stat = False
                    flash('Terjadi kesalahan')
                    flash(err)
        # Jika databasenya kosong
        if not staf:
            staf = False
        closeDb()
        return render_template('admin/tambah_staf.html', count=counter, staf=staf, prev=prev, next=next, lanjut=lanjut, status=Stat, pencarian=pencarian)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/konfirm_staf/<id>', methods = ['GET', 'POST'])
def addStaf(id):
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat
        # Ambil list hak akses untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT accessname FROM hakakses WHERE accessid = 1 OR accessid = 4')
        role = cursor.fetchall()

        # Ambil data yang akan ditambahkan
        cursor.execute(
            'SELECT u.userid, g.nama, u.email FROM user u LEFT JOIN hakakses h ON u.access = h.accessid LEFT JOIN guru g ON u.userid = g.nuptk WHERE u.userid = %s',
            (id))
        data = cursor.fetchone()

        if request.method == 'POST':
            try:
                nuptk = id
                namarole = request.form.get('role')
                cursor.execute('SELECT accessid FROM hakakses WHERE accessname = %s', namarole)
                rol = cursor.fetchone()
                info = (rol[0], nuptk)
                # Update data user dengan role staf yang dipilih
                cursor.execute('UPDATE user SET access = %s WHERE userid = %s', info)
                conn.commit()
                Stat = True
                flash('Data berhasil ditambahkan')
                closeDb()
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('datastaf'))

        return render_template('admin/konfirm_staf.html', data=data, role=role)
    else:
        return redirect(url_for('index'))


''' Akses Guru '''
@app.route('/dashboard_guru', methods = ['GET', 'POST'])
def guru():
    if verifLogin(2):
        openDb()
        # Fetch hari & tanggal saat ini
        tanggal = date.today()
        d = tanggal.strftime("%d")
        m = cekBulan(tanggal.month)
        y = tanggal.strftime("%Y")
        # dt = tanggal
        dt = d + " " + m + " " + y
        dow = tanggal.isoweekday()
        # numHari = hari
        numHari = cekHari(dow)
        return render_template('guru/dashboard_guru.html', hari=numHari, tanggal=dt)
    else:
        return redirect(url_for('index'))


''' Akses Siswa '''
@app.route('/dashboard_siswa', methods = ['GET', 'POST'])
def siswa():
    if verifLogin(3):
        openDb()
        # Fetch hari & tanggal saat ini
        tanggal = date.today()
        d = tanggal.strftime("%d")
        m = cekBulan(tanggal.month)
        y = tanggal.strftime("%Y")
        # dt = tanggal
        dt = d + " " + m + " " + y
        dow = tanggal.isoweekday()
        # numHari = hari
        numHari = cekHari(dow)

        # Fetch kelas dari siswa yang login
        sql = "SELECT r.kelas, k.namakelas from rombel r LEFT JOIN kelas k ON r.kelas = k.kelas WHERE r.anggota = %s"
        cursor.execute(sql, session['id'])
        kls = cursor.fetchone()

        # Fetch data jadwal hari ini
        sql = "SELECT j.jam, DATE_ADD(j.jam, interval 45 minute), j.mapel, p.namamapel, g.nama FROM jadwal j LEFT JOIN guru g ON j.pengajar = g.nuptk LEFT JOIN mapel p ON j.mapel = p.kodemapel WHERE j.kelas = %s AND j.hari = %s ORDER BY j.jam"
        temp = (kls[0], numHari)
        cursor.execute(sql, temp)
        jadwal = cursor.fetchall()

        # Jika jadwal kelas tersebut kosong
        if not jadwal:
            jadwal = False;
        return render_template('siswa/dashboard_siswa.html', hari=numHari, tanggal=dt, jadwal=jadwal, kelas=kls)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_siswa/jadwal/<kelas>/<hari>', methods = ['GET','POST'])
def jadwalSiswa(kelas, hari):
    if verifLogin(3):
        openDb()
        global Stat
        tambah = True
        # Ambil nama kelas dari kode kelas
        sql = "SELECT kelas, namakelas FROM kelas WHERE kelas = %s"
        cursor.execute(sql, kelas)
        kls = cursor.fetchone()

        # Ambil data jadwal menurut kelas yang dipilih
        sql = "SELECT j.jam, DATE_ADD(j.jam, interval 45 minute), j.mapel, p.namamapel, g.nama FROM jadwal j LEFT JOIN guru g ON j.pengajar = g.nuptk LEFT JOIN mapel p ON j.mapel = p.kodemapel WHERE j.kelas = %s AND j.hari = %s ORDER BY j.jam"
        detail=(kelas, hari)
        cursor.execute(sql, detail)
        jadwal = cursor.fetchall()

        # Ambil daftar hari belajar
        sql = "SELECT * FROM haribelajar ORDER BY hari DESC"
        cursor.execute(sql)
        listHari = cursor.fetchall()

        # Jika jadwal kelas tersebut kosong
        if not jadwal:
            jadwal = False;

        closeDb()
        return render_template('siswa/jadwal_siswa.html', kls=kls, hari=hari, jadwal=jadwal, listHari=listHari)
    else:
        return redirect(url_for('index'))


''' Akses Perpustakaan '''
@app.route('/dashboard_perpus', methods = ['GET', 'POST'])
def perpus():
    if verifLogin(4):
        openDb()
        # Fetch hari & tanggal saat ini
        tanggal = date.today()
        d = tanggal.strftime("%d")
        m = cekBulan(tanggal.month)
        y = tanggal.strftime("%Y")
        # dt = tanggal
        dt = d + " " + m + " " + y
        dow = tanggal.isoweekday()
        # numHari = hari
        numHari = cekHari(dow)

        # Fetch jumlah buku
        sql = "SELECT COUNT(*) FROM databuku"
        cursor.execute(sql)
        res = cursor.fetchone()
        numBuku = res[0]

        # Fetch jumlah total peminjaman
        sql = "SELECT COUNT(*) FROM peminjamanbuku"
        cursor.execute(sql)
        res = cursor.fetchone()
        totPeminjaman = res[0]

        # Fetch jumlah buku yang sedang dipinjam
        sql = "SELECT COUNT(*) FROM peminjamanbuku WHERE statuspinjam = 'Dipinjam'"
        cursor.execute(sql)
        res = cursor.fetchone()
        ongoingPeminjaman = res[0]
        closeDb()
        return render_template('perpus/dashboard_perpus.html', hari=numHari, tanggal=dt, buku=numBuku, total=totPeminjaman, pinjam=ongoingPeminjaman)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_perpus/buku', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_perpus/buku/<int:page>', methods = ['GET', 'POST'])
def buku(page):
    if verifLogin(4):
        openDb()
        global lanjut, Stat
        pencarian = ""
        prev = page - 1
        next = page + 1
        counter = prev*10
        # Ambil daftar buku dari database
        sql = "SELECT isbn, namabuku, namapenulis, namapenerbit, tahunterbit FROM databuku ORDER BY namabuku"
        cursor.execute(sql)
        bukuAll = cursor.fetchall()
        # Slice data yang akan ditampilkan sebanyak 10 baris
        buku = bukuAll[counter:page*10]
        # Data slice halaman selanjutnya
        nextPage = bukuAll[page*10:next*10]
        # Jika halaman selanjutnya kosong
        if not nextPage:
            lanjut = False
        if request.method == 'POST':
            # Jika user melakukan searching
            if request.form['search']:
                # Searching dengan mencocokkan nama buku
                try:
                    pencarian = request.form['search']
                    sql = "SELECT isbn, namabuku, namapenulis, namapenerbit, tahunterbit FROM databuku WHERE isbn LIKE '%" + request.form['search'] + "%' OR namabuku LIKE '%" + request.form['search'] + "%' OR namapenulis LIKE '%" + request.form['search'] + "%' OR namapenerbit LIKE '%" + request.form['search'] + "%' OR tahunterbit LIKE '%" + request.form['search'] + "%' ORDER BY namabuku"
                    cursor.execute(sql)
                    buku = cursor.fetchall()
                    lanjut = False
                except Exception as err:
                    Stat = False
                    flash('Terjadi kesalahan')
                    flash(err)
        # Jika databasenya kosong
        if not buku:
            buku = False
        closeDb()
        return render_template('perpus/data_buku.html', count=counter, buku=buku, prev=prev, next=next, lanjut=lanjut, status=Stat, pencarian=pencarian)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_perpus/edit_buku/<id>', methods = ['GET', 'POST'])
def editbuku(id):
    if verifLogin(4):
        openDb()
        # Status berhasil & error
        global Stat
        # Ambil data buku yang akan diedit
        sql = "SELECT isbn, namabuku, namapenulis, namapenerbit, tahunterbit FROM databuku WHERE isbn = %s"
        cursor.execute(sql, id)
        data = cursor.fetchone()
        # Jika user menekan tombol submit, maka mengumpulkan semua data yang ada di form untuk diedit
        if request.method == 'POST':
            try:
                isbn = request.form['isbn']
                judul = request.form['judul']
                penulis = request.form['penulis']
                penerbit = request.form['penerbit']
                tahun = request.form['tahunterbit']
                detail = (isbn, judul, penulis, penerbit, tahun, id)
                # Update data buku
                cursor.execute(
                    'UPDATE databuku SET isbn = %s, namabuku = %s, namapenulis = %s, namapenerbit = %s, tahunterbit = %s WHERE isbn = %s',
                    detail)
                conn.commit()
                Stat = True
                flash('Data berhasil diubah')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('buku'))
        closeDb()
        return render_template('perpus/edit_buku.html', data=data)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_perpus/hapus_buku/<id>', methods = ['GET', 'POST'])
def hapusbuku(id):
    if verifLogin(4):
        openDb()
        global Stat
        # Ambil data buku yang akan dihapus
        cursor.execute('SELECT isbn, namabuku, namapenulis, namapenerbit, tahunterbit FROM databuku WHERE isbn = %s', (id))
        data = cursor.fetchone()
        # Jika user mengkonfirm hapusdata
        if request.method == 'POST':
            try:
                cursor.execute('DELETE FROM databuku WHERE isbn = %s', (id))
                conn.commit()
                Stat = True
                flash('Data berhasil dihapus')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('buku'))
        closeDb()
        return render_template('perpus/hapus_buku.html', data=data)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_perpus/tambah_buku', methods = ['GET', 'POST'])
def tambahbuku():
    if verifLogin(4):
        openDb()
        # Status berhasil & error
        global Stat
        # Jika user mengkonfirm tambah data buku
        if request.method == 'POST':
            try:
                isbn = request.form['isbn']
                judul = request.form['judulbuku']
                penulis = request.form['penulis']
                penerbit = request.form['penerbit']
                tahun = request.form['tahunterbit']
                detail = (isbn, judul, penulis, penerbit, tahun)
                cursor.execute('INSERT INTO databuku VALUES (%s, %s, %s, %s, %s)', detail)
                conn.commit()
                Stat = True
                flash('Data berhasil ditambahkan')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('buku'))
        closeDb()
        return render_template('perpus/tambah_buku.html')
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_perpus/peminjaman/<status>', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_perpus/peminjaman/<status>/<int:page>', methods = ['GET', 'POST'])
def peminjaman(status, page):
    if verifLogin(4):
        openDb()
        global lanjut, Stat
        pencarian = ""
        prev = page - 1
        next = page + 1
        counter = prev*10
        # Ambil daftar peminjaman dari database
        sql = "SELECT p.idpeminjaman, s.nama, k.namakelas, b.namabuku, p.tanggalpinjam, p.statuspinjam, p.tanggalpengembalian FROM peminjamanbuku p LEFT JOIN kelas k ON p.kelas = k.kelas LEFT JOIN databuku b ON p.nomorbuku = b.isbn LEFT JOIN siswa s ON p.peminjam = s.nis ORDER BY p.idpeminjaman"
        cursor.execute(sql)
        peminjamanAll = cursor.fetchall()
        # Slice data yang akan ditampilkan sebanyak 10 baris
        peminjaman = peminjamanAll[counter:page*10]
        # Data slice halaman selanjutnya
        nextPage = peminjamanAll[page*10:next*10]
        # Jika halaman selanjutnya kosong
        if not nextPage:
            lanjut = False
        if request.method == 'POST':
            # Jika user melakukan searching
            if request.form['search']:
                try:
                    pencarian = request.form['search']
                    sql = "SELECT p.idpeminjaman, s.nama, k.namakelas, b.namabuku, p.tanggalpinjam, p.statuspinjam, p.tanggalpengembalian FROM peminjamanbuku p LEFT JOIN kelas k ON p.kelas = k.kelas LEFT JOIN databuku b ON p.nomorbuku = b.isbn LEFT JOIN siswa s ON p.peminjam = s.nis WHERE s.nama LIKE '%" + request.form['search'] + "%' OR k.namakelas LIKE '%" + request.form['search'] + "%' OR b.namabuku LIKE '%" + request.form['search'] + "%' OR p.statuspinjam LIKE '%" + request.form['search'] + "%' OR p.tanggalpinjam LIKE '%" + request.form['search'] + "%' ORDER BY p.idpeminjaman"
                    cursor.execute(sql)
                    peminjaman = cursor.fetchall()
                    lanjut = False
                except Exception as err:
                    Stat = False
                    flash('Terjadi kesalahan')
                    flash(err)
        # Jika databasenya kosong
        if not peminjaman:
            peminjaman = False
        closeDb()
        return render_template('perpus/data_peminjaman.html', count=counter, peminjama=peminjaman, prev=prev, next=next, lanjut=lanjut, status=Stat, pencarian=pencarian)
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)