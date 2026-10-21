<?php
declare(strict_types=1);

// simpan-xtc.php
$nama = $_GET['nama'] ?? 'Asmaul-Husna.xtc';
$nama = basename($nama);
$tambah = !empty($_GET['tambah']);

$xtcDir = getenv('XTC_DIR') ?: dirname(__DIR__) . '/xtc';
if (!is_dir($xtcDir)) {
    mkdir($xtcDir, 0755, true);
}

$target = $xtcDir . '/' . $nama;
$flags = $tambah ? FILE_APPEND : 0;

$input = fopen('php://input', 'rb');
if (!$input) {
    http_response_code(400);
    exit("Gagal membaca payload.");
}

$out = fopen($target, $tambah ? 'ab' : 'wb');
if (!$out) {
    http_response_code(500);
    exit("Gagal membuka file tujuan: $target");
}

stream_copy_to_stream($input, $out);
fclose($input);
fclose($out);

http_response_code(200);
echo "OK: $target";
