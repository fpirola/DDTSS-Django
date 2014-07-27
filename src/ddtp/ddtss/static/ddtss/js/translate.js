/*!
 * DDTSS-Django - A Django implementation of the DDTP/DDTSS website.
 * Copyright (C) 2011-2014 Martijn van Oosterhout <kleptog@svana.org>
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

var TRANSLATE = {
    showShortDiff : function(url) {
        var box,
            boxes = document.getElementsByName('shortboxes'),
            i;
        for(i = boxes.length - 1; i >= 0; i -= 1) {
            boxes[i].style.display = 'none';
        }
        /* Coded like this to avoid errors on 'None' */
        box = document.getElementById(url)
        if(box) {
            box.style.display = 'block';
        }
    },

    showLongDiff : function(url) {
        var boxes = document.getElementsByName('longboxes'),
            i;
        for(i = boxes.length - 1; i > 0; i -= 1) {
            boxes[i].style.display = 'none';
        }
        box = document.getElementById(url);
        if(box) {
            box.style.display='block';
        }
        return false;
    },

    toggleShowShortDescr : function() {
        var showDescrFields = document.getElementsByName('ShowShortDescr');
        for(i = showDescrFields.length; i > 0; i -= 1) {
            if(showDescrFields[i].style.display === 'block') {
                showDescrFields[i].style.display = 'none';
            } else {
                showDescrFields[i].style.display = 'block';
            }
        }
        return false;
    },

    toggleShowLongDescr : function() {
        var showDescrFields = document.getElementsByName('ShowLongDescr'),
            i;
        for(i = showDescrFields.length; i > 0; i -= 1) {
            if(showDescrFields[i].style.display === 'block') {
                showDescrFields[i].style.display = 'none';
            } else {
                showDescrFields[i].style.display = 'block';
            }
        }
        return false;
    }
};

$(document).ready(function($) {
    $('#submit').prop('disabled',true);
    DDTSS.setupMessagelinks();
})