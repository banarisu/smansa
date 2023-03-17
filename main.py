# File utama program ini
from flask import Flask, flash, session, render_template,\
    request, redirect, url_for
from flask_session import Session
import pymysql.cursors

app = Flask(__name__)
app.secret_key = "Smansa"

#Session disimpan pada sistem dan tidak permanen
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = cursor = None

# Deklarasi variabel global untuk diakses beberapa function
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


#Akses Dashboard Admin
@app.route('/dashboard_admin', methods = ['GET', 'POST'])
def admin():
    if verifLogin(1):
        return render_template('admin/dashboard_admin.html')
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

        #Cek jika halaman selanjutnya masih ada data atau tidak
        sql2 = "SELECT * FROM guru limit " + str(firstPage) + ", " + str(perPage)
        cursor.execute(sql2)
        lanjut = cursor.fetchall()

        if request.method == 'POST':
            # Jika user melakukan searching
            if request.form['search']:
                sql = "SELECT * FROM guru WHERE nama LIKE '%" + request.form['search'] + "%' ORDER BY nama limit " + str(fp) + ", " + str(perPage)
                cursor.execute(sql)
                guru = cursor.fetchall()
                lanjut=False
            elif request.form['edit']:
                print(request.form['edit'])

        # Jika databasenya kosong
        if not guru:
            guru = False

        # Jika halaman selanjutnya kosong
        if not lanjut:
            lanjut = False

        return render_template('admin/data_guru.html', count=fp, guru=guru, prev=prev, next=next, lanjut=lanjut, status=Stat)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/edit_guru/<id>', methods = ['GET', 'POST'])
def editguru(id):
    if verifLogin(1):
        openDb()
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
                #Padahal try nya berhasil, tapi di db ga kehapus njir
            except Exception as err:
                Stat = False
                flash('Terjadi kesalahan')
                flash(err)
            closeDb()
            return redirect(url_for('dataguru'))
        return render_template('admin/hapus_guru.html', data=data, gend=gend)
    else:
        return redirect(url_for('index'))
@app.route('/dashboard_admin/tambah_guru', methods = ['GET', 'POST'])
def tambahguru():
    if verifLogin(1):

        return render_template('admin/tambah_guru.html')
    else:
        return redirect(url_for('index'))


@app.route('/dashboard_admin/data_siswa', methods = ['GET', 'POST'])
def datasiswa():
    if verifLogin(1):
        return render_template('admin/data_siswa.html')
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/tambah_siswa', methods = ['GET', 'POST'])
def tambahsiswa():
    if verifLogin(1):
        return render_template('admin/tambah_siswa.html')
    else:
        return redirect(url_for('index'))

@app.route('/dashboard_admin/data_kelas', methods = ['GET', 'POST'])
def datakelas():
    if verifLogin(1):
        return render_template('admin/data_kelas.html')
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


#Akses Dashboard Guru
@app.route('/dashboard_guru', methods = ['GET', 'POST'])
def guru():
    if verifLogin(2):
        return render_template('guru/dashboard_guru.html')
    else:
        return redirect(url_for('index'))

#Akses Siswa
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