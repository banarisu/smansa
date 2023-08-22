-- phpMyAdmin SQL Dump
-- version 4.2.11
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Aug 22, 2023 at 03:25 PM
-- Server version: 5.6.21
-- PHP Version: 5.5.19

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `smansa`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE IF NOT EXISTS `admin` (
`idadmin` int(11) NOT NULL,
  `nama` varchar(50) NOT NULL,
  `jeniskelamin` enum('L','P') NOT NULL,
  `agama` varchar(15) NOT NULL,
  `email` varchar(30) NOT NULL,
  `telepon` varchar(16) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`idadmin`, `nama`, `jeniskelamin`, `agama`, `email`, `telepon`) VALUES
(1, 'admin', 'L', 'Buddha', 'admin@smansa.co.id', '');

-- --------------------------------------------------------

--
-- Table structure for table `agama`
--

CREATE TABLE IF NOT EXISTS `agama` (
  `agama` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `agama`
--

INSERT INTO `agama` (`agama`) VALUES
('Buddha'),
('Hindu'),
('Islam'),
('Katolik'),
('Kong Hu Cu'),
('Kristen');

-- --------------------------------------------------------

--
-- Table structure for table `databuku`
--

CREATE TABLE IF NOT EXISTS `databuku` (
  `isbn` varchar(13) NOT NULL,
  `namabuku` varchar(70) NOT NULL,
  `namapenulis` varchar(30) NOT NULL,
  `namapenerbit` varchar(30) NOT NULL,
  `tahunterbit` year(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `databuku`
--

INSERT INTO `databuku` (`isbn`, `namabuku`, `namapenulis`, `namapenerbit`, `tahunterbit`) VALUES
('111222333444', 'Matematika Wajib Kelas X', 'Irwansyah', 'GRAMEDIA', 2020),
('57513390104', 'Bahasa Inggris 2', 'Nirmala', 'Elex Media', 2010),
('86239246915', 'Matematika Wajib Kelas 9', 'Agus Firmansyah', 'Erlangga', 2008);

-- --------------------------------------------------------

--
-- Table structure for table `guru`
--

CREATE TABLE IF NOT EXISTS `guru` (
  `nuptk` varchar(16) NOT NULL,
  `nama` varchar(50) NOT NULL,
  `jeniskelamin` enum('L','P') NOT NULL,
  `agama` varchar(15) DEFAULT NULL,
  `email` varchar(30) NOT NULL,
  `telepon` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `guru`
--

INSERT INTO `guru` (`nuptk`, `nama`, `jeniskelamin`, `agama`, `email`, `telepon`) VALUES
('123456', 'Dummy Guru', 'P', 'Buddha', 'guru@smansa.com', '08123412'),
('6969', 'Dummy Perpus', 'L', 'Katolik', 'perpus@smansa.co.id', '081351739524'),
('878813', 'Rudi Darmawan', 'L', 'Islam', 'rudid@smansa.co.id', '08131313');

-- --------------------------------------------------------

--
-- Table structure for table `hakakses`
--

CREATE TABLE IF NOT EXISTS `hakakses` (
`accessid` int(11) NOT NULL,
  `accessname` varchar(30) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `hakakses`
--

INSERT INTO `hakakses` (`accessid`, `accessname`) VALUES
(1, 'Admin'),
(2, 'Guru'),
(3, 'Siswa'),
(4, 'Staf Perpustakaan');

-- --------------------------------------------------------

--
-- Table structure for table `haribelajar`
--

CREATE TABLE IF NOT EXISTS `haribelajar` (
  `hari` varchar(7) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `haribelajar`
--

INSERT INTO `haribelajar` (`hari`) VALUES
('Jumat'),
('Kamis'),
('Rabu'),
('Selasa'),
('Senin');

-- --------------------------------------------------------

--
-- Table structure for table `jadwal`
--

CREATE TABLE IF NOT EXISTS `jadwal` (
  `kelas` varchar(9) DEFAULT NULL,
  `hari` varchar(7) NOT NULL,
  `jam` time NOT NULL,
  `mapel` varchar(7) NOT NULL,
  `pengajar` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `jadwal`
--

INSERT INTO `jadwal` (`kelas`, `hari`, `jam`, `mapel`, `pengajar`) VALUES
('X_A', 'Senin', '07:00:00', 'UPAC', '123456'),
('X_A', 'Senin', '07:45:00', 'FISK', '123456'),
('X_A', 'Selasa', '07:00:00', 'GEOG', '123456'),
('X_A', 'Senin', '08:30:00', 'FISK', '123456'),
('X_A', 'Senin', '09:15:00', 'BIOL', '123456'),
('X_A', 'Senin', '10:20:00', 'BIOL', '123456'),
('X_A', 'Senin', '11:05:00', 'PJOK', '123456'),
('X_A', 'Senin', '11:50:00', 'PJOK', '123456');

-- --------------------------------------------------------

--
-- Table structure for table `jambelajar`
--

CREATE TABLE IF NOT EXISTS `jambelajar` (
  `jam` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `jambelajar`
--

INSERT INTO `jambelajar` (`jam`) VALUES
('07:00:00'),
('07:45:00'),
('08:30:00'),
('09:15:00'),
('10:20:00'),
('11:05:00'),
('11:50:00'),
('13:35:00');

-- --------------------------------------------------------

--
-- Table structure for table `jenisnilai`
--

CREATE TABLE IF NOT EXISTS `jenisnilai` (
  `kodenilai` int(7) NOT NULL,
  `namanilai` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `jenisnilai`
--

INSERT INTO `jenisnilai` (`kodenilai`, `namanilai`) VALUES
(1, 'Tugas'),
(2, 'Praktek'),
(3, 'Ujian'),
(4, 'UTS'),
(5, 'UAS'),
(6, 'Final');

-- --------------------------------------------------------

--
-- Table structure for table `kelas`
--

CREATE TABLE IF NOT EXISTS `kelas` (
  `kelas` varchar(9) NOT NULL,
  `namakelas` varchar(10) NOT NULL,
  `walikelas` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `kelas`
--

INSERT INTO `kelas` (`kelas`, `namakelas`, `walikelas`) VALUES
('XI_A', 'XI A', '123456'),
('X_A', 'X A', '878813');

-- --------------------------------------------------------

--
-- Table structure for table `mapel`
--

CREATE TABLE IF NOT EXISTS `mapel` (
  `kodemapel` varchar(7) NOT NULL,
  `namamapel` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `mapel`
--

INSERT INTO `mapel` (`kodemapel`, `namamapel`) VALUES
('AGBP', 'Agama & Budi Pekerti'),
('BIGP', 'Bahasa Inggris Peminatan'),
('BIGW', 'Bahasa Inggris Wajib'),
('BIND', 'Bahasa dan Sastra Indonesia'),
('BIOL', 'Biologi'),
('DUMM', 'Mapel Dummy'),
('EKOM', 'Ekonomi'),
('FISK', 'Fisika'),
('GEOG', 'Geografi'),
('KIMI', 'Kimia'),
('MTKP', 'Matematika Peminatan'),
('MTKW', 'Matematika Wajib'),
('PJOK', 'Pendidikan Jasmani, Olahraga, dan Kesehatan'),
('PKWU', 'Prakarya dan Kewirausahaan'),
('PPKN', 'Pendidikan Pancasila dan Kewarganegaraan'),
('SBDK', 'Seni Budaya dan Keterampilan'),
('SEJP', 'Sejarah Peminatan'),
('SEJW', 'Sejarah Wajib'),
('SOSI', 'Sosiologi'),
('UPAC', 'Upacara Bendera');

-- --------------------------------------------------------

--
-- Table structure for table `nilai`
--

CREATE TABLE IF NOT EXISTS `nilai` (
`idnilai` int(11) NOT NULL,
  `mapel` varchar(7) NOT NULL,
  `siswa` varchar(8) NOT NULL,
  `kelas` varchar(9) NOT NULL,
  `tugas` decimal(5,2) unsigned DEFAULT NULL,
  `praktek` decimal(5,2) unsigned DEFAULT NULL,
  `ujian` decimal(5,2) unsigned DEFAULT NULL,
  `uts` decimal(5,2) unsigned DEFAULT NULL,
  `uas` decimal(5,2) unsigned DEFAULT NULL,
  `pengetahuan` int(11) unsigned DEFAULT NULL,
  `keterampilan` int(11) unsigned DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `nilai`
--

INSERT INTO `nilai` (`idnilai`, `mapel`, `siswa`, `kelas`, `tugas`, `praktek`, `ujian`, `uts`, `uas`, `pengetahuan`, `keterampilan`) VALUES
(1, 'GEOG', '2105', 'X_A', '75.25', NULL, '88.00', '75.00', '90.00', 82, 82),
(2, 'GEOG', '2020', 'X_A', '84.00', NULL, '76.00', '81.00', '78.00', 80, 80),
(3, 'GEOG', '2928', 'X_A', '75.00', NULL, '85.00', '70.00', '85.00', 78, 78),
(4, 'FISK', '2105', 'X_A', NULL, NULL, NULL, '95.15', NULL, NULL, NULL),
(5, 'FISK', '2020', 'X_A', NULL, NULL, NULL, '80.00', NULL, NULL, NULL),
(6, 'FISK', '2928', 'X_A', NULL, NULL, NULL, '78.00', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `nilaihitung`
--

CREATE TABLE IF NOT EXISTS `nilaihitung` (
`idnilai` int(11) NOT NULL,
  `mapel` varchar(7) NOT NULL,
  `siswa` varchar(8) NOT NULL,
  `kelas` varchar(9) NOT NULL,
  `nomor` int(11) DEFAULT '1',
  `nilai` decimal(5,2) unsigned DEFAULT NULL,
  `tanggal` date NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `nilaihitung`
--

INSERT INTO `nilaihitung` (`idnilai`, `mapel`, `siswa`, `kelas`, `nomor`, `nilai`, `tanggal`) VALUES
(1, 'GEOG', '2020', 'X_A', 1, '100.00', '2023-08-01'),
(2, 'GEOG', '2105', 'X_A', 1, '80.00', '2023-08-01'),
(3, 'GEOG', '2928', 'X_A', 1, '70.00', '2023-08-01'),
(13, 'GEOG', '2020', 'X_A', 3, '76.00', '2023-08-01'),
(14, 'GEOG', '2105', 'X_A', 3, '88.00', '2023-08-01'),
(15, 'GEOG', '2928', 'X_A', 3, '85.00', '2023-08-01'),
(16, 'GEOG', '2020', 'X_A', 1, '68.00', '2023-08-04'),
(17, 'GEOG', '2105', 'X_A', 1, '70.50', '2023-08-04'),
(18, 'GEOG', '2928', 'X_A', 1, '80.00', '2023-08-04');

-- --------------------------------------------------------

--
-- Table structure for table `peminjamanbuku`
--

CREATE TABLE IF NOT EXISTS `peminjamanbuku` (
`idpeminjaman` int(5) NOT NULL,
  `peminjam` varchar(8) NOT NULL,
  `kelas` varchar(9) NOT NULL,
  `nomorbuku` varchar(13) NOT NULL,
  `tanggalpinjam` date NOT NULL,
  `statuspinjam` enum('Dipinjam','Dikembalikan','Rusak','Hilang') NOT NULL,
  `tanggalpengembalian` date DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `peminjamanbuku`
--

INSERT INTO `peminjamanbuku` (`idpeminjaman`, `peminjam`, `kelas`, `nomorbuku`, `tanggalpinjam`, `statuspinjam`, `tanggalpengembalian`) VALUES
(3, '2105', 'X_A', '111222333444', '2023-05-03', 'Dikembalikan', '2023-05-05'),
(4, '2020', 'X_A', '86239246915', '2023-05-16', 'Dipinjam', NULL),
(5, '2020', 'X_A', '57513390104', '2023-08-17', 'Dipinjam', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `presensi`
--

CREATE TABLE IF NOT EXISTS `presensi` (
  `mapel` varchar(7) NOT NULL,
  `siswa` varchar(8) NOT NULL,
  `kelas` varchar(9) NOT NULL,
  `tanggal` date NOT NULL,
  `status` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `presensi`
--

INSERT INTO `presensi` (`mapel`, `siswa`, `kelas`, `tanggal`, `status`) VALUES
('GEOG', '2020', 'X_A', '2023-05-23', 'Izin'),
('GEOG', '2105', 'X_A', '2023-05-23', 'Hadir'),
('BIOL', '2020', 'X_A', '2023-07-24', 'Hadir'),
('BIOL', '2105', 'X_A', '2023-07-24', 'Izin'),
('PJOK', '2020', 'X_A', '2023-07-24', 'Hadir'),
('PJOK', '2105', 'X_A', '2023-07-24', 'Sakit'),
('GEOG', '2020', 'X_A', '2023-08-01', 'Hadir'),
('GEOG', '2105', 'X_A', '2023-08-01', 'Hadir'),
('GEOG', '2928', 'X_A', '2023-08-01', 'Hadir'),
('GEOG', '2020', 'X_A', '2023-08-04', 'Hadir'),
('GEOG', '2105', 'X_A', '2023-08-04', 'Hadir'),
('GEOG', '2928', 'X_A', '2023-08-04', 'Hadir');

-- --------------------------------------------------------

--
-- Table structure for table `rombel`
--

CREATE TABLE IF NOT EXISTS `rombel` (
  `kelas` varchar(9) NOT NULL,
  `anggota` varchar(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `rombel`
--

INSERT INTO `rombel` (`kelas`, `anggota`) VALUES
('X_A', '2105'),
('X_A', '2020'),
('X_A', '2928');

-- --------------------------------------------------------

--
-- Table structure for table `siswa`
--

CREATE TABLE IF NOT EXISTS `siswa` (
  `nis` varchar(8) NOT NULL,
  `nama` varchar(50) NOT NULL,
  `jeniskelamin` enum('L','P') NOT NULL,
  `agama` varchar(15) DEFAULT NULL,
  `email` varchar(30) NOT NULL,
  `telepon` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `siswa`
--

INSERT INTO `siswa` (`nis`, `nama`, `jeniskelamin`, `agama`, `email`, `telepon`) VALUES
('2020', 'Okky Fenardi', 'L', 'Buddha', 'okky@gmail.com', '0812345678'),
('2105', 'Siswa Dummy', 'L', 'Buddha', 'siswa@smansa.co.id', '082273107891'),
('2928', 'Bana', 'L', 'Katolik', 'risu123@gmail.com', '0871384615');

-- --------------------------------------------------------

--
-- Table structure for table `statuspresensi`
--

CREATE TABLE IF NOT EXISTS `statuspresensi` (
  `status` varchar(20) NOT NULL DEFAULT 'Hadir'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `statuspresensi`
--

INSERT INTO `statuspresensi` (`status`) VALUES
('Alpha'),
('Hadir'),
('Izin'),
('Sakit');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `userid` varchar(16) NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(50) DEFAULT NULL,
  `access` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`userid`, `username`, `email`, `password`, `access`) VALUES
('1', 'admin', 'admin@smansa.co.id', 'admin', 1),
('123456', 'dummyguru', 'guru@smansa.com', 'guru123', 2),
('2020', 'okkyfenardi', 'okky@gmail.com', '0812345678', 3),
('2105', 'siswadummy', 'siswa@smansa.co.id', '082273107891', 3),
('2928', 'risu', 'risu123@gmail.com', '0871384615', 3),
('6969', 'perpus', 'stafperpus@smansa.co.id', 'perpus123', 4),
('878813', 'rudidarmawan', 'rudid@smansa.co.id', '08131313', 2);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
 ADD PRIMARY KEY (`idadmin`), ADD KEY `agamaadmin` (`agama`);

--
-- Indexes for table `agama`
--
ALTER TABLE `agama`
 ADD PRIMARY KEY (`agama`);

--
-- Indexes for table `databuku`
--
ALTER TABLE `databuku`
 ADD PRIMARY KEY (`isbn`);

--
-- Indexes for table `guru`
--
ALTER TABLE `guru`
 ADD PRIMARY KEY (`nuptk`), ADD KEY `agama` (`agama`);

--
-- Indexes for table `hakakses`
--
ALTER TABLE `hakakses`
 ADD PRIMARY KEY (`accessid`);

--
-- Indexes for table `haribelajar`
--
ALTER TABLE `haribelajar`
 ADD PRIMARY KEY (`hari`);

--
-- Indexes for table `jadwal`
--
ALTER TABLE `jadwal`
 ADD KEY `kelas_jadwal` (`kelas`), ADD KEY `jam_jadwal` (`jam`), ADD KEY `hari_jadwal` (`hari`), ADD KEY `mapel_jadwal` (`mapel`), ADD KEY `pengajar_jadwal` (`pengajar`);

--
-- Indexes for table `jambelajar`
--
ALTER TABLE `jambelajar`
 ADD PRIMARY KEY (`jam`);

--
-- Indexes for table `jenisnilai`
--
ALTER TABLE `jenisnilai`
 ADD PRIMARY KEY (`kodenilai`);

--
-- Indexes for table `kelas`
--
ALTER TABLE `kelas`
 ADD PRIMARY KEY (`kelas`), ADD KEY `walikelas` (`walikelas`);

--
-- Indexes for table `mapel`
--
ALTER TABLE `mapel`
 ADD PRIMARY KEY (`kodemapel`);

--
-- Indexes for table `nilai`
--
ALTER TABLE `nilai`
 ADD PRIMARY KEY (`idnilai`), ADD KEY `mapel` (`mapel`), ADD KEY `siswa` (`siswa`), ADD KEY `kelas` (`kelas`);

--
-- Indexes for table `nilaihitung`
--
ALTER TABLE `nilaihitung`
 ADD PRIMARY KEY (`idnilai`), ADD KEY `mapel` (`mapel`), ADD KEY `siswa` (`siswa`), ADD KEY `kelas` (`kelas`), ADD KEY `jenisnilai` (`nomor`);

--
-- Indexes for table `peminjamanbuku`
--
ALTER TABLE `peminjamanbuku`
 ADD PRIMARY KEY (`idpeminjaman`), ADD KEY `peminjamanDatabuku` (`nomorbuku`), ADD KEY `peminjamBuku` (`peminjam`), ADD KEY `peminjamKelas` (`kelas`);

--
-- Indexes for table `presensi`
--
ALTER TABLE `presensi`
 ADD KEY `status` (`status`), ADD KEY `mapel` (`mapel`), ADD KEY `kelas` (`kelas`);

--
-- Indexes for table `rombel`
--
ALTER TABLE `rombel`
 ADD KEY `rombelkelas` (`kelas`), ADD KEY `rombelsiswa` (`anggota`);

--
-- Indexes for table `siswa`
--
ALTER TABLE `siswa`
 ADD PRIMARY KEY (`nis`), ADD KEY `agama` (`agama`);

--
-- Indexes for table `statuspresensi`
--
ALTER TABLE `statuspresensi`
 ADD PRIMARY KEY (`status`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
 ADD PRIMARY KEY (`userid`), ADD KEY `fk_access` (`access`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
MODIFY `idadmin` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT for table `hakakses`
--
ALTER TABLE `hakakses`
MODIFY `accessid` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT for table `nilai`
--
ALTER TABLE `nilai`
MODIFY `idnilai` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=7;
--
-- AUTO_INCREMENT for table `nilaihitung`
--
ALTER TABLE `nilaihitung`
MODIFY `idnilai` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=19;
--
-- AUTO_INCREMENT for table `peminjamanbuku`
--
ALTER TABLE `peminjamanbuku`
MODIFY `idpeminjaman` int(5) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=6;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `admin`
--
ALTER TABLE `admin`
ADD CONSTRAINT `agamaadmin` FOREIGN KEY (`agama`) REFERENCES `agama` (`agama`);

--
-- Constraints for table `guru`
--
ALTER TABLE `guru`
ADD CONSTRAINT `guru_ibfk_1` FOREIGN KEY (`agama`) REFERENCES `agama` (`agama`);

--
-- Constraints for table `jadwal`
--
ALTER TABLE `jadwal`
ADD CONSTRAINT `hari_jadwal` FOREIGN KEY (`hari`) REFERENCES `haribelajar` (`hari`) ON DELETE CASCADE ON UPDATE CASCADE,
ADD CONSTRAINT `jam_jadwal` FOREIGN KEY (`jam`) REFERENCES `jambelajar` (`jam`) ON DELETE CASCADE ON UPDATE CASCADE,
ADD CONSTRAINT `kelas_jadwal` FOREIGN KEY (`kelas`) REFERENCES `kelas` (`kelas`) ON DELETE CASCADE ON UPDATE CASCADE,
ADD CONSTRAINT `mapel_jadwal` FOREIGN KEY (`mapel`) REFERENCES `mapel` (`kodemapel`) ON DELETE CASCADE ON UPDATE CASCADE,
ADD CONSTRAINT `pengajar_jadwal` FOREIGN KEY (`pengajar`) REFERENCES `guru` (`nuptk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `kelas`
--
ALTER TABLE `kelas`
ADD CONSTRAINT `walikelas` FOREIGN KEY (`walikelas`) REFERENCES `guru` (`nuptk`) ON DELETE NO ACTION;

--
-- Constraints for table `nilai`
--
ALTER TABLE `nilai`
ADD CONSTRAINT `nilai_ibfk_1` FOREIGN KEY (`mapel`) REFERENCES `mapel` (`kodemapel`),
ADD CONSTRAINT `nilai_ibfk_2` FOREIGN KEY (`siswa`) REFERENCES `siswa` (`nis`),
ADD CONSTRAINT `nilai_ibfk_3` FOREIGN KEY (`kelas`) REFERENCES `kelas` (`kelas`);

--
-- Constraints for table `nilaihitung`
--
ALTER TABLE `nilaihitung`
ADD CONSTRAINT `jenisnilai` FOREIGN KEY (`nomor`) REFERENCES `jenisnilai` (`kodenilai`),
ADD CONSTRAINT `nilaihitung_ibfk_1` FOREIGN KEY (`mapel`) REFERENCES `mapel` (`kodemapel`),
ADD CONSTRAINT `nilaihitung_ibfk_2` FOREIGN KEY (`siswa`) REFERENCES `siswa` (`nis`),
ADD CONSTRAINT `nilaihitung_ibfk_3` FOREIGN KEY (`kelas`) REFERENCES `kelas` (`kelas`);

--
-- Constraints for table `peminjamanbuku`
--
ALTER TABLE `peminjamanbuku`
ADD CONSTRAINT `peminjamBuku` FOREIGN KEY (`peminjam`) REFERENCES `siswa` (`nis`) ON DELETE NO ACTION ON UPDATE CASCADE,
ADD CONSTRAINT `peminjamKelas` FOREIGN KEY (`kelas`) REFERENCES `kelas` (`kelas`) ON DELETE NO ACTION ON UPDATE CASCADE,
ADD CONSTRAINT `peminjamanDatabuku` FOREIGN KEY (`nomorbuku`) REFERENCES `databuku` (`isbn`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `presensi`
--
ALTER TABLE `presensi`
ADD CONSTRAINT `presensi_ibfk_1` FOREIGN KEY (`status`) REFERENCES `statuspresensi` (`status`),
ADD CONSTRAINT `presensi_ibfk_2` FOREIGN KEY (`mapel`) REFERENCES `mapel` (`kodemapel`),
ADD CONSTRAINT `presensi_ibfk_3` FOREIGN KEY (`kelas`) REFERENCES `kelas` (`kelas`);

--
-- Constraints for table `rombel`
--
ALTER TABLE `rombel`
ADD CONSTRAINT `rombelkelas` FOREIGN KEY (`kelas`) REFERENCES `kelas` (`kelas`) ON DELETE NO ACTION ON UPDATE CASCADE,
ADD CONSTRAINT `rombelsiswa` FOREIGN KEY (`anggota`) REFERENCES `siswa` (`nis`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `siswa`
--
ALTER TABLE `siswa`
ADD CONSTRAINT `siswa_ibfk_1` FOREIGN KEY (`agama`) REFERENCES `agama` (`agama`);

--
-- Constraints for table `user`
--
ALTER TABLE `user`
ADD CONSTRAINT `fk_access` FOREIGN KEY (`access`) REFERENCES `hakakses` (`accessid`) ON DELETE CASCADE ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
