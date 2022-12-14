// This file is part of the FlOpEDT/FlOpScheduler project.
// Copyright (c) 2017
// Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
// Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public
// License along with this program. If not, see
// <http://www.gnu.org/licenses/>.
// 
// You can be released from the requirements of the license by purchasing
// a commercial license. Buying such a license is mandatory as soon as
// you develop activities involving the FlOpEDT/FlOpScheduler software
// without disclosing the source code of your own applications.

getMethods = (obj) => Object.getOwnPropertyNames(obj).filter(item => typeof obj[item] === 'function');

// useful to avoid d3 to redefine 'this'
function hard_bind(obj) {
    var methods = getMethods(obj);
    for (var i = 0; i < methods.length; i++) {
        obj[methods[i]] = obj[methods[i]].bind(obj);
    }
}


function get_transition(immediate) {
    if (immediate) {
        return d3.transition()
            .duration(0);
    } else {
        return d3.transition();
    }
}


// add get parameters to the url
function build_url(url, ...contexts) {
    let full_context = contexts.reduce(
        function (acc, val) {
            return Object.assign(acc, val);
        },
        {}
    );
    return url + "?" + Object.keys(full_context).map(
        function (p) {
            return p + "=" + full_context[p];
        }
    ).join("&");
}

function getCookie(name) {
    if (!document.cookie) {
        return null;
    }

    const xsrfCookies = document.cookie.split(';')
        .map(c => c.trim())
        .filter(c => c.startsWith(name + '='));

    if (xsrfCookies.length === 0) {
        return null;
    }
    return decodeURIComponent(xsrfCookies[0].split('=')[1]);
}

const csrfToken = getCookie('csrftoken');

async function postData(url = '', data = {}) {
    // Default options are marked with *
    const response = await fetch(`${url}${data.name}/`, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'same-origin', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
    let body = await response.json() // parses JSON response into native JavaScript objects
    if (!(response.ok)) {
        return Promise.reject(body)
    }
    return body;
}

async function deleteData(url = '', data = {}) {
    const response = await fetch(`${url}${data.name}/${data.id}`, {
        method: 'DELETE',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': csrfToken,
        },
        redirect: 'follow',
        referrerPolicy: 'same-origin',
    });
    let body = await response.json() // parses JSON response into native JavaScript objects
    if (!(response.ok)) {
        return Promise.reject(body)
    }
    return body;
}

async function putData(url = '', data = {}) {
    const response = await fetch(`${url}${data.name}/${data.id}/`, {
        method: 'PUT',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        redirect: 'follow',
        referrerPolicy: 'same-origin',
        body: JSON.stringify(data),
    });
    let body = await response.json() // parses JSON response into native JavaScript objects
    if (!(response.ok)) {
        return Promise.reject(body)
    }
    return body;
}

// Returns the ISO week of the date.
Date.prototype.getWeek = function() {
  var date = new Date(this.getTime());
  date.setHours(0, 0, 0, 0);
  // Thursday in current week decides the year.
  date.setDate(date.getDate() + 3 - (date.getDay() + 6) % 7);
  // January 4 is always in week 1.
  var week1 = new Date(date.getFullYear(), 0, 4);
  // Adjust to Thursday in week 1 and count number of weeks from date to week1.
  return 1 + Math.round(((date.getTime() - week1.getTime()) / 86400000
                         - 3 + (week1.getDay() + 6) % 7) / 7);
}
