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


// list: list of time interval
// instant: moment in time
// return the index i such that list[i-1]<=instant<list[i] if exists
//        0 if instant<list[0]
//        list.length if instant>=list[j]
function index_in_pref(list, instant) {
  var after = false;
  var i = 0;

  while (!after && i < list.length) {
    if (list[i] > instant) {
      after = true;
    } else {
      i++;
    }
  }
  return i;
}




// get the aggregated preference score of tutor on day, on an interval
// lasting duration, starting at start_time
// assumes well-formed (consecutive) intervals
function get_preference(pref, start_time, duration) {
  var after = false;
  var t = department_settings.time;


  if (pref.length == 0) {
    return -1;
  }
  if (duration == 0) {
    return 1;
  }

  var instants = pref.map(function (d) {
    return d.start_time;
  });
  instants.push(pref[pref.length - 1].start_time + pref[pref.length - 1].duration);

  var i_start = index_in_pref(instants, start_time);
  var i_end = index_in_pref(instants, start_time + duration);
  // correct border case
  if (i_end > 0 && instants[i_end - 1] == start_time + duration) {
    i_end -= 1;
  }

  var unavailable, unknown;

  // unknown value due to too short interval
  unknown = false;
  // all outside
  if (i_end == 0 || i_start == instants.length) {
    return -1;
  }
  // partly outside
  if (i_start == 0 || i_end == instants.length) {
    unknown = true;
  }

  // cut outside
  i_start = Math.max(0, i_start - 1);
  i_end = Math.min(pref.length - 1, i_end - 1);

  var i, tot_weight, weighted_pref, w;
  weighted_pref = 0;
  tot_weight = 0;

  unavailable = false;
  i = i_start;
  while (i <= i_end && !unavailable) {
    if (pref[i].value == 0) {
      unavailable = true;
    } else if (pref[i].value == -1) {
      unknown = true;
    } else {
      w = pref[i].duration
        - Math.max(0, start_time - pref[i].start_time)
        - Math.max(0, start_time + duration -
          (pref[i].start_time + pref[i].duration));
      tot_weight += w;
      weighted_pref += w * pref[i].value;
    }
    i += 1;
  }

  if (unavailable) {
    return 0;
  }
  if (unknown) {
    return -1;
  }

  return weighted_pref / tot_weight;
}


// period: {day: , start:, duration: }
function find_in_pref(pref, entity, period) {
  if (!Object.keys(pref).includes(entity)) {
    return undefined;
  }
  if (!Object.keys(pref[entity]).includes(period.day)) {
    return undefined;
  }

  return get_preference(pref[entity][period.day],
    period.start, period.duration);
}



function no_overlap(list, start_time, duration) {
  if (list.length == 0 || duration == 0) {
    return true;
  }

  var i_start = index_in_pref(list.map(function (d) { return d.start_time; }), start_time);
  var i_end = index_in_pref(list.map(function (d) { return d.start_time; }), start_time + duration);

  // too far
  if (i_end > i_start + 1) {
    return false;
  }

  // start inside an occupied interval
  if (i_start != 0
      && list[i_start - 1].start_time + list[i_start - 1].duration > start_time) {
    return false ;
  }

  // should end after the next occupied interval
  if (i_end == i_start
      || i_end == i_start + 1 && list[i_end - 1].start_time == start_time + duration) {
    return true ;
  }

  return false ;
}



// get all prefs that includes ]start_time, start_time+duration[
function get_covered_preferences(pref, start_time, duration) {
  return  pref.filter(function(p) {
    return ! (p.start_time>=start_time+duration
              || p.start_time + p.duration <=start_time) ;
  });
}


function update_pref_interval(tutor, day, start_time, duration, value) {
  var pref = dispos[user.name][day];
  var covered_preferences = get_covered_preferences(pref, start_time, duration);
  covered_preferences.forEach(function (p) {
    p.value = value ;
  });
  if (user.name == tutor) {
    user.dispos = user.dispos.filter(function(p) {
      return p.day != day ;
    });
    dispos[user.name][day].forEach(function(p) {
      user.dispos.push(Object.assign({day:day, off:-1}, p));
    });
  }
}


// PRECOND: sorted preference list
// fill preference list with def_value so that any moment has a value
function fill_holes(pref, def_value) {
  var i = 0;
  while (i < pref.length - 1) {
    if (pref[i].start_time + pref[i].duration < pref[i + 1].start_time) {
      pref.splice(i + 1, 0,
        {
          start_time: pref[i].start_time + pref[i].duration,
          duration: pref[i + 1].start_time - (pref[i].start_time + pref[i].duration),
          value: def_value
        });
      i++;
    }
    i++;
  }
}

function extend_pref(pref_list, start, end, value) {
  if (pref_list[0].start_time > start) {
    pref_list.unshift({
      start_time: start,
      duration: pref_list[0].start_time - start,
      value: value,
    });
  }
  let prev_end =
    pref_list[pref_list.length - 1].start_time +
    pref_list[pref_list.length - 1].duration;
  if (end > prev_end) {
    pref_list.push({
      start_time: prev_end,
      duration: end - prev_end,
      value: value,
    });
  }
}

function merge_pref(dic, key_from, key_to) {
  let existing_keys = Object.keys(dic);
  if (existing_keys.indexOf(key_from) == -1) {
    return;
  }
  if (existing_keys.indexOf(key_to) == -1) {
    let days_from = Object.keys(dic[key_from]);
    dic[key_to] = {};
    for (iday = 0; iday < days_from.length; iday++) {
      dic[key_to][days_from[iday]] = [];
    }
  }

  let common_days = Object.keys(dic[key_from]).filter(function (day) {
    return Object.keys(dic[key_to]).indexOf(day) !== -1;
  });

  for (ik = 0; ik < common_days.length; ik++) {
    let day = common_days[ik];
    if (dic[key_from][day].length == 0) {
      continue;
    }
    if (dic[key_to][day].length == 0) {
      dic[key_to][day] = dic[key_from][day].slice();
      continue;
    }

    let p_from = dic[key_from][day];
    let p_to = dic[key_to][day];
    let i_from = 0;
    let i_to = 0;
    let p_merged = [];

    let new_start = Math.min(p_from[0].start_time, p_to[0].start_time);
    let new_end = Math.max(
      p_from[p_from.length - 1].start_time + p_from[p_from.length - 1].duration,
      p_to[p_to.length - 1].start_time + p_to[p_to.length - 1].duration
    );
    extend_pref(p_from, new_start, new_end, 1);
    extend_pref(p_to, new_start, new_end, 1);

    let next_slot = { start_time: new_start };
    while (
      p_from[i_from].start_time + p_from[i_from].duration < new_end ||
      p_to[i_to].start_time + p_to[i_to].duration < new_end
    ) {
      let end_from = p_from[i_from].start_time + p_from[i_from].duration;
      let end_to = p_to[i_to].start_time + p_to[i_to].duration;
      next_slot["value"] = Math.min(
        p_from[i_from]["value"],
        p_to[i_to]["value"]
      );
      if (end_from <= end_to) {
        next_slot["duration"] = end_from - next_slot["start_time"];
        p_merged.push(next_slot);
        next_slot = { start_time: end_from };
        i_from++;
        if (end_to == end_from) {
          i_to++;
        }
      } else if (end_to < end_from) {
        next_slot["duration"] = end_to - next_slot["start_time"];
        p_merged.push(next_slot);
        next_slot = { start_time: end_to };
        i_to++;
      }
    }
    next_slot["value"] = Math.min(p_from[i_from]["value"], p_to[i_to]["value"]);
    next_slot["duration"] = new_end - next_slot["start_time"];
    p_merged.push(next_slot);

    dic[key_to][day] = p_merged;
  }
}
