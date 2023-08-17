/**
 *
 * You can write your JS code here, DO NOT touch the default style file
 * because it will make it harder for you to update.
 *
 */

"use strict";
$(document).ready(function() {
    // Fungsi search judul buku
    $('#searchInput').on('input', function() {
        const searchValue = $(this).val().toLowerCase();
        $('.dropdown-item').each(function() {
            const text = $(this).text().toLowerCase();
            if (text.includes(searchValue)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });

    // Mengambil nilai dari opsi dropdown yang dipilih
    $('.dropdown-item').click(function() {
        const selectedOption = $(this).text();
        $('#buku').val(selectedOption);
        $('.btn.dropdown-toggle').text(selectedOption);
    });
});