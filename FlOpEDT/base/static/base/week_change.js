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



           /*     \
          ----------           
        --------------         
      ------------------       
    ----------------------     
  --------------------------   
------------------------------ 
------  ON WEEK CHANGE  ------ 
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
                 */


/*---------------------
  ------- DISPOS ------
  ---------------------*/

// fetch all tutor preferences
function fetch_tutor_preferences() {


  fetch_status.ongoing_dispos = true;

  var exp_week = wdw_weeks.get_selected();
  let context = {dept: department};
  exp_week.add_to_context(context);

  show_loader(true);
  $.ajax({
    type: "GET", //rest Type
    headers: {Accept: 'text/csv'},
    dataType: 'text',
    url: build_url(url_user_pref, context),
    async: true,
    success: function (msg) {
      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {
        dispos = {};
        //user.dispos = [];
        d3.csvParse(msg, translate_dispos_from_csv);
        sort_preferences(dispos);
        fetch_status.ongoing_dispos = false;
        fetch_status.pref_saved = true;
        if (ckbox["dis-mod"].cked) {
          create_dispos_user_data();
          open_lunch() ;
          go_edt(false);
          create_pref_modes();
        }

        fetch_ended(false);
      }
      show_loader(false);


    },
    error: function (xhr, error) {
      console.log("error");
      console.log(xhr);
      console.log(error);
      console.log(xhr.responseText);
      show_loader(false);
      // window.location.href = url_login;
      window.location.replace(url_login + "?next=" + url_edt + exp_week.year + "/" + exp_week.week);
    }
  });
}


function translate_dispos_from_csv(d) {
  if (Object.keys(dispos).indexOf(d.user) == -1) {
    dispos[d.user] = {};
    week_days.forEach(function (day) {
      dispos[d.user][day.ref] = [];
    });
  }
  if(Object.keys(week_days.day_dict).includes(d.day)) {
    dispos[d.user][d.day].push({
      start_time: +d.start_time,
      duration: +d.duration,
      value: +d.value
    });
  }
}


// if there exist tutor preferences that would be cut 
function open_lunch() {
  let t = department_settings.time ;
  if (Object.keys(t.bu).length > 0) {
    return ;
  }
  let during_lunch = user.dispos.filter(function(d){
    return !(d.start_time + d.duration <= t.lunch_break_start_time
             || d.start_time >= t.lunch_break_finish_time) ;
  });
  if (during_lunch.length > 0) {
    t.bu.lunch_break_finish_time = t.lunch_break_finish_time ;
    t.lunch_break_finish_time = t.lunch_break_start_time ;
  }
  let min_start = t.day_start_time ;
  user.dispos.forEach(function(d){
    if (d.start_time < min_start) {
      min_start = d.start_time ;
    }
  });
  if (min_start < t.day_start_time) {
    t.bu.day_start_time = t.day_start_time ;
    t.day_start_time = min_start ;
  }
  let max_finish = t.day_finish_time ;
  user.dispos.forEach(function(d){
    if (d.start_time + d.duration > max_finish) {
      max_finish = d.start_time + d.duration ;
    }
  });
  if (max_finish > t.day_finish_time) {
    t.bu.day_finish_time = t.day_finish_time ;
    t.day_finish_time = max_finish ;
  }
}


// fetch the moments where a tutor teaches in another departement
function fetch_tutor_extra_unavailability() {

  let exp_week = wdw_weeks.get_selected();

  show_loader(true);
  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    url: build_url(
      url_fetch_extra_sched, context_dept, exp_week.as_context(),
      {'username': user.name}),
    async: true,
    contentType: "text/csv",
    success: function (msg) {
      //console.log(msg);
      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {
        extra_pref.tutors = {};
        d3.csvParse(msg, translate_extra_pref_tut_from_csv);
        sort_preferences(extra_pref.tutors);
        var tutors = Object.keys(extra_pref.tutors);
        for (i = 0; i < tutors.length; i++) {
          var busy_days = Object.keys(extra_pref.tutors[tutors[i]]);
          for (d = 0; d < busy_days.length; d++) {
            fill_holes(extra_pref.tutors[tutors[i]][busy_days[d]], 1);
          }
        }
      }
      show_loader(false);

    },
    error: function (xhr, error) {
      console.log("error");
      console.log(xhr);
      console.log(error);
      console.log(xhr.responseText);
      show_loader(false);
      // window.location.href = url_login;
      window.location.replace(url_login + "?next=" + url_edt + exp_week.url());
    }
  });
}




function translate_extra_pref_tut_from_csv(d) {
  if (Object.keys(extra_pref.tutors).indexOf(d.tutor) == -1) {
    extra_pref.tutors[d.tutor] = {};
    for (var i = 0; i < days.length; i++) {
      extra_pref.tutors[d.tutor][days[i].ref] = [];
    }
  }
  extra_pref.tutors[d.tutor][d.day].push({
    start_time: +d.start_time,
    duration: +d.duration,
    value: 0
  });
}


function sort_preferences(pref) {
  var i, d;
  var tutors_or_rooms = Object.keys(pref);
  for (i = 0; i < tutors_or_rooms.length; i++) {
    week_days.forEach(function (day) {
      pref[tutors_or_rooms[i]][day.ref].sort(
        function (a, b) {
          return a.start_time - b.start_time;
        }
      );
    });
  }
}

// insert a valued interval into a list of valued interval
// (splices it and divides it if needed)
// pref: {start_time, duration, value}
// list: list of pref
function insert_interval(pref, list) {
  var ts = department_settings.time;

  // starts too early or finishes too late
  if (pref.start_time < ts.day_start_time) {
    pref.duration -= ts.day_start_time - pref.start_time;
    pref.start_time = ts.day_start_time;
  }
  if (pref.start_time + pref.duration > ts.day_finish_time) {
    pref.duration -= pref.start_time + pref.duration - ts.day_finish_time;
  }

  // lunch break
  if (pref.start_time < ts.lunch_break_start_time) {
    // starts in the morning
    if (pref.start_time + pref.duration > ts.lunch_break_start_time) {
      if (pref.start_time + pref.duration < ts.lunch_break_finish_time) {
        // finishes during lunch break
        pref.duration -= pref.start_time + pref.duration - ts.lunch_break_start_time;
      } else {
        // cut by lunch break
        insert_normalized_interval(
          {
            start_time: ts.lunch_break_finish_time,
            duration: pref.start_time + pref.duration - ts.lunch_break_finish_time,
            value: pref.value
          },
          list);
        pref.duration = ts.lunch_break_start_time - pref.start_time;
      }
    }
  } else if (pref.start_time + pref.duration < ts.lunch_break_finish_time) {
    // fully within lunch break
    return;
  } else if (pref.start_time < ts.lunch_break_finish_time) {
    // starts during lunch break
    pref.duration -= ts.lunch_break_finish_time - pref.start_time;
    pref.start_time = ts.lunch_break_finish_time;
  }
  insert_normalized_interval(pref, list);
}

// PRECOND: interval fully within the working hours
// pref: {start_time, duration, value}
// list: list of pref
function insert_normalized_interval(pref, list) {
  //    list.splice(index, nbElements, item)
  list.push(pref);
}


function allocate_dispos(tutor) {
  dispos[tutor] = {};
  week_days.forEach(function (day) {
    dispos[tutor][day.ref] = [];
  });
}

// -- no slot --
// --  begin  --
// to change, maybe, if splitting intervals is not allowed
// in the interface
function fill_missing_preferences(pref, ts) {
  week_days.forEach(function (day) {
    var current = ts.day_start_time;
    var next;
    while (current < ts.day_finish_time) {
      if (current < ts.lunch_break_start_time) {
        next = Math.min(
          current + ts.def_pref_duration,
          ts.lunch_break_start_time);
      } else {
        next = Math.min(
          current + ts.def_pref_duration,
          ts.day_finish_time);
      }
      insert_interval(
        {
          start_time: current,
          duration: next - current,
          value: -1
        },
        pref[day.ref]
      );
      if (next == ts.lunch_break_start_time) {
        next = ts.lunch_break_finish_time;
      }
      current = next;
    }
  });

}
// --   end   --
// -- no slot --


// -- no slot --
// --  begin  --
// to be cleaned: user.dispos should be avoidable
// off: offset useful for the view. Quite unclean.
function create_dispos_user_data() {

  var d, j, k, d2p, pref_list;
  var ts = department_settings.time;

  user.dispos = [];
  user.dispos_bu = [];

  var current;

  if (dispos[user.name] === undefined) {
    allocate_dispos(user.name);
    fill_missing_preferences(dispos[user.name], ts);
    sort_preferences(dispos);
  }

  week_days.day_list.forEach(function (day) {
    pref_list = dispos[user.name][day.ref];
    for (var k = 0; k < pref_list.length; k++) {
      d2p = {
        day: day.ref,
        start_time: pref_list[k].start_time,
        duration: pref_list[k].duration,
        value: pref_list[k].value,
        off: -1
      };
      user.dispos_bu.push(d2p);
      if (pref_list[k].value < 0) {
        if (!pref_only) {
          let default_pref = get_dispos_type(d2p);
          if (default_pref != null) {
            pref_list[k].value = default_pref.value;
          } else {
            pref_list[k].value = 0 ;
          }
        } else {
          pref_list[k].value = par_dispos.nmax;
        }
      }

      // different object
      user.dispos.push({
        day: day.ref,
        start_time: pref_list[k].start_time,
        duration: pref_list[k].duration,
        value: pref_list[k].value,
        off: -1
      });
    }

  });



}
// --   end   --
// -- no slot --



/*---------------------
  ------- WEEKS -------
  ---------------------*/
/*----------------------
  -------- GRID --------
  ----------------------*/
/*----------------------
  ------- GROUPS -------
  ----------------------*/
/*--------------------
  ------ MENUS -------
  --------------------*/
/*----------------------
  ------ MODULES -------
  ----------------------*/
/*--------------------
  ------ PROFS -------
  --------------------*/
function fetch_colors() {
  var exp_week = wdw_weeks.get_selected();

  cours_bouge = {};

  show_loader(true);
  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    url: url_colors + "?week=" + exp_week.week
      + "&year=" + exp_week.year
      + "&work_copy=" + num_copie,
    async: true,
    success: function (msg, ts, req) {
      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {
        colors = {} ;
        d3.csvParse(msg, translate_colors_from_csv);

        fetch_status.ongoing_colors = false;
        fetch_ended(false);
      }
      show_loader(false);
    },
    error: function (msg) {
      console.log("error");
      show_loader(false);
    }
  });

}

function translate_colors_from_csv(d) {
  colors[d.key] = {
    color_bg: d.color_bg,
    color_txt: d.color_txt
  };
}
// touch courses to trigger color update
function ping_colors() {
  cours.forEach(function(c) {
    c.color_bg = cours_fill(c) ;
    c.color_txt = cours_txt_fill(c);
  });
}

/*--------------------
  ------ BKNEWS -------
  --------------------*/
function fetch_bknews(first) {
  fetch_status.ongoing_bknews = true;

  var exp_week = wdw_weeks.get_selected();
  let context = {dept: department};
  exp_week.add_to_context(context);

  show_loader(true);
  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    url: build_url(url_bknews, context),
    async: true,
    contentType: "text/csv",
    headers: {Accept: 'text/csv'},
    success: function (msg) {
      bknews.cont = d3.csvParse(
        msg,
        translate_bknews_from_csv
      );

      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {
        var max_y = -1;
        for (var i = 0; i < bknews.cont.length; i++) {
          if (bknews.cont[i].y > max_y) {
            max_y = bknews.cont[i].y;
          }
        }
        bknews.nb_rows = max_y + 1;

        adapt_labgp(first);
        if (first) {
          create_but_scale();
          if (splash_id == 1) {

            var splash_mail = {
              id: "mail-sent",
              but: { list: [{ txt: "Ok", click: function (d) { splash_id = 0; } }] },
              com: { list: [{ txt: "E-mail envoyé !", ftsi: 23 }] }
            };
            splash(splash_mail);

          } else if (splash_id == 2) {

            var splash_quote = {
              id: "quote-sent",
              but: { list: [{ txt: "Ok", click: function (d) { splash_id = 0; } }] },
              com: { list: [{ txt: "Citation envoyée ! (en attente de modération)", ftsi: 23 }] }
            };
            splash(splash_quote);

          }

        }



        fetch_status.ongoing_bknews = false;
        fetch_ended(false);
      }
      show_loader(false);
    },
    error: function (msg) {
      console.log("error");
      show_loader(false);
    }
  });

}

function translate_bknews_from_csv(d) {
  return {
    id: +d.id,
    x_beg: +d.x_beg,
    x_end: +d.x_end,
    y: +d.y,
    is_linked: d.is_linked,
    fill_color: d.fill_color,
    strk_color: d.strk_color,
    txt: d.txt
  };
}



function adapt_labgp(first) {
  var expected_ext_grid_dim = dsp_svg.h - dsp_svg.margin.top - dsp_svg.margin.bot;
  var new_gp_dim;

  if (nbRows > 0) {
    // including bottom garbage
    scale = expected_ext_grid_dim / (nb_minutes_in_grid() + garbage.duration * nbRows);
    // if (new_gp_dim > labgp.hm) {
    //     labgp.height = new_gp_dim;
    // } else {
    //     labgp.height = labgp.hm;
    // }
  } // sinon ?
  dsp_svg.h = svg_height();
  // console.log(dsp_svg.h);
  d3.select("#edt-main").attr("height", dsp_svg.h);

  if (first) {
    window.scroll(0, $("#menu-edt").height());
    expected_ext_grid_dim = dsp_svg.w - dsp_svg.margin.left - dsp_svg.margin.right;
    new_gp_dim = expected_ext_grid_dim / (rootgp_width * week_days.nb_days());
    if (new_gp_dim > labgp.wm) {
      labgp.width = new_gp_dim;
    } else {
      labgp.width = labgp.wm;
    }
    dsp_svg.w = svg_width();
    d3.select("#edt-main").attr("width", dsp_svg.w);
  }

}


/*--------------------
  ------ COURS -------
  --------------------*/
function fetch_constraint(){
  $.ajax({
  type: "GET",
  dataType: 'text',
  url: build_url(url_ttconstraint,context_dept),
  async: true,
  contentType: "application/json",
  success: function(msg){
    data = JSON.parse(msg)
  },
  error: function (msg) {
    console.log("error");
    show_loader(false);
  }
  })
};

function fetch_cours() {
  fetch_status.ongoing_cours_pp = true;
  fetch_status.ongoing_cours_pl = true;

  fetch_status.course_saved = false;

  var garbage_plot;

  ack.more = "";

  var exp_week = wdw_weeks.get_selected();

  cours_bouge = {};

  show_loader(true);

  // Week days
  $.ajax({
    type: "GET",
    dataType: 'text',
    url: build_url(url_weekdays, context_dept, exp_week.as_context()),
    async: true,
    contentType: "application/json",
    success: function(msg, ts, req) {
      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) === 0) {
        week_days = new WeekDays(JSON.parse(msg));
        days_header.mix.days = week_days;
        days_header.fetch_physical_presence() ;
      }
    }
  });

  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    accepts: {
      text: 'application/json'
    },
    url: build_url(
      url_cours_pl,
      context_dept,
      exp_week.as_context(),
      {'work_copy': num_copie}
    ),
    async: true,
    success: function (msg, ts, req) {

      const parsed_msg = JSON.parse(msg);

      go_regen(null);
      go_alarm_pref();

      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {

        tutors.pl = [];
        modules.pl = [];
        salles.pl = [];

        cours_pl = [] ;

        parsed_msg.forEach(function(sched_course) {
          translate_cours_pl_from_json(sched_course, cours_pl);
        });

        fetch_status.ongoing_cours_pl = false;
        fetch_ended(false);
      }
      show_loader(false);
    },
    error: function (msg) {
      console.log("error");
      show_loader(false);
    }
  });



  if (cours_pp.length > 0) {
    garbage_plot = true;
  } else {
    garbage_plot = false;
  }


  show_loader(true);
  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    accepts: {
      text: 'application/json'
    },
    url: build_url(
      url_cours_pp,
      context_dept,
      exp_week.as_context(),
      {'work_copy': num_copie}
    ),
    async: true,
    success: function (msg, ts, req) {
      msg = JSON.parse(msg) ;

      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {

        tutors.pp = [];
        modules.pp = [];
        salles.pp = [];

        // console.log(exp_week,num_copie);

        cours_pp = [] ;
        msg.forEach(function(sched_course) {
          translate_cours_pp_from_json(sched_course, cours_pp);
        });


        go_grid(true);

        fetch_status.ongoing_cours_pp = false;
        fetch_ended(false);
        show_loader(false);
      }
    },
    error: function (msg) {
      console.log("error");
      show_loader(false);
    }
  });

}

function translate_cours_pl_from_json(d, result) { 
  if (modules.pl.indexOf(d.course.module.abbrev) === -1) {
    modules.pl.push(d.course.module.abbrev);
  }
  if (salles.pl.indexOf(d.room) === -1) {
    salles.pl.push(d.room);
  }


  if (department_settings.mode.cosmo==0) {
      // pre-process supplementary tutors
      d.tutors = d.course.supp_tutor.map(function (st) {
        return st.username;
      });
  }
  else{
    d.tutors=[];
  }

  // pre-process colors
  d.color_bg = 'white' ;
  d.color_txt = 'black' ;
  if (department_settings.mode.cosmo !== 1) {
    d.tutors.unshift(d.tutor) ;
    if(d.course.module !== null && d.course.module.display !== null) {
      d.color_bg = d.course.module.display.color_bg ;
      d.color_txt = d.course.module.display.color_txt ;
    }
  } else {
    if(d.tutor !== null && d.tutor.display !== null) {
      d.tutors.unshift(d.tutor.username) ;
      d.color_bg = d.tutor.display.color_bg ;
      d.color_txt = d.tutor.display.color_txt ;
    }
  }

  // TBD: add also supp_tutors
  for(let ip = 0 ; ip < Math.max(d.tutors.length, 1) ; ip++) {
    if (tutors.pl.indexOf(d.tutors[ip]) == -1) {
      tutors.pl.push(d.tutors[ip]) ;
    }
  }

  
  for (let i = 0 ; i < d.course.groups.length ; i++) {
    if (d.course.groups[i].is_structural) {
      let new_course = course_pl_canevas_json_to_obj(d) ;

      new_course.group = translate_gp_name(d.course.groups[i].name);
      new_course.promo = set_promos.indexOf(d.course.groups[i].train_prog);
      new_course.from_transversal = null ;

      result.push(new_course);
    } else {
      let conflicting_groups = groups[set_promos.indexOf(d.course.groups[i].train_prog)]["transversal"][d.course.groups[i].name]["conflicting_groups"];
      console.log(conflicting_groups);
      for (let j=0 ; j < conflicting_groups.length; j++) {
        new_course = course_pl_canevas_json_to_obj(d) ;

        new_course.group = translate_gp_name(conflicting_groups[j].name);
        new_course.promo = set_promos.indexOf(d.course.groups[i].train_prog);
        new_course.from_transversal = translate_gp_name(d.course.groups[i].name);

        result.push(new_course);
      }
    }
  }
}

function course_pl_canevas_json_to_obj(d) {
  var p_m = null;
  console.log(d.course);
  if (d.course.pay_module!=null) {
    p_m = d.course.pay_module.abbrev;
  }
  return {
    id_course: d.course.id,
    mod: d.course.module.abbrev,
    pay_mod: p_m,
    c_type: d.course.type,
    day: d.day,
    start: d.start_time,
    duration: constraints[d.course.type].duration,
    room: d.room,
    room_type: d.course.room_type,
    display: true,
    id_visio: d.room===null?(d.id_visio===null?-1:+d.id_visio):-1,
    graded: d.course.is_graded,
    color_bg: d.color_bg,
    color_txt: d.color_txt,
    tutors: d.tutors
  };
}

function course_pp_canevas_json_to_obj(d) {
  return {
    id_course: d.id,
    mod: d.module.abbrev,
    c_type: d.type.name,
    day: garbage.day,
    start: garbage.start,
    duration: constraints[d.type.name].duration,
    room: null,
    id_visio: -1,
    room_type: d.room_type,
    color_bg: d.module.display.color_bg,
    color_txt: d.module.display.color_txt,
    display: true,
    graded: d.is_graded,
    tutors: d.tutors
  };
}


function translate_cours_pp_from_json(d, result) {
  if (department_settings.mode.cosmo==0) {
    // pre-process supplementary tutors
    d.tutors = d.supp_tutor.map(function(st) {
      return st.username ;
    });
  } else {
    d.tutors = [] ;
  }

  if (d.tutor !== null) {
    d.tutors.unshift(d.tutor) ;
  }

  
  // TBD: add also supp_tutors
  for(let ip = 0 ; ip < Math.max(d.tutors.length, 1) ; ip++) {
    if (tutors.pp.indexOf(d.tutors[ip]) == -1) {
      tutors.pp.push(d.tutors[ip]) ;
    }
  }

  if (modules.pp.indexOf(d.module.abbrev) === -1) {
    modules.pp.push(d.module.abbrev);
  }
  if (salles.pp.indexOf(d.room) === -1) { 
    salles.pp.push(d.room);
  }
  for (let i = 0 ; i < d.groups.length ; i++) {
    if (d.groups[i].is_structural) {
      let new_course = course_pp_canevas_json_to_obj(d) ;
      new_course.group = translate_gp_name(d.groups[i].name) ;
      new_course.promo = set_promos.indexOf(d.groups[i].train_prog) ;
      new_course.from_transversal = null ;
      result.push(new_course);
    } else {
      let conflicting_groups = groups[set_promos.indexOf(d.groups[i].train_prog)]["transversal"][d.groups[i].name]["conflicting_groups"];
      for (let j=0 ; j < conflicting_groups.length; j++) {
        let new_course = course_pp_canevas_json_to_obj(d) ;
        new_course.group = translate_gp_name(conflicting_groups[j].name) ;
        new_course.promo = set_promos.indexOf(d.groups[i].train_prog) ;
        new_course.from_transversal = translate_gp_name(d.groups[i].name) ;
        result.push(new_course);        
      }
    }
  }
}


// insert the given week in the side weeks
function insert_side_week(week, days_, courses_) {
  var found = side_courses.find(function (d) {
    return Week.compare(d, week) == 0;
  });
  if (typeof found === 'undefined') {
    side_courses.push({
      week: week,
      days: days_,
      courses: courses_
    });
  }
}

// insert in week_set the week of index iweek in weeks.init_data if possible
// return true if it hase been inserted
function insert_in_week_set(week_set, iweek) {
  if (iweek < 0 || iweek >= weeks.init_data.length) {
    return false;
  }
  var week = weeks.init_data[iweek].week;
  var year = weeks.init_data[iweek].year;
  var found = week_set.find(function (d) {
    return d.year == year && d.week == week;
  });
  if (typeof found === 'undefined') {
    week_set.push({
      year: year,
      week: week,
    });
    return true;
  }
  return false;
}


// compute which weeks are needed to check the constraints
function which_side_weeks() {
  var week_set = new Weeks();
  var fweeks = wdw_weeks.full_weeks;

  var cur_week_index = wdw_weeks.get_iselected_pure();

  // constraint: 'sleep'
  week_set.add_by_index(fweeks, cur_week_index - 1);
  week_set.add_by_index(fweeks, cur_week_index + 1);

  // constraint: 'monthly'
  // note: load too much if empty weeks (not in weak_year_init)
  // until day 1 of the month of the first day of the week
  var first_day = week_days.day_by_num(0);
  var cur_extremum = first_day.day - 1;
  var iextrem = cur_week_index - 1;
  while (cur_extremum >= 1) {
    week_set.add_by_index(fweeks, iextrem);
    cur_extremum -= 7;
    iextrem -= 1;
  }

  // until final day of the month of the last day of the week
  var last_day = week_days.day_by_num(week_days.day_list.length - 1);
  cur_extremum = last_day.day + week_jump;
  iextrem = cur_week_index + 1;
  while (cur_extremum <= last_day.max_days_in_month()) {
    console.log(iextrem);
    week_set.add_by_index(fweeks, iextrem);
    cur_extremum += 7;
    iextrem += 1;
  }

  return week_set;
}



function side_week_rcv(side_week) {
  return function (msg, ts, req) {


    var side_days = new WeekDays(JSON.parse(req.getResponseHeader('days').replace(/'/g, '"')));

    side_cours_pl = [] ;
    var side_cours_pl = d3.csvParse(
      msg,
      function(d) {
        translate_cours_pl_from_csv(d, side_cours_pl) ;
      }
    );

    insert_side_week(side_week, side_days, side_cours_pl);

  };
}


// fetches courses of the weeks before and after the current week
function fetch_side_weeks() {

  // shunt it for now
  var needed_weeks = [] ; // which_side_weeks();

  for (var i = 0; i < needed_weeks.data.length; i++) {
    console.log(url_cours_pl + needed_weeks.data[i].url() + "/" + 0);
    $.ajax({
      type: "GET", //rest Type
      dataType: 'text',
      url: build_url(
        url_cours_pl,
        context_dept,
        needed_weeks.data[i].as_context(),
        {'work_copy': num_copie}
      ),
      async: true,
      contentType: "text/csv",
      success: side_week_rcv(needed_weeks.data[i]),
      error: function (msg) {
        console.log("error");
      }
    });

  }


}





// Add pseudo-courses that do not appear in the database //
function add_exception_course(cur_week, cur_year, targ_week, targ_year,
  day, slot, group, promo, l1, l2, l3) {
  if (cur_week == targ_week && cur_year == targ_year) {
    cours.push({
      day: day,
      slot: slot,
      group: group,
      promo: set_promos.indexOf(promo),
      id_course: -1,
      no_course: -1,
      mod: l1,
      tutors: [l2],
      room: l3
    });
  }
}



// Pseudo fonction pour des possibles exceptions //
//
// "Passeport Avenir (Bénéficiaires d'une bourse)"
// "--- 13h30 ---"
// "Amphi 1"
// "exception"
// function add_exception(sem_att, an_att, sem_voulue, an_voulu, nom, l1, l2, l3){
//     if(sem_att==sem_voulue && an_att==an_voulu){
// 	var gro = svg.get_dom("dg").append("g")
// 	    .attr("class",nom);

// 	var tlx = 3*(rootgp_width*labgp.width
// 		     + dim_dispo.plot*(dim_dispo.width+dim_dispo.right))
// 	    + groups[0]["P"].x*labgp.width ;
// 	var tlx2 = tlx + .5*groups[0]["P"].width*labgp.width;

// 	var tly = (3*nbPromos + row_gp[0].y)*(labgp.height) ;

// 	gro
// 	    .append("rect")
// 	    .attr("x", tlx  )
// 	    .attr("y", tly )
// 	    .attr("fill","red")
// 	    .attr("width",groups[0]["P"].width*labgp.width)
// 	    .attr("height",labgp.height);

// 	gro.append("text")
// 	    .text(l1)
// 	    .attr("font-weight","bold")
// 	    .attr("x",tlx2 )
// 	    .attr("y",tly + labgp.height/4);
// 	gro.append("text")
// 	    .text(l2)
// 	    .attr("font-weight","bold")
// 	    .attr("x",tlx2 )
// 	    .attr("y",tly + 2*labgp.height/4);
// 	gro.append("text")
// 	    .text(l3)
// 	    .attr("font-weight","bold")
// 	    .attr("x",tlx2 )
// 	    .attr("y",tly + 3*labgp.height/4);

//     } else {
// 	d3.select("."+nom).remove();
//     }
// }


function clean_prof_displayed(light) {

  var tutor_names = tutors.pl;
  for (var i = 0; i < tutors.pp.length; i++) {
    var ind = tutor_names.indexOf(tutors.pp[i]);
    if (ind == -1) {
      tutor_names.push(tutors.pp[i]);
    }
  }

  tutor_names.sort();

  update_selection();

  swap_data(tutor_names, tutors, "tutor");

  // relevant tutors
  tutors.all.forEach(function (t) {
    t.relevant = false;
    if (t.name == user.name) {
      t.relevant = true;
    }
  });

  if (!light) {
    go_selection_popup();
  }

}

function translate_gp_name(gp) {
  /*
  var ret = gp.slice(2);
  if (ret == "") {
      ret = "P";
  }
  return ret;
  */
  return gp;
}



/*--------------------
   ------ ROOMS ------
   --------------------*/

function fetch_room_preferences_unavailability() {
  fetch_room_preferences();
  fetch_room_extra_unavailability();
}

// fetch room preferences
function fetch_room_preferences() {
  fetch_status.ongoing_un_rooms = true;

  var exp_week = wdw_weeks.get_selected() ;

  show_loader(true);
  $.ajax({
    type: "GET", //rest Type
    headers: {Accept: 'text/csv'},
    dataType: 'text',
    url: build_url(url_unavailable_rooms, context_dept, exp_week.as_context()),
    async: true,
    success: function (msg, ts, req) {
      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {
        clean_unavailable_rooms();
        d3.csvParse(msg, translate_unavailable_rooms);
        sort_preferences(unavailable_rooms);
      }
      show_loader(false);
      fetch_status.ongoing_un_rooms = false;
      fetch_ended(false);
    },
    error: function (msg) {
      console.log("error");
      show_loader(false);
    }
  });
}

function translate_unavailable_rooms(d) {
  var i;
  //console.log(d);
  if (Object.keys(unavailable_rooms).indexOf(d.room) == -1) {
    unavailable_rooms[d.room] = {};
    week_days.forEach(function (day) {
      unavailable_rooms[d.room][day.ref] = [];
    });
  }
  unavailable_rooms[d.room][d.day].push({
    start_time: +d.start_time,
    duration: +d.duration
  });
}

// fetch the moments where a room is occupied in another departement
function fetch_room_extra_unavailability() {

  var exp_week = wdw_weeks.get_selected();

  show_loader(true);
  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    url: url_fetch_shared_rooms + exp_week.url(),
    async: true,
    contentType: "text/csv",
    success: function (msg) {
      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {
        extra_pref.rooms = {};
        d3.csvParse(msg, translate_extra_pref_room_from_csv);
        sort_preferences(extra_pref.rooms);
        var shared_rooms = Object.keys(extra_pref.rooms);
        for (i = 0; i < shared_rooms.length; i++) {
          var busy_days = Object.keys(extra_pref.rooms[shared_rooms[i]]);
          for (d = 0; d < busy_days.length; d++) {
            fill_holes(extra_pref.rooms[shared_rooms[i]][busy_days[d]], 1);
          }
        }
      }
      show_loader(false);

    },
    error: function (xhr, error) {
      console.log("error");
      console.log(xhr);
      console.log(error);
      console.log(xhr.responseText);
      show_loader(false);
      // window.location.href = url_login;
      window.location.replace(url_login + "?next=" + url_edt + exp_week.url());
    }
  });
}

function translate_extra_pref_room_from_csv(d) {
  if (Object.keys(extra_pref.rooms).indexOf(d.room) == -1) {
    extra_pref.rooms[d.room] = {};
    for (var i = 0; i < days.length; i++) {
      extra_pref.rooms[d.room][days[i].ref] = [];
    }
  }
  extra_pref.rooms[d.room][d.day].push({
    start_time: +d.start_time,
    duration: +d.duration,
    value: 0
  });
}




/*--------------------
   ------ ALL -------
   --------------------*/

function fetch_all(first, fetch_work_copies) {

  if (is_side_panel_open && fetch_work_copies) {
    fetch_work_copy_numbers(true, first);
    return ;
  }


  fetch_status.done = false;

  if (!fetch_status.course_saved) {
    fetch_status.ongoing_cours_pp = true;
    fetch_status.ongoing_cours_pl = true;
    fetch_status.ongoing_bknews = true;
    fetch_ongoing_colors = true;
  }
  if (!fetch_status.pref_saved &&
    (ckbox["dis-mod"].cked
      || ckbox["edt-mod"].cked)) {
    fetch_status.ongoing_dispos = true;
  }
  if (ckbox["edt-mod"].cked) {
    fetch_status.ongoing_un_rooms = true;
  }

  fetch_version();

  if (!fetch_status.course_saved) {
    fetch_module();
    fetch_tutor();
    fetch_cours();
    fetch_colors();
  }
  if (!fetch_status.pref_saved &&
    (ckbox["dis-mod"].cked
      || ckbox["edt-mod"].cked)) {
    fetch_tutor_preferences();
  }
  if (ckbox["edt-mod"].cked) {
    fetch_tutor_extra_unavailability();
    fetch_room_preferences_unavailability();
    if (department_settings.mode.cosmo) {
      fetch_side_weeks();
    }
  }
  fetch_bknews(first);

}


function fetch_version() {
  var exp_week = wdw_weeks.get_selected();
  let context = {dept: department};
  exp_week.add_to_context(context);

  show_loader(true);
  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    url: build_url(url_week_infos, context),
    async: true,
    success: function (msg) {
      var parsed = JSON.parse(msg);
      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {
        version = parsed.version;
        filled_dispos = parsed.proposed_pref;
        required_dispos = parsed.required_pref;
        go_regen(parsed.regen);
      }

      show_loader(false);
    },
    error: function (msg) {
      console.log("error");
      show_loader(false);
    }
  });

}

function translate_version_from_csv(d) {
  return +d.version;
}


function fetch_ended(light) {
  if (!fetch_status.ongoing_cours_pl &&
    !fetch_status.ongoing_cours_pp &&
    !fetch_status.course_saved) {

    fetch_status.course_saved = true;

    cours = cours_pl.concat(cours_pp);

    var module_names = modules.pl;
    for (var i = 0; i < modules.pp.length; i++) {
      if (module_names.indexOf(modules.pp[i]) == -1) {
        module_names.push(modules.pp[i]);
      }
    }

    module_names.sort();

    update_selection();

    swap_data(module_names, modules, "module");

    update_active();
    update_relevant();

    salles.all = [""].concat(salles.pl);
    for (let i = 0; i < salles.pp.length; i++) {
      if (salles.all.indexOf(salles.pp[i]) == -1) {
        salles.all.push(salles.pp[i]);
      }
    }

    salles.all.sort();

    if (salles.all.indexOf(salles.sel) == -1) {
      salles.sel = "";
    }

    clean_prof_displayed(light);

    //Do not hide groups...
    //hide_idle_groups() ;
    
  }

  if (fetch_status.course_saved &&
    !fetch_status.ongoing_dispos &&
    !fetch_status.ongoing_un_rooms &&
    !fetch_status.ongoing_bknews &&
    !fetch_status.ongoing_colors) {
    ping_colors();
    fetch_status.done = true;
    go_edt(false);

  }
}

function hide_idle_groups() {
  for(let ip = 0 ; ip < set_promos.length ; ip++) {
    let group_names = Object.keys(groups[ip]["structural"]);
    for(let ig = 0 ; ig < group_names.length ; ig ++) {
      const found = cours.find(function(c) {
        return (c.group == groups[ip]["structural"][group_names[ig]].name
                && c.promo == groups[ip]["structural"][group_names[ig]].promo) ;
      }) ;
      if (typeof found === 'undefined') {
        groups[ip]["structural"][group_names[ig]].display = false ;
      }
    }
  }

  for(let itrain_prog = 0 ; itrain_prog < set_promos.length ; itrain_prog++) {
    clean_group_display(root_gp[itrain_prog].gp, itrain_prog);
  }

  are_all_groups_hidden(); // all hidden => all displayed
  check_hidden_groups();
  
  update_all_groups();
  go_gp_buttons();
}


function clean_group_display(group, itrain_prog) {
  let ichild ;
  let propagate_down = false ;
  for (ichild = 0 ; ichild < group.children.length ; ichild++) {
    let child_group = groups[itrain_prog]["structural"][group.children[ichild]];
    if (clean_group_display(child_group, itrain_prog)) {
      group.display = true ;
      propagate_down = true ;
    }
  }
  if (group.display && propagate_down) {
    propagate_display_down(group, true) ;
  }

  return group.display ;
}


// - store old data in old
// - translate fetched into current (keeping display values)
function swap_data(fetched, current, type) {
  current.old = current.all;
  current.all = fetched.map(
    function (m) {
      var em = {};
      em.name = m;
      var oldf = current.old.find(function (mo) {
        return mo.name == m;
      });
      var avail = sel_popup.get_available(type);
      if (typeof avail === 'undefined') {
        em.display = true;
      } else {
        em.display = !(avail.active);
      }
      if (typeof oldf !== 'undefined') {
        em.display = oldf.display;
      }
      return em;
    }
  );
  var panel = sel_popup.panels.find(function (p) {
    return p.type == type;
  });
  if (typeof panel !== 'undefined') {
    panel.list = current.all;
  }
}


/*-----------------
  ------Module-----
  -----------------*/
// Get all the information of the module present in the week and stored him in a dictionary of Module_info
function fetch_module() {
  var exp_week = wdw_weeks.get_selected();
  let context = {dept: department};
  exp_week.add_to_context(context);
  
  show_loader(true);
  $.ajax({
    type: "GET",
    dataType: 'text',
    headers: {Accept: 'text/csv'},
    url: build_url(url_module, context),
    async: true,
    success: function (msg, ts, req) {
      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {
        d3.csvParse(msg, translate_module_from_csv);
      }
      show_loader(false);
    },
    error: function (msg) {
      console.log("error");
      show_loader(false);
    }
  });
}
function translate_module_from_csv(d) { 
  //console.log(d);
  if (Object.keys(modules_info).indexOf(d.abbrev) == -1) {
    modules_info[d.abbrev] = {
      name: d.name,
      url: d.url
    };
  }
}

/*-----------------
  ------Tutor------
  -----------------*/
// Get all the information of the Tutor present in the week and stored him in a dictionary of Tutor_info
function fetch_tutor() {
  var exp_week = wdw_weeks.get_selected();
  let context = {dept: department};
  exp_week.add_to_context(context);

  show_loader(true);
  $.ajax({
    type: "GET",
    headers: {Accept: 'text/csv'},
    dataType: 'text',
    url: build_url(url_tutor, context),
    async: true,
    success: function (msg, ts, req) {
      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(exp_week, sel_week) == 0) {
        d3.csvParse(msg, translate_tutor_from_csv);
      }
      show_loader(false);
    },
    error: function (xhr, status, msg) {
      console.log("error");
      console.log(msg);
      show_loader(false);
    }
  });
}
function translate_tutor_from_csv(d) {
  if (Object.keys(tutors_info).indexOf(d.username) == -1) {
    tutors_info[d.username] = {
      full_name: d.first_name + " " + d.last_name,
      email: d.email
    };
  }
}




/*
Reste :
  x couleur modules
  x display filtre prof
  x weeks (fetch, go_course, go_dispo)
  x base edt (d&d, struct edt, check, display conflits, week pro)
  o base dispos (simple, 0-9, week type)
  o plot par défaut
  x move next week
*/

/*
Fichiers :
-> better.js           -- static
-> better-groupes.json -- static
-> better-cours.csv    -- dynamic
-> better-dispos.json  -- dynamic
-> better-salles.json  --
<-
*/

/*
Checks :
o on a la dispo de tous les profs

*/

/*
https://www.youtube.com/watch?v=XNzKZ7lJRUc

*/





/*

function fetchjson() {
    console.log("in");
    $.ajax({
        type: "GET", //rest Type
        dataType: 'json', //mispelled
        url: url_json,
        async: false,
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            console.log(msg);
	    var data = JSON.parse(msg);
            console.log(data);
            console.log("success");
        },
	error: function(msg) {
	    console.log("error");
	},
	complete: function(msg) {
	    console.log("complete");
	}
    });
    console.log("out");
}

*/


/*
Harmonisations :
- noms groupes
- promo 0-1 ou 1-2
*/
