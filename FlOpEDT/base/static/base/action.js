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
-------     ACTIONS    -------
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
                 */



/*--------------------------
  ------- PREFERENCES ------
  --------------------------*/

// 
function update_pref_selection(d) {
  // paint-like mode?
  if (!pref_selection.is_paint_mode() || pref_selection.start === null) {
    return ;
  }
  
  let covered_days = week_days.get_days_between(d.day, pref_selection.start.day);
  user.dispos.forEach(function (p) { p.selected = false ; });
  covered_days.forEach(function(day) {
    let start = Math.min(pref_selection.start.start_time, d.start_time) ;
    let end = Math.max(
      pref_selection.start.start_time+pref_selection.start.duration,
      d.start_time + d.duration
    ) ;
    user.dispos.filter(function(p) {
      return p.day == day.ref
        && ! (p.start_time>=end || p.start_time + p.duration <= start) ;
    }).forEach( function(p) {
      p.selected = true ;
    });
  });

  go_pref(true);
}

// apply pref change when simple mode
function apply_change_simple_pref(d) {
  if (pref_only || ckbox["dis-mod"].cked) {
    var sel = pref_selection.choice.data.find(function (dd) {
      return dd.selected;
    });
    if (typeof sel === 'undefined') {
      // normal selection mode
      if (Math.floor(d.value % (par_dispos.nmax / 2)) != 0) {
        d.value = Math.floor(d.value / (par_dispos.nmax / 2)) * par_dispos.nmax / 2;
      }
      d.value = (d.value + par_dispos.nmax / 2) % (3 * par_dispos.nmax / 2);
      if (department_settings.mode.cosmo && d.value == 0) {
        d.value++;
      }
      update_pref_interval(user.name, d.day, d.start_time, d.duration, d.value);
    } else {
      // paint-like selection mode
      let covered_days = week_days.get_days_between(d.day,
                                                    pref_selection.start.day);
      user.dispos.forEach(function (p) { p.selected = false ; });
      covered_days.forEach(function(day) {
        let start = Math.min(pref_selection.start.start_time, d.start_time) ;
        let end = Math.max(
          pref_selection.start.start_time+pref_selection.start.duration,
          d.start_time + d.duration
        ) ;
        update_pref_interval(user.name, day.ref, start, end - start, sel.value);
      });
    }
    go_pref(true);
  }
  pref_selection.start = null ;
}

// change preference selection mode
function apply_pref_mode(d) {
  pref_selection.mode.forEach(function (d) {
    d.selected = false;
  });
  d.selected = true;
  if (d.desc == "nominal") {
    pref_selection.choice.data.forEach(function (d) {
      d.selected = false;
    });
  } else {
    var current_sel = pref_selection.choice.data.find(function (d) {
      return d.selected;
    });
    if (typeof current_sel === 'undefined') {
      pref_selection.choice.data[0].selected = true;
    }
  }
  go_pref_mode();
  go_pref();
}

// 
function apply_pref_mode_choice(d) {
  pref_selection.choice.data.forEach(function (p) {
    p.selected = false;
  });
  d.selected = true;
  pref_selection.mode.forEach(function (m) {
    m.selected = false;
  });
  var sel_mode = pref_selection.mode.find(function (m) {
    return m.desc == "paint";
  });
  sel_mode.selected = true;
  go_pref_mode(false);
  go_pref(true);
}

/*---------------------
  ------- WEEKS -------
  ---------------------*/

// move timeline to the left
function week_left() {
  if (weeks.fdisp > 0) {
    weeks.fdisp -= 1;
    weeks.cur_data.pop();
    weeks.cur_data.unshift(weeks.init_data[weeks.fdisp]);
  }
  go_week_menu(false);
}

// move timeline to the right
function week_right() {
  if (weeks.fdisp + weeks.ndisp + 2 < weeks.init_data.length) {
    weeks.fdisp += 1;
    weeks.cur_data.splice(0, 1);
    weeks.cur_data.push(weeks.init_data[weeks.fdisp + weeks.ndisp + 1]);
  }
  go_week_menu(false);
}


/*----------------------
  -------- GRID --------
  ----------------------*/

/*--------------------
  ------- ROOMS ------
  --------------------*/

// Filters the candidates and keep only the rooms that, during slot
//   -     are not used in the current department
//   -and- are not unavailable (due to room preferences or room bookings)
//   -and- are not used in another department
// Returns a list of the selected rooms
function are_rooms_free(candidates,
                        slot,
                        occupied_rooms) {
  // slot: {'day': day_ref, 'start': min_from_midnight, 'duration': in_min}
  // candidates: list of room names

  if (typeof slot.id_course === "undefined") {
    slot.id_course = -2 ;
  }
  const free_rooms = [] ;

  if (typeof occupied_rooms === "undefined") {
    // find rooms where a course take place
    const concurrent_courses = simultaneous_courses(slot);

    occupied_rooms = [];
    for (let i = 0; i < concurrent_courses.length; i++) {
    // for real rooms
      if (concurrent_courses[i].room != null) {
      busy_rooms = rooms.roomgroups[concurrent_courses[i].room];
        for (j = 0; j < busy_rooms.length; j++) {
          if (occupied_rooms.indexOf(busy_rooms[j]) == -1) {
            occupied_rooms.push(busy_rooms[j]);
          }
        }
      }
    }
  }

  for (let i = 0; i < candidates.length; i++) {
    cur_roomgroup = candidates[i];

    // is a room in the roomgroup occupied?
    is_occupied = false;
    is_available = true;
    j = 0;
    while (!is_occupied && is_available
           && j < rooms.roomgroups[cur_roomgroup].length) {
      cur_room = rooms.roomgroups[cur_roomgroup][j];
      is_occupied = (occupied_rooms.indexOf(cur_room) != -1);
      is_available = (Object.keys(unavailable_rooms).indexOf(cur_room) == -1
                      || no_overlap(unavailable_rooms[cur_room][slot.day],
                                    slot.start, slot.duration));
      j++;
    }

    if (!is_occupied && is_available) {
      // other depts
      if (!Object.keys(extra_pref.rooms).includes(cur_roomgroup)
          || !Object.keys(extra_pref.rooms[cur_roomgroup]).includes(slot.day)
          || get_preference(extra_pref.rooms[cur_roomgroup][slot.day],
                            slot.start, slot.duration) != 0) {
        free_rooms.push(candidates[i]);
      }
    }
  }

  return free_rooms ;
}



// return: true iff a change is needed (i.e. unassigned room or already occupied) (or level>0)
function select_room_change() {
  let level = room_cm_level;
  room_tutor_change.cm_settings = room_cm_settings[level];

  let c = pending.wanted_course;
  room_tutor_change.old_value = c.room;
  room_tutor_change.cur_value = c.room;

  let busy_rooms, cur_roomgroup, cur_room, is_occupied, is_available, proposed_rg, initial_rg;
  let j, i_unav;
  const occupied_rooms = [];

  proposed_rg = [];

  if (level < room_cm_settings.length - 1) {

    // find rooms where a course take place
    const concurrent_courses = simultaneous_courses(c);

    for (let i = 0; i < concurrent_courses.length; i++) {
      // for real rooms
      if (concurrent_courses[i].room != null) {
        busy_rooms = rooms.roomgroups[concurrent_courses[i].room];
        for (j = 0; j < busy_rooms.length; j++) {
          if (occupied_rooms.indexOf(busy_rooms[j]) == -1) {
            occupied_rooms.push(busy_rooms[j]);
          }
        }
      }
    }


    if (level == 0) {
      initial_rg = rooms.roomtypes[c.room_type];
    } else if (level == 1) {
      initial_rg = Object.keys(rooms.roomgroups);
    } else {
      // should not go here
      initial_rg = [];
    }

    if (!is_garbage({ day: c.day, start_time: c.start })) {
      proposed_rg.push.apply(proposed_rg,
                             are_rooms_free(initial_rg, c, occupied_rooms)) ;
    }

  } else {
    proposed_rg = Object.keys(rooms.roomgroups);
  }


  // atomic rooms first, then composed
  var atomic_rooms, composed_rooms, room;
  atomic_rooms = [];
  composed_rooms = [];
  var fake_id = new Date();
  fake_id = fake_id.getMilliseconds() + "-";
  room_tutor_change.proposal = [];

  for (let rg = 0; rg < proposed_rg.length; rg++) {
    room = { fid: fake_id + proposed_rg[rg], content: proposed_rg[rg] };
    if (rooms.roomgroups[room.content].length == 1) {
      atomic_rooms.push(room);
    } else {
      composed_rooms.push(room);
    }
  }
  room_tutor_change.proposal = atomic_rooms.concat(composed_rooms);

  if (level < room_cm_settings.length - 1) {
    room_tutor_change.proposal.push({ fid: fake_id, content: "+" });
  }

  update_change_cm_nlin() ;

  if (level > 0 || c.room == "" ||
    occupied_rooms.indexOf(c.room) != -1) {
    return true;
  } else {
    return false;
  }

}


function confirm_room_change(d) {
  Object.assign(
    pending.wanted_course,
    {room: d.content, id_visio: -1}
  );

  room_tutor_change.proposal = [];
  check_pending_course();
}



/*---------------------
  ------- TUTORS ------
  ---------------------*/

function fetch_all_tutors() {
  if (all_tutors.length == 0) {
    show_loader(true);
    $.ajax({
      type: "GET",
      dataType: 'json',
      url: build_url(url_all_tutors, {dept: department}),
      async: false,
      success: function (data) {
        
        all_tutors = data
          .map(function(d) { return d.username; })
          .filter(function (d) {
            return d > 'A';
          });
        all_tutors.sort();
        show_loader(false);
      },
      error: function (msg) {
        console.log("error");
        show_loader(false);
      }
    });
  }
}

// update number of lines in the context menu
function update_change_cm_nlin() {
  room_tutor_change.cm_settings.nlin = Math.ceil(
    room_tutor_change.proposal.length / room_tutor_change.cm_settings.ncol
  );
}


function select_tutor_module_change() {
  room_tutor_change.cm_settings = tutor_module_cm_settings;

  var c = pending.wanted_course;

  room_tutor_change.old_value = null ;
  if (c.tutors.length > 0) {
    room_tutor_change.old_value = c.tutors[0];
  }
  room_tutor_change.cur_value = room_tutor_change.old_value ;

  let courses_same_module = cours
    .filter(function (oth_c) {
      return oth_c.mod == c.mod;
    }) ;

  let tutor_same_module = [] ;
  for (let ic = 0 ; ic < courses_same_module.length ; ic++) {
    Array.prototype.push.apply(tutor_same_module, courses_same_module[ic].tutors) ;
  }

  // remove duplicate 
  tutor_same_module = tutor_same_module.filter(function (t, i) {
    return tutor_same_module.indexOf(t) == i;
  });

  var fake_id = new Date();
  fake_id = fake_id.getMilliseconds() + "-" + c.id_course;
  room_tutor_change.proposal = [];

  room_tutor_change.proposal = tutor_same_module.map(function (t) {
    return { fid: fake_id, content: t };
  });

  room_tutor_change.proposal.push({ fid: fake_id, content: "+" });

  update_change_cm_nlin() ;

}


function select_tutor_filters_change() {
  room_tutor_change.cm_settings = tutor_filters_cm_settings;

  var chunk_size = tutor_cm_settings.ncol * tutor_cm_settings.nlin - 1;

  room_tutor_change.proposal = [];

  var i = 0; var i_end;
  while (i < all_tutors.length) {
    i_end = i + chunk_size - 1;
    if (i_end >= all_tutors.length) {
      i_end = all_tutors.length - 1;
    }
    room_tutor_change.proposal.push(all_tutors[i]
      + arrow.right
      + all_tutors[i_end]);
    i = i_end + 1;
  }

  var fake_id = new Date();
  fake_id = fake_id.getMilliseconds();
  room_tutor_change.proposal = room_tutor_change.proposal.map(function (t) {
    return { fid: fake_id + t, content: t };
  });

  update_change_cm_nlin() ;

}

// quels salaries afficher 
function select_salarie_change() {
  room_tutor_change.cm_settings = salarie_cm_settings;
  var level = salarie_cm_level;

  var tache = pending.wanted_course;

  if (level == 0) {
    var possibles = new Set();
    cours.forEach(function (c) {
      if (c.group == tache.group) {
        Set.prototype.add.apply(possibles, c.tutors);
      }
    });
    room_tutor_change.proposal = Array.from(possibles);
    room_tutor_change.proposal.push("+");
  } else {
    room_tutor_change.proposal = tutors.all.filter(function (t) {
      return t != "";
    }).map(function (t) {
      return t.name;
    });
  }

  update_change_cm_nlin() ;

  var fake_id = new Date();
  fake_id = fake_id.getMilliseconds() + "-" + tache.id_cours;
  room_tutor_change.proposal = room_tutor_change.proposal.map(function (t) {
    return { fid: fake_id, content: t };
  });

}
// appliquer le changement pour la tache
function confirm_salarie_change(d) {
  confirm_tutor_change(d);
}

function select_tutor_change(f) {
  room_tutor_change.cm_settings = tutor_cm_settings;


  var ends = f.content.split(arrow.right);

  room_tutor_change.proposal = all_tutors.filter(function (t) {
    return t >= ends[0] && t <= ends[1];
  });

  room_tutor_change.proposal.push(arrow.back);

  var fake_id = new Date();
  fake_id = fake_id.getMilliseconds();
  room_tutor_change.proposal = room_tutor_change.proposal.map(function (t) {
    return { fid: fake_id + t, content: t };
  });

}


// unicode →


function confirm_tutor_change(d) {

  pending.wanted_course.tutors.shift();
  pending.wanted_course.tutors.unshift(d.content);

  room_tutor_change.proposal = [];

  check_pending_course();
}





function go_cm_room_tutor_change() {

  var tmp_array = [];
  if (pending.wanted_course != null) {
    tmp_array.push(pending.wanted_course);
  }

  var tut_cm_course_dat = svg.get_dom("cmtg")
    .selectAll(".cm-chg")
    .data(tmp_array,
      function (d) {
        return d.id_course;
      });

  if (room_tutor_change.cm_settings.type !== undefined) {

    var tut_cm_course_g = tut_cm_course_dat
      .enter()
      .append("g")
      .attr("class", "cm-chg")
      .attr("cursor", "pointer");


    tut_cm_course_g
      .append("rect")
      .attr("class", "cm-chg-bg")
      .merge(tut_cm_course_dat.select(".cm-chg-bg"))
      .attr("x", cm_chg_bg_x)
      .attr("y", cm_chg_bg_y)
      .attr("width", cm_chg_bg_width)
      .attr("height", cm_chg_bg_height)
      .attr("fill", "white");
    // .attr("stroke", "darkslategrey")
    // .attr("stroke-width", 2);

    tut_cm_course_g
      .append("text")
      .attr("class", "cm-chg-comm")
      .merge(tut_cm_course_dat.select(".cm-chg-comm"))
      .attr("x", cm_chg_txt_x)
      .attr("y", cm_chg_txt_y)
      .text(cm_chg_txt);
    // .attr("stroke", "darkslategrey")
    // .attr("stroke-width", 2);
  }

  tut_cm_course_dat.exit().remove();



  var tut_cm_room_dat = svg.get_dom("cmtg")
    .selectAll(".cm-chg-rooms")
    .data(room_tutor_change.proposal,
      function (d, i) {
        return d.fid + "-" + i;
      });

  if (room_tutor_change.cm_settings.type !== undefined) {

    var tut_cm_room_g = tut_cm_room_dat
      .enter()
      .append("g")
      .attr("class", "cm-chg-rooms")
      .attr("cursor", "pointer")
      .on("click", room_tutor_change.cm_settings.click);


    tut_cm_room_g
      .append("rect")
      .attr("class", "cm-chg-rec")
    // never updated
    //      .merge(tut_cm_room_dat.select(".cm-chg-rec"))
      .attr("x", cm_chg_but_x)
      .attr("y", cm_chg_but_y)
      .attr("width", cm_chg_but_width)
      .attr("height", cm_chg_but_height)
      .attr("fill", cm_chg_but_fill)
      .attr("stroke", "black")
      .attr("stroke-width", cm_chg_but_stk);

    tut_cm_room_g
      .append("text")
      .attr("class", "cm-chg-bt")
    // never updated
    //     .merge(tut_cm_room_dat.select(".cm-chg-bt"))
      .attr("x", cm_chg_but_txt_x)
      .attr("y", cm_chg_but_txt_y)
      .attr("fill", cm_chg_but_txt_fill)
      .text(cm_chg_but_txt);
    // .attr("stroke", "darkslategrey")
    // .attr("stroke-width", 2);

  }

  tut_cm_room_dat.exit().remove();
}


function remove_panel(p, i) {
  sel_popup.panels.splice(i, 1);
  go_selection_popup();
}

function go_select_tutors() {
  create_static_tutor();
  create_pr_buttons();
}


/*--------------------------
  ------- COURSES ------
  --------------------------*/
function select_course_attributes () {
  room_tutor_change.cm_settings = course_cm_settings;
  room_tutor_change.proposal = [] ;

  let fake_id = new Date();
  fake_id = fake_id.getMilliseconds() + "-";

  let c = pending.wanted_course ;
  let grade_it = {fid: fake_id, content: "Noté"} ;
  if (c.graded) {
    grade_it.content = "Non noté" ;
  }

  room_tutor_change.proposal.push(grade_it) ;

  /* TODO change type of course
  room_tutor_change.proposal.push({
    fid: fake_id,
    content: "Type"
  }) ;
  */

  update_change_cm_nlin() ;

}


/*----------------------
  ------- GROUPS -------
  ----------------------*/


var is_no_hidden_grp = true;

function check_hidden_groups() {
  is_no_hidden_grp = true;
  for (let a in groups) {
    for (let g in groups[a]["structural"]) {
      if (groups[a]["structural"][g].display == false) {
        is_no_hidden_grp = false;
        return;
      }
    }
  }
}

function are_all_groups_hidden() {
  // if all groups are hidden
  // all groups are automatically displayed
  for (let a in groups) {
    for (let g in groups[a]["structural"]) {
      if (groups[a]["structural"][g].display == true) {
        return;
      }
    }
  }
  set_all_groups_display(true);
}

function set_all_groups_display(isDisplayed) {
  for (let a in groups) {
    for (let g in groups[a]["structural"]) {
      groups[a]["structural"][g].display = isDisplayed;
    }
  }
}


// apply changes in the display of group gp
// start == true iff a particular group is chosen by a GET request
// go_button == true iff the group buttons are to be updated
function apply_gp_display(gp, start, go_button) {
  if (fetch_status.done || start) {
    if (is_no_hidden_grp) {
      set_all_groups_display(false);
      gp.display = true;
    } else {
      gp.display = !gp.display;
    }

    propagate_display_up(gp, gp.display);
    propagate_display_down(gp, gp.display);

    are_all_groups_hidden(); // all hidden => all displayed
    check_hidden_groups();

    update_all_groups();
    if (go_button) {
      go_gp_buttons();
    }
  }
  if (fetch_status.done) {
    go_edt();
  }
}


// set to boolean b the attribute display of every group
// that is a descendant of gp, gp included
function propagate_display_down(gp, b) {
  gp.display = b;
  for (let i = 0; i < gp.children.length; i++) {
    propagate_display_down(groups[gp.promo]["structural"][gp.children[i]], b);
  }
}

// set to boolean b the attribute display of every group
// that is an ancestor of gp, gp included
function propagate_display_up(gp, b) {
  gp.display = b;
  if (gp.parent != null) {
    if (b) { // ancestors should be displayed too 
      propagate_display_up(groups[gp.promo]["structural"][gp.parent], true);
    } else { // is there any sibling still displayed?
      var i = 0;
      var hidden_child = true;
      while (hidden_child && i < groups[gp.promo]["structural"][gp.parent].children.length) {
        if (groups[gp.promo]["structural"][groups[gp.promo]["structural"][gp.parent].children[i]].display) {
          hidden_child = false;
        } else {
          i += 1;
        }
      }
      if (hidden_child) {
        propagate_display_up(groups[gp.promo]["structural"][gp.parent], false);
      }
    }
  }
}


/*--------------------
  ------ MENUS -------
  --------------------*/

// apply the updates resulting from a change in a checkbox
function apply_ckbox(dk) {
  if (ckbox[dk].en && fetch_status.done) {

    if (ckbox[dk].cked) {
      ckbox[dk].cked = false;
    } else {
      ckbox[dk].cked = true;
    }

    if (dk == "dis-mod") {

      if (ckbox[dk].cked) {

        if(user.name == '') {
          window.location.href = $('#sign_in').attr('href');
        }
        
        //create_dispos_user_data();
        //ckbox["dis-mod"].disp = true;
        svg.get_dom("stg").attr("visibility", "visible");

        dim_dispo.plot = 1;
        if (rootgp_width != 0) {
          labgp.width *= 1 - (dim_dispo.width + dim_dispo.right) / (rootgp_width * labgp.width);
        }

        fetch_tutor_preferences();

        if (logged_usr.dispo_all_change) {

          // a single tutor was selected
          if (tutors.all.filter(function (t) {
            return t.display;
          }).length == 1) {
            user.name = tutors.all.find(function (t) {
              return t.display;
            }).name;
          }
          // otherwise cancel selection
          else {
            tutors.all.forEach(function (t) {
              t.display = true;
            });
            user.name = logged_usr.name;
          }
        }
      } else {

        // close back lunck break
        let bus = [
          "day_start_time", "day_finish_time",
          "lunch_break_start_time", "lunch_break_finish_time"
        ] ;
        for (let i = 0 ; i < bus.length ; i ++) {
          if (typeof department_settings.time.bu[bus[i]] !== 'undefined') {
            department_settings.time[bus[i]] = department_settings.time.bu[bus[i]] ;
          }
        }
        department_settings.time.bu = {} ;
        
        user.dispos = [];
        //ckbox["dis-mod"].disp = false;
        svg.get_dom("stg").attr("visibility", "hidden");
        dim_dispo.plot = 0;
        if (rootgp_width != 0) {
          labgp.width *= 1 + (dim_dispo.width + dim_dispo.right) / (rootgp_width * labgp.width);
        }
        go_edt(false);
        remove_pref_modes();
      }
    } else if (dk == "edt-mod") {
      if (ckbox[dk].cked) {
        fetch_all_tutors();
        if (total_regen && (logged_usr.rights >> 2) % 2 == 0) {

          ckbox[dk].cked = false;

          var splash_disclaimer = {
            id: "disc-edt-mod",
            but: { list: [{ txt: "Ok", click: function (d) { } }] },
            com: {
              list: [{ txt: "Avis", ftsi: 23 }, { txt: "" },
                { txt: gettext("The schedule shall be fully regenerated (see downside to the right).") },
                { txt: gettext("Just update your availabilities : they will be considered for the next generation.")}]
            }
          };
          splash(splash_disclaimer);

          return;
        }
        edt_but.attr("visibility", "visible");

        fetch_all();

      } else {
        edt_but.attr("visibility", "hidden");
        go_edt(true);
      }
    } else {
      go_edt(true);
    }
    // Fetch data, ask for login, etc.
    // ...

    svg.get_dom("stg")
      .select("[but=st-ap]")
      .attr("cursor", st_but_ptr());



    go_menus();
  }
}



/*-----------------------
   ------ VALIDATE ------
   ----------------------*/

function compute_changes(changes, conc_tutors, gps) {
  var id, change, prof_changed, gp_changed, gp_named, date;

  var cur_course, cb;

  var splash_case, msg;
  var msgRetry = "Corrigez, puis réessayez.";
  var butOK = { list: [{ txt: "Ok", click: function (d) { } }] };


  for (let i = 0; i < Object.keys(cours_bouge).length; i++) {
    id = Object.keys(cours_bouge)[i];
    cur_course = get_course(id);
    cb = cours_bouge[id];
    date = {
      day: cur_course.day,
      start_time: cur_course.start
    };

    if (has_changed(cb, cur_course)) {

      /* Sanity checks */

      // No course has been moved to garbage slots
      if (is_garbage(date)) {
        splash_case = {
          id: "garb-sched",
          but: butOK,
          com: {
            list: [
              { txt: "Vous avez déplacé, puis laissé des cours non placés." },
              { txt: msgRetry }]
          }
        };

        splash(splash_case);
        return false;
      }


      // // Course in unavailable slots for some training programme
      // else if (is_free(date, cur_course.promo)) {

      // 	msg = "Pas de cours pour les ";
      // 	if (set_promos[gp_changed.promo] == 3) {
      // 	    msg += "LP" ;
      // 	} else {
      // 	    msg += set_promos[cur_course.promo] + "A" ;

      // 	}
      // 	msg += " le " + days[cur_course.day].date
      // 	    + " sur le créneau."

      // 	splash_case = {
      // 	    id: "unav-tp",
      // 	    but: butOK,
      // 	    com: {list: [{txt: msg},
      // 			 {txt: msgRetry}]}
      // 	}

      // 	splash(splash_case);
      // 	return false ;
      // } else 


      if (cur_course.room == null && cur_course.id_visio == -1) {
        splash_case = {
          id: "def-room",
          but: butOK,
          com: {
            list: [
              { txt: "Vous n'avez pas attribué de salle à un cours." },
              { txt: "Pour l'instant, le changement n'est pas accepté." },
              { txt: "Merci de chercher et de renseigner une salle disponible." }
            ]
          }
        } ;

        splash(splash_case);
        return false;
      }


      /* Change is accepted now */
      /* Compute who is concerned by the change */

      // add instructor if never seen
      let it ;
      for (it = 0 ; it < cur_course.tutors.length ; it++) {
        if (conc_tutors.indexOf(cur_course.tutors[it]) == -1
            && cur_course.tutors[it] != logged_usr.name
            && cur_course.tutors[it] !== null) {
          conc_tutors.push(cur_course.tutors[it]);
        }
      }
      for (it = 0 ; it < cb.tutors.length ; it++) {
        if (conc_tutors.indexOf(cb.tutors[it]) == -1
            && cb.tutors[it] != logged_usr.name
            && cb.tutors[it] != null) {
          conc_tutors.push(cb.tutors[it]);
        }
      }

      // add group if never seen
      gp_changed = groups[cur_course.promo]["structural"][cur_course.group];
      gp_named = set_promos[gp_changed.promo] + gp_changed.name;
      if (gps.indexOf(gp_named) == -1) {
        gps.push(gp_named);
      }


      // build the communication with django
      var sel_week = wdw_weeks.get_selected();
      change = {
        id: id,
        day: cur_course.day,
        start: cur_course.start,
        graded: cur_course.graded,
        room: cur_course.room,
        tutor: null, 
        id_visio: cur_course.id_visio
      };

      if (cur_course.tutors.length > 0) {
        change.tutor = cur_course.tutors[0] ;
      }

      console.log("change", change);
      changes.push(change);

    }


  }

  console.log(JSON.stringify({
    v: version,
    tab: changes
  }));

  return true;

}




// compute latest finishing time
// independently of the days
function max_finish_time(courses_list) {
  return Math.max.apply(Math, courses_list.map(function (d) {
    return d.start + d.duration;
  }));
}


// compute the earliest starting time
// independently of the days
function min_start_time(courses_list) {
  return Math.min.apply(Math, courses_list.map(function (d) {
    return d.start;
  }));
}


// slack between two sets of courses
function compute_slack(prev_day_courses, next_day_courses) {
  //console.log(prev_day_courses, next_day_courses);
  if (prev_day_courses.length == 0 || next_day_courses == 0) {
    return -1;
  }
  return 24 * 60 + min_start_time(next_day_courses) - max_finish_time(prev_day_courses);
}


// return next day
// day_desc: {iweek: int, ref: string}
function compute_next_day(day_desc) {
  var ret = {
    iweek: day_desc.iweek,
    ref: ''
  };
  if (day_desc.ref == 'su') {
    ret.iweek++ ;
    ret.ref = 'm' ;
  } else {
    ret.ref = day_refs[day_refs.indexOf(day_desc.ref) + 1];
  }
  return ret;
}


// fill date field of a given day
function fill_date(day_desc) {

  //console.log("fill date : IW"+day_desc.iweek+" - "+day_desc.ref);

  day_desc.date = side_courses.find(function (d) {
    return Week.compare(d.week,
      wdw_weeks.full_weeks.data[day_desc.iweek]) == 0;
  }).days.day_by_ref(day_desc.ref).date;
}


// return the courses of tutor tutor on day day_desc
function get_courses(tutor, day_desc) {
  if (day_desc.iweek < 0 || day_desc.iweek >= wdw_weeks.full_weeks.data.length) {
    return [];
  }
  var full_week = side_courses.find(function (d) {
    return Week.compare(d.week,
      wdw_weeks.full_weeks.data[day_desc.iweek]) == 0;
  });
  if (typeof full_week !== 'undefined') {
    return full_week.courses.filter(function (d) {
      return d.day == day_desc.ref && d.tutors.includes(tutor);
    });
  }
  return [];
}


// in [start_day_desc, end_day_desc[
function compute_sleep(tutor, start_day_des, end_day_desc, issues) {
  var cur_day = start_day_des;
  var next_day;

  var cur_courses, next_courses;
  var sleep_time;

  while (cur_day.iweek != end_day_desc.iweek
    || cur_day.ref != end_day_desc.ref) {

    //console.log("day IW" + cur_day.iweek + " - " + cur_day.ref);

    next_day = compute_next_day(cur_day);
    cur_courses = get_courses(tutor, cur_day);
    next_courses = get_courses(tutor, next_day);

    sleep_time = compute_slack(cur_courses, next_courses);
    //console.log(sleep_time);
    if (sleep_time > 0 &&
      sleep_time <= law_constraints.sleep_time) {
      fill_date(cur_day);
      fill_date(next_day);

      issues.push({
        nok_type: 'sleep',
        duration: sleep_time,
        prev: cur_day.date,
        next: next_day.date
      });
    }
    cur_day = next_day;
  }
}


// aggregate working time of a tutor in the week described with its index
// return an array of 7 {duration, month, iweek}
function aggregate_hours(tutor, iweek) {

  //console.log("Aggregate "+ tutor + "IW " + iweek);

  var ret = new Array(7);
  for (let i = 0; i < ret.length; i++) {
    ret[i] = {
      duration: 0, month: 0,
      iweek: iweek
    };
  }

  var week_desc = side_courses.find(function (d) {
    return Week.compare(d.week,
      wdw_weeks.full_weeks.data[iweek]) == 0;
  });
  if (typeof week_desc === 'undefined') {
    return ret;
  }

  for (let i = 0; i < week_desc.days.day_list.length; i++) {
    var dday = week_desc.days.day_list[i];
    ret[day_shifts[dday.ref]].month = dday.month;
  }

  week_desc.courses.filter(function (d) {
    return d.tutors.includes(tutor) ;
  }).forEach(function (d) {
    ret[day_shifts[d.day]].duration += d.duration;
  });
  return ret;
}


function print_agg(service) {
  console.log("Service");
  for (let i = 0; i < service.length; i++) {
    console.log("D" + service[i].duration + " -M" + service[i].month + " -IW"
      + service[i].iweek);
  }
}

// check whether there is 2 free days in service
// append problem infos in issues
function compute_weekend(service, issues) {
  var nb_free_days = service.filter(function (d) {
    return d.duration == 0;
  }).length;
  if (nb_free_days < law_constraints.free_days_per_week) {
    issues.push({
      nok_type: 'weekend',
      nb_free_days: nb_free_days
    });
  }
}


// check whether the service is not too heavy
// append problem infos in issues
function compute_weekly(tutor, service, issues) {
  var working_minutes = 0;
  for (let i = 0; i < service.length; i++) {
    working_minutes += service[i].duration;
  }
  if (Object.keys(working_time).includes(tutor)) {
    if (working_minutes > working_time[tutor] + law_constraints.week) {
      issues.push({
        nok_type: 'weekly',
        duration: working_minutes
      }) ;
    }
  }
}


// build description of a day
function build_day_desc(service, iday) {
  var day_desc = {
    iweek: service[iday].iweek,
    ref: day_refs[iday - Math.floor(iday / 7) * 7]
  };
  fill_date(day_desc);
  return day_desc;
}


// PRECOND: ended by free days 
function compute_tunnels(service, issues) {
  var last_free = -1;
  var consec_busy = 0;
  for (let i = 0; i < service.length; i++) {
    if (service[i].duration == 0) {
      if (consec_busy > law_constraints.max_consec_days) {
        if ((i - 1 > 6 || last_free > 6)
          && (i - 1 < 14 || last_free < 14)) {
          //console.log(service,i-1,last_free);
          var end_day = build_day_desc(service, i - 1);
          var beg_day = build_day_desc(service, last_free + 1);
          issues.push({
            nok_type: 'tunnel',
            begin: beg_day.date,
            end: end_day.date,
            nb_consec: consec_busy
          }) ;
        }
      }
      last_free = i;
      consec_busy = 0;
    } else {
      consec_busy++;
    }
  }
}






/*
Check constraints of a given tutor
  - nok_type: 'sleep',    (date1: string(%DD/MM), date2: string(%DD/MM)) 
                         -> the tutor needs to sleep (11h break)
  - nok_type: 'weekend', -> the tutor needs 2 free days per week
  - nok_type: 'tunnel',  -> the tutor should not work more than 6 days in a row
  - nok_type: 'weekly',  -> no more than working time per week + max_variation.week hours
  - nok_type: 'monthly', -> not excluded from working time per month ± max_variation.month hours
*/
// Check everything even if the constraint was violated before the change
// side_weeks should be fille dwith the current week
function check_constraints_tutor(tutor) {

  var issues = [];

  var tut_courses = cours.filter(function (d) {
    d.tutors.includes(tutor) ;
  });

  var icur_week = wdw_weeks.get_iselected_pure();



  // CARE  COURS PAS PLACÉ
  insert_side_week(wdw_weeks.full_weeks.data[icur_week],
    week_days,
    cours);


  // sleep constraint
  compute_sleep(tutor,
    { iweek: icur_week - 1, ref: 'su' },
    { iweek: icur_week + 1, ref: 'm' },
    issues);

  // weekend constraint
  var tutor_service = aggregate_hours(tutor,
    icur_week);

  //print_agg(tutor_service);

  compute_weekend(tutor_service, issues);


  // weekly working time
  compute_weekly(tutor, tutor_service, issues);


  // tunnel constraint
  var prev_service = aggregate_hours(tutor, icur_week - 1);
  var next_service = aggregate_hours(tutor, icur_week + 1);
  tutor_service = prev_service.concat(tutor_service).concat(next_service);

  tutor_service.push({ duration: 0 });
  compute_tunnels(tutor_service, issues);
  tutor_service = tutor_service.slice(0, -1);

  // weekly working time


  return issues;
}


function min_to_hm_txt(minutes) {
  minutes = Math.round(minutes);
  var h = Math.floor(minutes / 60);
  var m = minutes - h * 60;
  var mt = '';
  if (m != 0) {
    mt = m.toString().padStart(2, '0');
  }
  return h + "h" + mt;
}

function law_issue_to_txt(tutor, issue) {
  var ret;
  switch (issue.nok_type) {
  case 'sleep':
    ret = "Nuit trop courte pour " + tutor + " entre le " + issue.prev + " et le " + issue.next + " : "
      + min_to_hm_txt(issue.duration) + " (min " + min_to_hm_txt(law_constraints.sleep_time) + ")" ;
    break;
  case 'weekend':
    ret = tutor + " a seulement " + issue.nb_free_days + " jour libre dans la semaine (min "
      + law_constraints.free_days_per_week + ")";
    break;
  case 'tunnel':
    ret = tutor + " a " + issue.nb_consec + " jours consécutifs sans repos (max "
      + law_constraints.max_consec_days + ") entre le " + issue.begin
      + " et le " + issue.end;
    break;
  case 'weekly':
    ret = tutor + " travaille " + min_to_hm_txt(issue.duration) + "  cette semaine (max "
      + min_to_hm_txt(working_time[tutor] + law_constraints.week) + ")" ;
    break;
  case 'monthly':
    break;
  }
  return ret;
}



function confirm_law_constraints(changes, conc_tutors, gps) {
  var issues;
  var issues_txt = [];
  for (let i = 0; i < conc_tutors.length; i++) {
    issues = check_constraints_tutor(conc_tutors[i]);
    for (let j = 0; j < issues.length; j++) {
      issues_txt.push({ txt: law_issue_to_txt(conc_tutors[i], issues[j]) });
    }
  }

  if (issues_txt.length == 0) {
    confirm_contact_all(changes, conc_tutors, gps);
  } else {
    var splash_confirm = {
      id: "conf-law",
      but: {
        list: [{
          txt: "Je veux être hors-la-loi",
          click: function (d) {
            confirm_contact_all(changes, conc_tutors, gps);
          }
        },
        {
          txt: "Je vais trouver autre chose",
          click: function (d) { }
        }],
        width: 250
      },
      com: { list: issues_txt }
    } ;

    splash(splash_confirm);
  }

}


function confirm_change() {
  var changes, conc_tutors, gps;
  changes = [];
  conc_tutors = [];
  gps = [];
  var changesOK = compute_changes(changes, conc_tutors, gps);

  if (!changesOK) {
    return;
  }

  if (changes.length == 0) {
    ack.status = 'OK';
    ack.more = "Rien à signaler.";
    go_ack_msg();
  } else {
    if (!department_settings.mode.cosmo) {
      confirm_contact_all(changes, conc_tutors, gps);
    } else {
      confirm_law_constraints(changes, conc_tutors, gps);
    }
  }
}

function confirm_contact_all(changes, conc_tutors, gps) {

  var prof_txt, gp_txt;

  if (logged_usr.is_student == "True") {
    if (conc_tutors.length > 0) {
      prof_txt = "Souhaitez-vous envoyer un mail automatique suggérant la modification du cours à :";
      prof_txt += array_to_msg(conc_tutors);
      prof_txt += " ?";
    } else {
      prof_txt = "Il y quelqu'un·e à contacter ?";
    }

    gp_txt = "Par ailleurs, ce serait bien de prévenir ";
    if (gps.length == 1) {
      gp_txt += "le groupe ";
    } else {
      gp_txt += "les groupes ";
    }
    gp_txt += array_to_msg(gps);
    gp_txt += ".";

    att_txt = "/!\\ Votre nom sera mentionné dans le mail /!\\";
  } else {
    if (conc_tutors.length > 0) {
      prof_txt = "Avez-vous contacté ";
      prof_txt += array_to_msg(conc_tutors);
      prof_txt += " ?";
    } else {
      prof_txt = "Tudo bem ?";
    }

    gp_txt = "(Par ailleurs, ce serait bien de prévenir ";
    if (gps.length == 1) {
      gp_txt += "le groupe ";
    } else {
      gp_txt += "les groupes ";
    }
    gp_txt += array_to_msg(gps);
    gp_txt += ").";
    att_txt = "";
  }

  if (logged_usr.is_student == "True") {
    list_but = {
      list: [
        { txt: "Oui", click: function (d) { send_mail_proposal(changes); } },
        { txt: "Non", click: function (d) { } }
      ]
    };
  } else {
    list_but = {
      list: [
        { txt: "Oui", click: function (d) { send_edt_change(changes); } },
        { txt: "Contacter (email)", click: function (d) { send_mail_proposal(changes); } },
        { txt: "Non", click: function (d) { } }
      ]
    };
  }

  var splash_confirm = {
    id: "conf-cont",
    but: list_but,
    com: {
      list: [
        { txt: prof_txt },
        { txt: gp_txt },
        { txt: att_txt }
      ]
    }
  };

  splash(splash_confirm);
}

function send_mail_proposal(changes) {

  var cur_week = wdw_weeks.get_selected();
  var sent_data = {};
  sent_data['version'] = JSON.stringify(version);
  sent_data['week'] = JSON.stringify(cur_week.week);
  sent_data['year'] = JSON.stringify(cur_week.year);
  sent_data['work_copy'] = JSON.stringify(num_copie);
  sent_data['tab'] = JSON.stringify(changes);

  $.ajax({
    url: url_mail_auto,
    type: 'POST',
    data: sent_data,
    dataType: 'json',
    success: function (msg) {
      console.log("SUCCESSSSSSSSSSSSSSSSSSSSSSSSSS");
      console.log(msg);
      mail_ack(msg);
    },
    error: function (msg) {
      console.log("ERROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOR");
      console.log(msg);
      mail_ack(msg);
    }
  });
}

function mail_ack(msg) {
  var splash_disclaimer = {
    id: "mail-ack",
    but: { list: [{ txt: "Ok.", click: function (d) { } }] },
    com: { list: [] }
  };
  if (msg.status == "OK") {
    splash_disclaimer.com.list[0] = { txt: "Email envoyé !" };
  } else {
    splash_disclaimer.com.list[0] = { txt: "Email non envoyé !" };
    splash_disclaimer.com.list[1] = { txt: msg.more };
  }
  splash(splash_disclaimer);
}



function array_to_msg(a) {
  console.log(a);
  var ret = "";
  for (let i = 0; i < a.length - 2; i++) {
    ret += a[i] + ", ";
  }
  if (a.length > 1) {
    ret += a[a.length - 2] + " et "
      + a[a.length - 1];
  } else {
    ret += a[0];
  }
  return ret;
}



function send_edt_change(changes) {
  var cur_week = wdw_weeks.get_selected();
  var sent_data = {};
  sent_data['version'] = JSON.stringify(version);
  sent_data['week'] = JSON.stringify(cur_week.week);
  sent_data['year'] = JSON.stringify(cur_week.year);
  sent_data['work_copy'] = JSON.stringify(num_copie);
  sent_data['tab'] = JSON.stringify(changes);

  var sel_week = wdw_weeks.get_selected();

  show_loader(true);
  $.ajax({
    url: url_edt_changes,
    type: 'POST',
    //        contentType: 'application/json; charset=utf-8',
    data: sent_data,
    dataType: 'json',
    success: function (msg) {
      edt_change_ack(msg);
      show_loader(false);
    },
    error: function (xhr, ajaxOptions, thrownError) {
      console.log(xhr);
      console.log(ajaxOptions);
      console.log(thrownError);
      edt_change_ack({
        status: 'KO',
        more: 'Pb de communication avec le serveur'
      });
      show_loader(false);
    }
  });
}


//
function compute_pref_changes(changes) {
  var nbDispos = 0;
  var modified_days = [];

  for (let i = 0; i < Object.keys(user.dispos).length; i++) {
    //user.dispos[i].value != user.dispos_bu[i].value	   &&
    if (modified_days.indexOf(user.dispos[i].day) == -1) {
      modified_days.push(user.dispos[i].day);
    }
  }

  for (let i = 0; i < modified_days.length; i++) {
    changes.push({
      day: modified_days[i],
      val_inter: []
    });
  }


  for (i = 0; i < Object.keys(user.dispos).length; i++) {
    cur_pref = user.dispos[i];
    bu_pref = user.dispos_bu[i];
    if (cur_pref.value > 0) {
      nbDispos++;
    }
    if (modified_days.indexOf(cur_pref.day) != -1) {

      changes.filter(function (d) {
        return d.day == cur_pref.day;
      })[0].val_inter.push({
        start_time: cur_pref.start_time,
        duration: cur_pref.duration,
        value: cur_pref.value
      });
    }
  }
  user.dispos_bu = user.dispos.slice(0);

  return nbDispos;
}


function send_dis_change() {
  var nbDispos = 0;

  if (user.dispos_bu.length == 0) {
    ack.list.push({
      'status': 'OK',
      'more': "Rien à signaler."
    });
    go_ack_msg();
    return;
  }

  var changes = [];
  nbDispos = compute_pref_changes(changes);

  // console.log(nbDispos);
  // console.log(changes);
  // console.log(JSON.stringify({create: create, tab: changes}));
  // console.log(JSON.stringify(changes));


  if (changes.length == 0) {
    console.log('no change here');
    ack.list.push({
      'status': 'OK',
      'more': "Rien à signaler."
    });
    go_ack_msg();
  } else {

    var sent_data = {};
    sent_data['changes'] = JSON.stringify(changes);

    var sel_week = wdw_weeks.get_selected();

    show_loader(true);
    $.ajax({
      url: url_user_pref_changes
        + sel_week.url()
        + "/" + user.name,
      type: 'POST',
      //            contentType: 'application/json; charset=utf-8',
      data: sent_data, //JSON.stringify(changes),
      dataType: 'json',
      success: function (msg) {
        show_loader(false);
        ack.list.push({
          'status': 'OK',
          'more': ""
        }) ;
        ack.ongoing = ack.ongoing.filter(function(o){
          return o != 'preference' ;
        });
        go_ack_msg();
        filled_dispos = nbDispos;
        go_alarm_pref();
      },
      error: function (msg) {
        show_loader(false);
        ack.list.push({
          'status': 'KO',
          'more': ""
        }) ;
        ack.ongoing = ack.ongoing.filter(function(o){
          return o != 'preference' ;
        });
        go_ack_msg();
      }
    });
  }


}



function send_pref_pres_change() {
  ack.ongoing = ['preference', 'presence'] ;
  send_dis_change() ;
  days_header.send_change_physical_presence() ;
}


function edt_change_ack(msg) {
  if (msg.status == "OK") {
    version += 1;
    ack.status = "OK";
    ack.more = "";
    cours_bouge = [];
  } else {
    ack.status = 'KO';
    ack.more = msg.more;
    if (ack.more != null && ack.more.startsWith("Version")) {
      ack.more = "Il y a eu une modification concurrente. Rechargez et réessayez.";
    }
    var splash_disclaimer = {
      id: "failed-edt-mod",
      but: { list: [{ txt: "Zut. Ok.", click: function (d) { } }] },
      com: { list: [{ txt: ack.more }] }
    };
    splash(splash_disclaimer);
  }
  // console.log(ack.more);
  go_ack_msg();
}



/*--------------------
   ------ SPLASH ------
  --------------------*/



function clean_splash(class_id) {
  svg.get_dom("dg").select("." + class_id).remove();
  splash_hold = true;
}



function splash(splash_ds) {


  if (splash_ds.bg === undefined) {
    splash_ds.bg = {
      x: 0,
      y: 0,
      width: grid_width(),
      height: grid_height()
    };// + valid.margin_edt + 1.1 * valid.h} ;

  }

  var wp = splash_ds.bg;

  var class_id = "spl_" + splash_ds.id;

  svg.get_dom("dg")
    .select("." + class_id)
    .remove();

  svg.get_dom("dg")
    .append("g")
    .attr("class", class_id)
    .append("rect")
    .attr("x", wp.x)
    .attr("y", wp.y)
    .attr("width", wp.width)
    .attr("height", wp.height)
    .attr("fill", "white");

  var spg = svg.get_dom("dg").select("." + class_id);



  var f;

  var but_par = splash_ds.but;

  if (but_par.slack_y === undefined) {
    but_par.slack_y = valid.h;
  }
  if (but_par.slack_x === undefined) {
    but_par.slack_x = 90;
  }
  if (but_par.width === undefined) {
    but_par.width = valid.w;
  }
  if (but_par.height === undefined) {
    but_par.height = valid.h;
  }


  var but_dat = but_par.list;
  var init_but_x = wp.x + .5 * wp.width
    - .5 * (but_dat.length * but_par.width
      + (but_dat.length - 1) * but_par.slack_x);
  var init_but_y = wp.y + wp.height - but_par.height - but_par.slack_y;
  for (let i = 0; i < but_dat.length; i++) {
    f = but_dat[i].click;
    but_dat[i].x = init_but_x + i * (but_par.width + but_par.slack_x);
    but_dat[i].y = init_but_y;
    but_dat[i].w = but_par.width;
    but_dat[i].h = but_par.height;
  }



  var buts = spg
    .selectAll(".but")
    .data(but_dat)
    .enter()
    .append("g")
    .attr("cursor", "pointer")
    .attr("class", "but")
    .on("click", function (d) { d.click(d); clean_splash(class_id); });


  buts
    .append("rect")
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("x", classic_x)
    .attr("y", classic_y)
    .attr("width", classic_w)
    .attr("height", classic_h)
    .attr("fill", "steelblue")
    .attr("stroke", "black")
    .attr("stroke-width", 2);

  buts
    .append("text")
    .attr("style", function (d) {
      return "text-anchor: middle";
    })
    .attr("x", classic_txt_x)
    .attr("y", classic_txt_y)
    .text(classic_txt);



  var com_par = splash_ds.com;

  if (com_par.x === undefined) {
    com_par.x = .5 * grid_width();
  }
  if (com_par.slack_y === undefined) {
    com_par.slack_y = 50;
  }
  if (com_par.anch === undefined) {
    com_par.anch = "middle";
  }



  var com_dat = com_par.list;
  var init_com_y = wp.y + .5 * (wp.height - but_par.height - 2 * but_par.slack_y)
    - .5 * (com_dat.length * com_par.slack_y);
  for (i = 0; i < com_dat.length; i++) {
    com_dat[i].x = com_par.x;
    com_dat[i].y = init_com_y + i * com_par.slack_y;
    if (com_dat[i].ftsi === undefined) {
      com_dat[i].ftsi = 18;
    }
  }

  // console.log(com_dat);


  var comms = spg
    .selectAll(".comm")
    .data(com_dat)
    .enter();


  comms
    .append("text")
    .attr("class", "comm")
    .attr("font-size", function (d) { return d.ftsi; })
    .attr("text-anchor", function (d) { return d.anch; })
    .attr("x", classic_x)
    .attr("y", classic_y)
    .text(classic_txt);

}








/*--------------------
   ------ STYPE ------
  --------------------*/

function apply_stype() {
  if (ckbox["dis-mod"].cked) {
    user.dispos = new Array(user.dispos_type.length);
    dispos[user.name] = {} ;
    for (let d = 0; d < user.dispos.length; d++) {
      if (typeof dispos[user.name][user.dispos_type[d].day] === 'undefined') {
        dispos[user.name][user.dispos_type[d].day] = [] ;
      }
      dispos[user.name][user.dispos_type[d].day].push({
        start_time:user.dispos_type[d].start_time,
        duration:user.dispos_type[d].duration,
        value:user.dispos_type[d].value});

    }
    create_dispos_user_data();
    
    go_pref(true);
    send_dis_change();
  }
}


/*--------------------
   ------ VISIO -------
   --------------------*/

function gp_training_prog_to_str (c) {
  return set_promos[c.promo] + '-' + c.group ;
}

// user's links for now
function select_pref_links_change() {
  room_tutor_change.cm_settings = pref_links_cm_settings;

  room_tutor_change.proposal = [] ;

  let key, pref_links;
  ["users", "groups"].forEach(function(link_type) {
    switch(link_type) {
    case 'users':
      pref_links = preferred_links.users ;
      //TBD supp_tutor
      key = Object.keys(pref_links)[0];
      if (pending.wanted_course.tutors.length > 0) {
        key = pending.wanted_course.tutors[0] ;
      }
      break;
    case 'groups':
      key = gp_training_prog_to_str(pending.wanted_course) ;
      pref_links = preferred_links.groups ;
      break;
    default:
      console.log('Unknonwn type of link!');
      return ;
    }
    
    if (Object.keys(pref_links).includes(key)) {
      room_tutor_change.proposal =
        room_tutor_change.proposal.concat(
          pref_links[key].map(function(l) {
            l.type = link_type ;
            return l;
          })
        ) ;
      let fake_id = new Date();
      fake_id = fake_id.getMilliseconds();
      room_tutor_change.proposal.forEach(function (t) {
        t.content = t.desc ;
        t.fid = fake_id ;
      });
    }

  });

  if (room_tutor_change.proposal.length == 0) {
    console.log('Pas de lien...');
    if (pending.wanted_course.tutors.length > 0) {
      window.location.href =
        url_change_preferred_links + pending.wanted_course.tutors[0] ;
    }
  }
  
  
  update_change_cm_nlin() ;

}


function confirm_pref_links_change(d) {
  Object.assign(
    pending.wanted_course,
    { id_visio: d.id, room: null }
  );

  room_tutor_change.proposal = [];
  check_pending_course();
}

/*--------------------
   ------ ALL -------
   --------------------*/

// add the initial comfiguration of a course to cours_bouge if
// it has not been moved until now
function add_bouge(pending) {
  if (Object.keys(cours_bouge).indexOf(pending.init_course.id_course.toString()) == -1) {
    cours_bouge[pending.init_course.id_course] = {
      id: pending.init_course.id_course,
      day: pending.init_course.day,
      start: pending.init_course.start,
      graded: pending.init_course.graded,
      room: pending.init_course.room,
      tutors: pending.init_course.tutors.slice(),
      id_visio: pending.init_course.id_visio
    };
    cours.forEach(function(c) {
      if (c.id_course == pending.wanted_course.id_course) {
        c.day = pending.wanted_course.day ;
        c.start = pending.wanted_course.start ;
        c.graded = pending.wanted_course.graded ;
        c.room = pending.wanted_course.room ;
        c.tutors = pending.wanted_course.tutors.slice() ;
        id_visio = pending.wanted_course.id_visio ;
      }
    });
    console.log(cours_bouge[pending.init_course.id_course]);
  }
}

function has_changed(cb, c) {
  let except_tutors = cb.day != c.day
    || cb.start != c.start
    || cb.graded != c.graded
    || cb.room != c.room
    || cb.id_visio != c.id_visio;
  if (except_tutors) {
    return true;
  } else {
    if (cb.tutors.length != c.tutors.length) {
      return true ;
    } else {
      for (let it = 0 ; it < cb.tutors.length ; it++) {
        if (cb.tutors[it] != c.tutors[it]) {
          return true ;
        }
      }
      return false ;
    }
  }
}


function get_course(id) {
  var found = false;
  var i = 0;

  while (i < Object.keys(cours).length && !found) {
    if (cours[i].id_course == id) {
      found = true;
    } else {
      i++;
    }
  }

  if (found) {
    return cours[i];
  } else {
    return null;
  }

}


function compute_cm_room_tutor_direction() {
  var c = pending.wanted_course;
  var cm_start_x, cm_start_y;
  cm_start_x = cours_x(c) + .5 * cours_width(c);
  cm_start_y = cours_y(c) + .5 * cours_height(c);
  if (grid_width() - cm_start_x < cm_start_x) {
    room_tutor_change.posh = 'w';
  } else {
    room_tutor_change.posh = 'e';
  }
  if (grid_height() - cm_start_y < cm_start_y) {
    room_tutor_change.posv = 'n';
  } else {
    room_tutor_change.posv = 's';
  }
}


function find_overlapping_courses(reference_course) {
  let start_time = reference_course["start"];
  let finish_time = reference_course["start"]+reference_course["duration"];
  let reference_group_name = reference_course["group"];
  let reference_train_prog_name = reference_course["promo"];
  let reference_day = reference_course["day"];
  overlapping_courses = [];
  
  for (let i = 0; i<cours.length ; i++) {
    if (cours[i]["group"] == reference_group_name
        && cours[i]["promo"] == reference_train_prog_name
        && cours[i]["day"]==reference_day ){
      let cours_finish_time = cours[i]["start"]+cours[i]["duration"];
      if (cours[i]["start"] < finish_time && cours_finish_time > start_time){
        overlapping_courses.push(cours[i]);
      }
    }
  }
  return overlapping_courses;
}

function show_detailed_courses(cours) {
  remove_details(); 
  var details = svg.get_dom("dg").append("g")
    .attr("id", "course_details");

  let overlapping_courses = find_overlapping_courses(cours);

  var strokeColor;
  var strokeWidth;

  if (is_exam(cours)) {
    strokeColor = "red";
    strokeWidth = 4;
  }
  else {
    strokeColor = "black";
    strokeWidth = 2;
  }

  let room_info = {'txt': cours.room} ;
  if (cours.id_visio > -1) {
    let visio_link = links_by_id[String(cours.id_visio)] ;
    if (typeof visio_link !== 'undefined') {
      room_info.txt = visio_link.desc ;
      room_info.url = visio_link.url ;
    }
  }
  
  let modinfo = {name: '', url: ''} ;
  let tutinfo = {name: '', mail: ''} ;
  if (cours.mod in modules_info){
    modinfo.name = modules_info[cours.mod].name;
    modinfo.url = modules_info[cours.mod].url;
    if (cours.pay_mod!=null){
    modinfo.name += ' (' + cours.pay_mod+ ')';
  }
  } else {
    if (cours.mod == null) {
      modinfo.name = 'Pas de module';
    } else {
      modinfo.name = 'Module inconnu';
    }
  }
  if (cours.tutors.length > 0) {
    let tutor = cours.tutors[0] ;
    if (tutor in tutors_info) {
      tutinfo.name = tutors_info[tutor].full_name;
      tutinfo.mail = tutors_info[tutor].email;
    } else {
      tutinfo.name = 'Prof inconnu·e' ;
    }
  } else {
    tutinfo.name = 'Pas de prof attitré·e';
  }
  
  // TBD supp_tutor
  let tutor = null ;
  if (cours.tutors.length > 0) {
    tutor = cours.tutors[0] ;
  }
  let infos = [
    {
      'txt': modinfo.name,
      'url': modinfo.url
    },
    room_info,
    {'txt': (cours.number?cours.c_type +' n°' + cours.number + " ":"")
     + (cours.comment?cours.comment:"")},
    {'txt': tutinfo.name},
    {
      'txt': tutinfo.mail,
      'url': tutor==null?url_contact:(url_contact + tutor)
    },
  ]; 
  
  if (overlapping_courses.length > 1) {
    infos.push( {'txt':""} );
    infos.push( {'txt':"Cours ayant lieu en même temps:"} );
    infos.push( {'txt':""} );
    
    for (let i=1; i<overlapping_courses.length; i++) {
      infos.push( {'txt':overlapping_courses[i]["mod"] + ' - '
                   + overlapping_courses[i]["from_transversal"] + ' - '
                   + overlapping_courses[i]["prof"] + ' - '
                   + overlapping_courses[i]["start"]/60+"h à "
                   +(overlapping_courses[i]["start"]
                     +overlapping_courses[i]["duration"])/60+"h"} );
      infos.push( {'txt':''});
    }
  }
  
  nb_detailed_infos = infos.length ;

  details
    .append("rect")
    .attr("x", detail_wdw_x(cours))
    .attr("y", detail_wdw_y(cours))
    .attr("width", detail_wdw_width())
    .attr("height", detail_wdw_height())
    .attr("rx", 15)
    .attr("ry", 15)
    .attr("fill", cours.color_bg)
    .attr("stroke", strokeColor)
    .attr("stroke-width", strokeWidth)
    .on("click", remove_details);

  for(let i = 0 ; i < infos.length ; i++) {
    let onto = details ;
    if (typeof infos[i].url !== 'undefined') {
      onto = details
        .append('a')
        .attr("xlink:href", infos[i].url)
        .attr("target", "_blank") 
        .attr("style", "text-decoration:underline") ;
    }
    onto
      .append('text')
      .text(infos[i].txt)
      .attr("fill", cours.color_txt)
      .attr("x", detail_txt_x(cours))
      .attr("y", detail_txt_y(cours, i));
  }
  
}

function remove_details() {
  d3.select("#course_details").remove();
}

function apply_selection_display(choice) {
  if (fetch_status.done) {

    var sel_list = choice.panel.list;

    var concerned = sel_list.find(function (t) {
      return t.name == choice.name;
    });
    if (typeof concerned === 'undefined') {
      console.log("Prof, module ou salle inexistante...");
      return;
    }


    if (choice.panel.type == "tutor"
        && logged_usr.dispo_all_change && ckbox["dis-mod"].cked) {
      // special mode
      tutors.all.forEach(function (t) { t.display = false; });
      concerned.display = true;
      user.name = choice.name;
      create_dispos_user_data();
      go_pref(true);

      
    } else {

      if (concerned.display) {
        // click when displayed
        
        var nb_displayed = sel_list.filter(function (t) {
          return t.display;
        }).length;
        
        if (nb_displayed == sel_list.length) {
          // click when all displayed
          sel_list.forEach(function (t) { t.display = false; });
          concerned.display = true;
          
        } else {
          concerned.display = false;
          nb_displayed--;
          if (nb_displayed == 0) {
            sel_list.forEach(function (t) { t.display = true; });
          }
        }
      } else {
        concerned.display = true;
      }
    }
    update_active();
    update_relevant();
    go_courses();
    go_selection_popup();
  }
}


function apply_selection_display_all(p) {
  var condition = true;
  var sel_list = [];

  if (p.type != "tutor"
    || (fetch_status.done
      && (!logged_usr.dispo_all_change
        || !ckbox["dis-mod"].cked))) {
    p.list.forEach(function (d) {
      d.display = true;
    });
    update_active();
    update_relevant();
    go_selection_buttons();
    go_courses();
  }
}

// discards all filters
function apply_cancel_selections() {

  // classical filters
  var display = function (d) {
    d.display = true;
  };
  for (let di = 0; di < sel_popup.available.length; di++) {
    popup_data(sel_popup.available[di].type)
      .forEach(display);
  }


  // group filters
  var displayed = root_gp.reduce(function (acc, d) {
    var ret = d.gp.display ? 1 : 0;
    return acc + ret;
  }, 0);
  var rgi = 0;
  check_hidden_groups();
  if (!is_no_hidden_grp) {
    while (displayed > 0 && rgi < root_gp.length) {
      var gp = root_gp[rgi].gp;
      if (gp.display) {
        apply_gp_display(gp, false, true);
        displayed--;
      }
      rgi++;
    }
  }

  // remove all panels
  sel_popup.panels = [];

  // update flags and display
  update_active();
  update_relevant();
  go_courses();
  go_selection_popup();

}

// move to another department
function redirect_dept(d) {
  var split_addr = url_edt.split("/");
  // change dept
  split_addr[split_addr.length - 2] = d;
  // clean
  if (split_addr[split_addr.length - 1] == "") {
    split_addr.splice(-1, 1);
  }
  // go to the right week
  var sel_week = wdw_weeks.get_selected();
  split_addr.push(sel_week.year);
  split_addr.push(sel_week.week);
  window.location.href = split_addr.join("/");
}

