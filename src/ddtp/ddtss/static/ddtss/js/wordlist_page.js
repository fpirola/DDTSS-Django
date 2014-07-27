/*!
 * DDTSS-Django - A Django implementation of the DDTP/DDTSS website.
 * Copyright (C) 2014 Fabio Pirola <fabio@pirola.org>
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

var WORDLIST_PAGE = {
    // This field will evaluated in wordlist_page.html.
    wordlistUrl : undefined,
    // Wordlist DataTable.
    wordlistTable : undefined,

    init : function() {
        // Language variable is defined in wordlist_page.html.
        DDTSS.retrieveWordlist(this.wordlistUrl, WORDLIST_PAGE.populateTable);
    },

    populateTable : function(wordlist) {
        var rows = [];
        WORDLIST_PAGE.buildTable();
        WORDLIST_PAGE.wordlistTable.fnClearTable();
        for (keyCycle in wordlist) {
            if (wordlist.hasOwnProperty(keyCycle)) {
                rows.push([keyCycle,
                    wordlist[keyCycle]]);
            }
        }

        if (rows.length > 0) {
            WORDLIST_PAGE.wordlistTable.fnAddData(rows, true);
        }
        WORDLIST_PAGE.wordlistTable.fnAdjustColumnSizing();
        WORDLIST_PAGE.wordlistTable.fnDraw();
        WORDLIST_PAGE.wordlistTable.fnSort([ [ 0, 'asc' ] ]);
    },
    buildTable : function() {
        WORDLIST_PAGE.wordlistTable = $('#table-wordlist')
        .dataTable(
                {
                    'bSearchable' : true,
                    'bPaginate' : false,
                    'bFilter' : true,
                    'bInfo' : false,
                    'sDom' : '<"top-left"f>rt<"clear">',
                    'bScrollCollapse': true,
                    'language' : {
                        'emptyTable' : 'No wordlist defined for this language.',
                        'infoEmpty' : 'No wordlist defined for this language.'
                     },
                    'fnRowCallback' : function(nRow, aData,
                            iDisplayIndex, iDisplayIndexFull) {
                        return nRow;
                    }
                });
        new $.fn.dataTable.FixedHeader( WORDLIST_PAGE.wordlistTable );
    }
};

// Document ready!
$(document).ready(function() {
    WORDLIST_PAGE.init();
});
