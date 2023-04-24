# File utama program ini
from flask import Flask, flash, session, render_template,\
    request, redirect, url_for
from flask_session import Session
from datetime import datetime, date
import pymysql.cursors

app = Flask(__name__)
app.secret_key = "Smansa"

#Session disimpan pada sistem dan tidak permanen
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = cursor = None

# Deklarasi variabel global status berhasil/error untuk diakses beberapa fungsi
Stat = True
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
    if dow == 1:
        hari="Senin"
    elif dow == 2:
        hari="Selasa"
    elif dow == 3:
        hari="Rabu"
    elif dow == 4:
        hari="Kamis"
    elif dow == 5:
        hari="Jumat"
    elif dow == 6:
        hari="Sabtu"
    elif dow == 7:
        hari="Minggu"
    return hari;

#Penamaan bulan berdasarkan angka
def cekBulan(mm):
    if mm == 1:
        month="Januari"
    elif mm == 2:
        month="Februari"
    elif mm == 3:
        month="Maret"
    elif mm == 4:
        month="April"
    elif mm == 5:
        month="Mei"
    elif mm == 6:
        month="Juni"
    elif mm == 7:
        month="Juli"
    elif mm == 8:
        month="Agustus"
    elif mm == 9:
        month="September"
    elif mm == 10:
        month="Oktober"
    elif mm == 11:
        month="November"
    elif mm == 12:
        month="Desember"
    return month;

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
        dt = d + " " + m + " " + y
        dow = tanggal.isoweekday()
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

        # Fetch jumlah mapel
        sql = "SELECT COUNT(*) FROM mapel"
        cursor.execute(sql)
        res = cursor.fetchone()
        numMapel = res[0]

        closeDb()
        return render_template('admin/dashboard_admin.html', guru=numGuru, siswa=numSiswa, hari=numHari, tanggal=dt, kelas=numKelas, mapel=numMapel)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_guru', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_admin/data_guru/<int:page>', methods = ['GET', 'POST'])
def dataguru(page):
    if verifLogin(1):
        openDb()
        perPage = 10
        prev = page-1
        next = page+1
        firstPage = page*perPage
        fp = firstPage-10
        #Ambil daftar guru dari database
        sql = "SELECT * FROM guru ORDER BY nama limit "+str(fp)+", "+str(perPage)
        cursor.execute(sql)
        guru = cursor.fetchall()

        #Ambil data halaman selanjutnya
        sql2 = "SELECT * FROM guru ORDER BY nama limit " + str(firstPage) + ", " + str(perPage)
        cursor.execute(sql2)
        lanjut = cursor.fetchall()

        if request.method == 'POST':
            # Jika user melakukan searching
            if request.form['search']:
                # Searching dengan mencocokkan nama guru
                sql = "SELECT * FROM guru WHERE nama LIKE '%" + request.form['search'] + "%' ORDER BY nama limit " + str(fp) + ", " + str(perPage)
                cursor.execute(sql)
                guru = cursor.fetchall()
                lanjut=False

        # Jika databasenya kosong
        if not guru:
            guru = False

        # Jika halaman selanjutnya kosong
        if not lanjut:
            lanjut = False
        closeDb()
        return render_template('admin/data_guru.html', count=fp, guru=guru, prev=prev, next=next, lanjut=lanjut, status=Stat)
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
                jk = request.form['gender']
                agama = request.form['aga']
                email = request.form['email']
                telp = request.form['tel']
                detail = (nama, jk, agama, email, telp, nuptk)
                cursor.execute(
                    'UPDATE guru SET nama = %s, jeniskelamin = %s, agama = %s, email = %s, telepon = %s WHERE nuptk = %s',
                    detail)
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
                cursor.execute('DELETE FROM guru WHERE nuptk = %s', (id))
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

        return render_template('admin/tambah_guru.html')
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_siswa', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_admin/data_siswa/<int:page>', methods = ['GET', 'POST'])
def datasiswa(page):
    if verifLogin(1):
        openDb()
        perPage = 10
        prev = page - 1
        next = page + 1
        firstPage = page * perPage
        fp = firstPage - 10
        # Ambil daftar siswa dari database
        sql = "SELECT * FROM siswa ORDER BY nama limit " + str(fp) + ", " + str(perPage)
        cursor.execute(sql)
        siswa = cursor.fetchall()

        # Cek jika halaman selanjutnya masih ada data atau tidak
        sql2 = "SELECT * FROM siswa limit " + str(firstPage) + ", " + str(perPage)
        cursor.execute(sql2)
        lanjut = cursor.fetchall()

        if request.method == 'POST':
            # Jika user melakukan searching
            if request.form['search']:
                sql = "SELECT * FROM siswa WHERE nama LIKE '%" + request.form[
                    'search'] + "%' ORDER BY nama limit " + str(fp) + ", " + str(perPage)
                cursor.execute(sql)
                siswa = cursor.fetchall()
                lanjut = False

        # Jika databasenya kosong
        if not siswa:
            siswa = False

        # Jika halaman selanjutnya kosong
        if not lanjut:
            lanjut = False
        return render_template('admin/data_siswa.html', count=fp, siswa=siswa, prev=prev, next=next, lanjut=lanjut, status=Stat)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/edit_siswa/<id>', methods = ['GET', 'POST'])
def editsiswa(id):
    if verifLogin(1):
        openDb()
        # Status berhasil & error
        global Stat
        cursor.execute('SELECT * FROM siswa WHERE nis = %s', (id))
        data = cursor.fetchone()

        # Ambil list agama untuk ditampilkan pada pilihan dropdown
        cursor.execute('SELECT * FROM agama')
        agam = cursor.fetchall()

        # Jika user menekan tombol submit, maka mengumpulkan semua data yang ada di form
        if request.method == 'POST':
            try:
                nis = request.form['nis']
                nama = request.form['nama']
                jk = request.form['gender']
                agama = request.form['aga']
                email = request.form['email']
                telp = request.form['tel']
                detail = (nama, jk, agama, email, telp, nis)
                cursor.execute(
                    'UPDATE siswa SET nama = %s, jeniskelamin = %s, agama = %s, email = %s, telepon = %s WHERE nis = %s',
                    detail)
                conn.commit()
                Stat = True
                flash('Data berhasil diubah')
                closeDb()
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('datasiswa'))
        closeDb()
        return render_template('admin/edit_siswa.html', data=data, ag=agam, gend=gend)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/hapus_siswa/<id>', methods = ['GET', 'POST'])
def hapussiswa(id):
    if verifLogin(1):
        openDb()
        global Stat
        cursor.execute('SELECT * FROM siswa WHERE nis = %s', (id))
        data = cursor.fetchone()

        # Jika user mengkonfirm hapusdata
        if request.method == 'POST':
            try:
                cursor.execute('DELETE FROM siswa WHERE nis = %s', (id))
                conn.commit()
                Stat = True
                flash('Data berhasil dihapus')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('datasiswa'))
        closeDb()
        return render_template('admin/hapus_siswa.html', data=data, gend=gend)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/tambah_siswa', methods = ['GET', 'POST'])
def tambahsiswa():
    if verifLogin(1):
        return render_template('admin/tambah_siswa.html')
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_kelas', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_admin/data_kelas/<int:page>', methods = ['GET', 'POST'])
def datakelas(page):
    if verifLogin(1):
        openDb()
        perPage = 10
        prev = page - 1
        next = page + 1
        firstPage = page * perPage
        fp = firstPage - 10
        # Ambil daftar kelas dan nama wali kelas dari database
        sql = "SELECT k.kelas, k.namakelas, g.nama FROM kelas k LEFT JOIN guru g ON k.walikelas = g.nuptk ORDER BY k.kelas limit " + str(fp) + ", " + str(perPage)
        cursor.execute(sql)
        kelas = cursor.fetchall()

        # Ambil data halaman selanjutnya
        sql2 = "SELECT k.kelas, k.namakelas, g.nama FROM kelas k LEFT JOIN guru g ON k.walikelas = g.nuptk ORDER BY k.kelas limit " + str(
            firstPage) + ", " + str(perPage)
        cursor.execute(sql2)
        lanjut = cursor.fetchall()

        # Jika databasenya kosong
        if not kelas:
            kelas = False

        # Jika halaman selanjutnya kosong
        if not lanjut:
            lanjut = False

        closeDb()
        return render_template('admin/data_kelas.html', count=fp, kelas=kelas, prev=prev, next=next, lanjut=lanjut, status=Stat)
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
                closeDb()
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            return redirect(url_for('datakelas'))
        closeDb()
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
                Stat = True
                flash('Data berhasil dihapus')
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('datakelas'))
        closeDb()
        return render_template('admin/hapus_kelas.html', data=kelas)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/tambah_kelas', methods = ['GET', 'POST'])
def tambahkelas():
    if verifLogin(1):
        return render_template('admin/tambah_kelas.html')
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_jadwal', methods = ['GET', 'POST'])
def datajadwal():
    if verifLogin(1):
        return render_template('admin/data_jadwal.html')
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/tambah_jadwal', methods = ['GET', 'POST'])
def tambahjadwal():
    if verifLogin(1):
        return render_template('admin/tambah_jadwal.html')
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_mapel', methods = ['GET', 'POST'], defaults={'page':1})
@app.route('/dashboard_admin/data_mapel/<int:page>', methods = ['GET', 'POST'])
def datamapel(page):
    if verifLogin(1):
        openDb()
        perPage = 10
        prev = page - 1
        next = page + 1
        firstPage = page * perPage
        fp = firstPage - 10
        # Ambil daftar mapel dari database
        sql = "SELECT * FROM mapel ORDER BY namamapel limit " + str(fp) + ", " + str(perPage)
        cursor.execute(sql)
        mapel = cursor.fetchall()

        # Ambil data halaman selanjutnya
        sql2 = "SELECT * FROM mapel ORDER BY namamapel limit " + str(firstPage) + ", " + str(perPage)
        cursor.execute(sql2)
        lanjut = cursor.fetchall()

        if request.method == 'POST':
            # Jika user melakukan searching
            if request.form['search']:
                # Ambil data berdasarkan inputan dengan mencocokkan nama atau kode mapel
                sql = "SELECT * FROM mapel WHERE namamapel LIKE '%" + request.form['search'] + "%' OR kodemapel LIKE '%" + request.form['search'] + "%' ORDER BY namamapel limit " + str(fp) + ", " + str(perPage)
                cursor.execute(sql)
                mapel = cursor.fetchall()
                lanjut=False

        # Jika databasenya kosong
        if not mapel:
            mapel = False

        # Jika halaman selanjutnya kosong
        if not lanjut:
            lanjut = False
        closeDb()

        return render_template('admin/data_mapel.html', count=fp, mapel=mapel, prev=prev, next=next, lanjut=lanjut, status=Stat)
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
            closeDb()
            return redirect(url_for('datamapel'))
        closeDb()
        return render_template('admin/hapus_mapel.html', data=mapel)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/tambah_mapel', methods = ['GET', 'POST'])
def tambahmapel():
    if verifLogin(1):
        return render_template('admin/tambah_mapel.html')
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_staf', methods = ['GET', 'POST'])
def datastaf():
    if verifLogin(1):
        openDb()
        # Ambil daftar staf dari database, left join dengan nama hak akses
        sql = "SELECT u.userid, u.username, u.email, h.accessname FROM user u LEFT JOIN hakakses h ON u.access = h.accessid WHERE u.username NOT IN('admin') AND u.access = 1 OR u.access = 4"
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
        cursor.execute('SELECT u.userid, u.username, u.email, h.accessname FROM user u LEFT JOIN hakakses h ON u.access = h.accessid WHERE u.userid = %s', (id))
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
        cursor.execute('SELECT u.userid, u.username, u.email, h.accessname FROM user u LEFT JOIN hakakses h ON u.access = h.accessid WHERE u.userid = %s',(id))
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

@app.route('/dashboard_admin/tambah_staf', methods = ['GET', 'POST'])
def tambahStaf():
    if verifLogin(1):
        return render_template('admin/tambah_staf.html')
    else:
        return redirect(url_for('index'))



''' Akses Guru '''
@app.route('/dashboard_guru', methods = ['GET', 'POST'])
def guru():
    if verifLogin(2):
        return render_template('guru/dashboard_guru.html')
    else:
        return redirect(url_for('index'))

''' Akses Siswa '''
@app.route('/dashboard_siswa', methods = ['GET', 'POST'])
def siswa():
    if verifLogin(3):
        return render_template('siswa/dashboard_siswa.html')
    else:
        return redirect(url_for('index'))

#Akses Perpustakaan
@app.route('/dashboard_perpustakaan', methods = ['GET', 'POST'])
def perpus():
    if verifLogin(4):
        return render_template('perpus/dashboard_perpus.html')
    else:
        return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)