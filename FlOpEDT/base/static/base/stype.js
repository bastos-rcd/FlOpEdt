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


// Redefinition of some variables

dsp_svg.margin = { top: 50, left: 50, right: 10, bot: 10 };

dsp_svg.h = 625 - dsp_svg.margin.top - dsp_svg.margin.bot;
dsp_svg.w = 900 - dsp_svg.margin.left - dsp_svg.margin.right;

dsp_svg.cadastre = [
  // dispos info ground
  ["svg", "pmg"],
  // valider
  ["svg", "vg"],
  // background, middleground, foreground, dragground
  ["svg", "edtg"],
  ["edtg", "edt-bg"],
  ["edtg", "edt-mg"],
  ["edtg", "edt-fg"],
  // context menus ground
  ["svg", "cmg"],
  ["cmg", "cmpg"],
  ["cmg", "cmtg"],
  // drag ground
  ["svg", "dg"]
];


var mode = "tutor";

var dd_selections = {
  'tutor': { value: logged_usr.name },
  'prog': { value: '' },
  'type': { value: '' },
  'room': { value: '' }
};



smiley.tete = 8;

dim_dispo.width = 80;
dim_dispo.height = 500;
dim_dispo.mh = 10;
dim_dispo.plot = 1;
nbRows = 1;
scale = dim_dispo.height / nb_minutes_in_grid();
pref_selection.choice.w = 35;
pref_selection.choice.h = 35;


ckbox["dis-mod"].cked = true;

pref_only = true;
var pref_fetched = false ;

svg = new Svg(dsp_svg.layout_tree, false);
svg.create_container(true);
svg.create_layouts(dsp_svg.cadastre);

var days_header = new WeekDayHeader(svg, "edt-fg", week_days, false, null);

// overwrite functions for headers
function WeekDayMixStype() {
  this.gsckd_x = function (datum, i) {
    return i * (dim_dispo.width + dim_dispo.mh)
      + dim_dispo.width * .5;
  };
  this.gsckd_y = function (datum) {
    return - 20;
  };
  this.gsckd_txt = function (d) {
    return d.name;
  };
  this.gsckh_x = function (datum) {
    return - dim_dispo.width;
  };
}
Object.assign(days_header.mix, new WeekDayMixStype());
hard_bind(days_header.mix);

var hours_header = new HourHeader(svg, "edt-fg", hours);

var labgp = {width: 0};

hours_header.create_indicator();

go_days(true, false);
create_pref_modes(pref_only);
fetch_pref_only();





function create_lunchbar() {
  svg.get_dom("edt-fg")
    .append("line")
    .attr("class", "lunchbar")
    .attr("stroke", "black")
    .attr("stroke-width", 6)
    .attr("x1", 0)
    .attr("y1", gsclb_y)
    .attr("x2", gsclb_x)
    .attr("y2", gsclb_y);

}


/*---------------------
  ------- DISPOS ------
  ---------------------*/
function fetch_url() {
  switch (mode) {
  case 'tutor':
    return build_url(url_user_pref_default, {user: user.name});
  case 'course':
    return build_url(
      url_fetch_course_dweek,
      {
        dept: department,
        train_prog: dd_selections['prog'].value,
        course_type: dd_selections['type'].value
      }
    );
  case 'room':
    return build_url(url_fetch_room_dweek, {room: user.name});
  }
}


function course_type_prog_name(prog, ctype) {
  return prog + '--' + ctype;
}


function translate_course_preferences_from_csv(d) {
  var pseudo_tutor = course_type_prog_name(d.train_prog, d.course_type);

  if (Object.keys(dispos).indexOf(pseudo_tutor) == -1) {
    dispos[pseudo_tutor] = {};
    week_days.forEach(function (day) {
      dispos[pseudo_tutor][day.ref] = [];
    });
  }
  dispos[pseudo_tutor][d.day].push({
    start_time: +d.start_time,
    duration: +d.duration,
    value: +d.value
  });
}


function translate_room_preferences_from_csv(d) {
  var i;
  if (Object.keys(dispos).indexOf(d.room) == -1) {
    dispos[d.room] = {};
    week_days.forEach(function (day) {
      dispos[d.room][day.ref] = [];
    });
  }
  dispos[d.room][d.day].push({
    start_time: +d.start_time,
    duration: +d.duration,
    value: +d.value,
  });
}


function translate_pref_from_csv(d) {
  switch (mode) {
  case 'tutor':
    return translate_dispos_from_csv(d);
  case 'course':
    return translate_course_preferences_from_csv(d);
  case 'room':
    return translate_room_preferences_from_csv(d);
  }
}



function fetch_pref_only() {
  show_loader(true);
  $.ajax({
    type: "GET",
    headers: {Accept: 'text/csv'},
    dataType: 'text',
    url: fetch_url(),
    async: false,
    success: function (msg) {
      console.log(msg);

      console.log("in");
      dispos = {};
      user.dispos_type = [];
      user.dispos_type = d3.csvParse(msg, translate_pref_from_csv);
      create_dispos_user_data();
      pref_fetched = true ;
      arrange_stype_layout() ;
      go_pref(true);
      show_loader(false);
    },
    error: function (xhr, error) {
      console.log("error");
      console.log(xhr);
      console.log(error);
      console.log(xhr.responseText);
      show_loader(false);
      // window.location.href = url_login;
      //window.location.replace(url_login+"?next="+url_stype);
    }
  });
}


function arrange_stype_layout() {
  open_lunch() ;
  hours_header.update() ;
  svg.get_dom('pmg').attr("transform", "translate(" + pmg_x() + ", 0)") ;
  let max_time = department_settings.time.day_finish_time ;
  user.dispos.forEach(function(d) {
    let end = d.start_time + d.duration ;
    if (end > max_time) {
      max_time = end ;
    }
  });
  d3.select("#edt-main")
    .attr(
      "height",
      dispo_y({start_time: max_time}) + dsp_svg.margin.bot + dsp_svg.margin.top
    )
    .attr(
      "width",
      dsp_svg.margin.left
        + pmg_x()
        + pref_mode_choice_trans_x()
        + pref_selection.choice.w
        + pref_selection.marx
    );
}
















function dispo_x(d) {
  return week_days.day_by_ref(d.day).num * (dim_dispo.width + dim_dispo.mh);
}
function dispo_h(d) {
  return d.duration * scale;
}



function gsclb_y() {
  return dispo_y({
    start_time:
      department_settings.time.lunch_break_start_time
  });
}
function gsclb_x() {
  return (dim_dispo.width + dim_dispo.mh) * week_days.nb_days() - dim_dispo.mh;
}






d3.select("body")
  .on("click", function (d) {
    cancel_cm_adv_preferences();
    cancel_cm_room_tutor_change();
  });



// compute url to send preference changes to
// according to mode
function send_url(year, week) {
  switch (mode) {
  case 'tutor':
    return url_user_pref_changes + year + "/" + week
      + "/" + user.name + "/";
  case 'course':
    return url_course_pref_changes + year + "/" + week
      + "/" + dd_selections['prog'].value
      + "/" + dd_selections['type'].value + "/";
  case 'room':
    return url_room_pref_changes + year + "/" + week
      + "/" + user.name + "/";
  }
}


function apply_stype_from_button(save) {

  var changes = [];
  compute_pref_changes(changes);
  var sent_data = {};
  sent_data['changes'] = JSON.stringify(changes);

  var week_st, year_st, week_end, year_end;
  var year, se;
  var se_abs_max = 53;
  var se_min, se_max;

  if (save) {
    week_st = 0;
    console.log(current_year);
    year_st = +current_year;
    week_end = week_st;
    year_end = year_st;
  } else {
    week_st = +document.forms['app'].elements['week_st'].value;
    year_st = +document.forms['app'].elements['year_st'].value;
    week_end = +document.forms['app'].elements['week_end'].value;
    year_end = +document.forms['app'].elements['year_end'].value;
  }


  if (year_st < year_end ||
    (year_st == year_end && week_st <= week_end)) {


    if (changes.length == 0) {
      ack.pref = "RAS";
      document.getElementById("ack").textContent = ack.pref;
    } else {

      ack.pref = "Ok ";
      if (save) {
        ack.pref += "semaine type";
      } else {
        ack.pref += "week " + week_st + " année " + year_st
          + " à week " + week_end + " année " + year_end;
      }


      for (year = year_st; year <= year_end; year++) {
        if (year == year_st) {
          se_min = week_st;
        } else {
          se_min = 1;
        }
        if (year == year_end) {
          se_max = week_end;
        } else {
          se_max = se_abs_max;
        }

        for (se = se_min; se <= se_max; se++) {

          //console.log(se,year);
          show_loader(true);
          $.ajax({
            url: send_url(year, se),
            type: 'POST',
            //			contentType: 'application/json; charset=utf-8',
            data: sent_data, //JSON.stringify(changes),
            dataType: 'json',
            success: function (msg) {
              if (msg.status != 'OK') {
                ack.pref = msg.more;
              }
              document.getElementById("ack").textContent = ack.pref;
              show_loader(false);
            },
            error: function (msg) {
              ack.pref = 'Pb communication serveur';
              document.getElementById("ack").textContent = ack.pref;
              show_loader(false);
            }
          });
        }
      }
    }

  } else {
    ack.pref = "Problème : seconde week avant la première";
    document.getElementById("ack").textContent = ack.pref;
  }


}

d3.select("html")
  .on("mouseup", function(d) {
    pref_selection.start = null ;
    go_pref(true);
  });
