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

/* INPUTS

// var user = {nom: string,
// 	    dispos: [],
// 	    dispos_bu: [],
// 	    dispos_type: [],
// 	   };

// var margin = {top: nb, left: nb, right: nb, bot: nb};

// var svg = {height: nb, width: nb};

// var week = nb ;
// var year = nb;

// var labgp = {height: nb, width: nb, tot: nb, height_init: nb, width_init: nb};

// var dim_dispo = {height:2*labgp.height, width: 60, right: 10, plot:0,
// 		 adv_v_margin: 5};

*/
           /*     \
          ----------           
        --------------         
      ------------------       
    ----------------------     
  --------------------------   
------------------------------ 
-------  VAR GLOBALES  -------
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
           \     */



/*--------------------------
  ------- API CONTEXT ------
  --------------------------*/

const context_dept = {dept: department} ;



/*--------------------------
  ------- TIME ------
  --------------------------*/

// days
var week_days = new WeekDays(days);

// for y-axis
var hours = new Hours(department_settings.time);


/*-------------------------
  - CONTEXT MENUS HELPERS -
  -------------------------*/

// remove context menu if click outside
function cancel_cm_adv_preferences() {
  if (ckbox["dis-mod"].cked) {
    if (!context_menu.dispo_hold) {
      data_dispo_adv_cur = [];
      go_cm_advanced_pref(true);
    }
    context_menu.dispo_hold = false;
  }
}

// remove context menu if click outside
function cancel_cm_room_tutor_change() {
  if (ckbox["edt-mod"].cked) {
    if (!context_menu.room_tutor_hold) {
      if (pending.init_course != null) {
        pending.rollback();
        room_tutor_change.proposal = [];
        go_cm_room_tutor_change();
        go_courses(false);
      }
    }
    context_menu.room_tutor_hold = false;
  }
}




/*-----------------------------
   ------ file fetchers -------
  -----------------------------*/

var file_fetch =
{
  groups: { done: false, data: null, callback: null },
  transversal_groups: { done: false, data: null, callback: null }, 
  constraints: { done: false, data: null, callback: null },
  rooms: { done: false, data: null, callback: null }
};

function main(name, data) {
  file_fetch[name].data = data;
  file_fetch[name].done = true;
  // callback all when all received
  if (!Object.keys(file_fetch).some(function(att){
    return !file_fetch[att].done ;
  })) {
    Object.keys(file_fetch).forEach(function(att){
      file_fetch[att].callback() ;
    });
  }
}

file_fetch.rooms.callback = function () {
  rooms = this.data;
  var room_names ;
  room_names = Object.keys(rooms.roomgroups).filter(function(k){
    return rooms.roomgroups[k].length == 1 ;
  });
  room_names.sort(function comp(a, b) { return a.localeCompare(b) ; }) ;
  swap_data(room_names, rooms_sel, "room");
};

file_fetch.constraints.callback = function () {
  constraints = this.data;

  // rev_constraints only used when training programmes on multiple lines
  let i, j, coursetypes, cur_start_time;
  coursetypes = Object.keys(constraints);
  for (i = 0; i < coursetypes.length; i++) {
    for (j = 0; j < constraints[coursetypes[i]].allowed_st.length; j++) {
      cur_start_time = constraints[coursetypes[i]].allowed_st[j].toString();
      if (!Object.keys(rev_constraints).includes(cur_start_time)) {
        rev_constraints[cur_start_time]
          = constraints[coursetypes[i]].duration;
      }
    }
  }
  rev_constraints[garbage.start.toString()] = garbage.duration;


  fetch_status.constraints_ok = true;
  create_grid_data();
};




/*--------------------
   ------ ALL -------
  --------------------*/

// do we have slots
var slot_case = false; //true ;

// horizontal lines where a course may start
var plot_constraint_lines = false ;

// current number of rows
var nbRows = 1;
// last positive number of rows (when filtering by group)
var pos_nbRows = 0;

// maximum number of lab groups among promos
var rootgp_width = 0;
// last positive number of lab groups (when filtering by group)
var pos_rootgp_width = 0;

// opacity of disabled stuffs
var opac = .4;


// status of fetching (cours_pl : cours placés, cours_pp : cours pas placés)
var fetch_status = {
  ongoing_cours_pl: false,
  ongoing_dispos: false,
  ongoing_cours_pp: false,
  ongoing_bknews: false,
  ongoing_un_rooms: false,
  done: false,
  course_saved: false,
  pref_saved: false,
  groups_ok: false,
  constraints_ok: false
};
//cours_ok pas très utile

// Svg 
var svg;

var dsp_svg =
{
  w: 0,
  h: 0,
  margin: {
    top: 0,     // - TOP BANNER - //
    left: 0,
    right: 0,
    bot: 0
  },
  trans: function () {
    return "translate(" + this.margin.left + "," + this.margin.top + ")";
  }
};

/*--------------------------
  ------- PREFERENCES ------
  --------------------------*/

// 2D array of list [tutor_name][day_reference] -> list of intervals)
var dispos = {};
// unavailabilities due to other departments
var extra_pref = {
  tutors: {},
  rooms: {}
};

// parameters for availability
var par_dispos = {
  nmax: 8, // maximum happiness
  adv_red: .7, // width of dd menu
  // compared to dispo cell
  rad_cross: .6, // radius of + circle
  // compared to smiley
  red_cross: .3 // length of + branches
  // compared to smiley
};

// parameters for the smileys
var smiley = {
  tete: 5,
  oeil_x: .35,
  oeil_y: -.35,
  oeil_max: .08,
  oeil_min: .03,
  bouche_x: .5,
  bouche_haut_y: -.1,
  bouche_bas_y: .6,
  sourcil: .4,
  headphone: {
    ear: .5,
    top: 1.02,
    mouth_y: .2,
    mouth_w: 1,
    mouth_h: .4
  },
  init_x: 0,
  init_y: -180,
  max_r: 1,
  mid_o_v: 0xA5 * 100 / 255,
  mid_y_v: 0xE0 * 100 / 255,
  min_v: 0x90 * 100 / 255,
  rect_w: 1.1,
  rect_h: .3
};

// seed array for advanced preferences (smileys)
var data_dispo_adv_init = [];
for (let i = 0; i <= par_dispos.nmax; i++) {
  data_dispo_adv_init.push({
    day: 0,
    start_time: 0,
    duration: 0,
    off: i
  });
}
// current array for advanced preferences (smileys)
var data_dispo_adv_cur = [];

// preference selection mode
var pref_selection = {
  butw: 70,
  buth: 30,
  mary: 5,
  marx: 10,
  choice: {
    data: [],
    w: 25,
    h: 25
  },
  mode: [{
    // click on pref => round robin over default values
    desc: "nominal",
    txt: "Normal",
    selected: true,
  }, {
    // select color, then paint any preference with a click
    desc: "paint",
    txt: "Sélection",
    selected: false,
  }],
  is_paint_mode: function () {
    let p = this.mode.find(function(m){ return m.desc=='paint';});
    if (typeof p === 'undefined') {
      console.log('Something is wrong with paint-like mode.');
    } else {
      return p.selected ;
    }
  },
  // pref when mouse was initialy pressed
  start: null
};
for (let i = 0; i <= par_dispos.nmax; i++) {
  pref_selection.choice.data.push({
    value: i,
    // for smile_trans
    off: -2,
    selected: false
  });
}

// number of required and provided availability slots
var required_dispos = -1;
var filled_dispos = -1;

// display only preferences (for typical week)
var pref_only;

// display parameters for preferences
var dim_dispo = {
  width: 60,
  right: 10,
  // are preferences plotted? 1|0
  plot: 0,
  adv_v_margin: 5
};


/*---------------------
  ------- WEEKS -------
  ---------------------*/

var dsp_weeks = {
  visible_weeks: 13,
  width: 40,
  height: 30,
  x: 0,      // top of week banner
  y: -240,   // "
  rad: 1.2,  // ratio for the radius of prev/next week buttons
  hfac: 0.9, // ratio for week selection ellipse
  wfac: 0.9, // ratio for week selection ellipse
  cont: null, // will be initiated in create_clipweek
};

// weeks in the current sliding window
var wdw_weeks = new WeeksExcerpt(dsp_weeks.visible_weeks);


/*----------------------
  -------- GRID --------
  ----------------------*/

// possible slots when drag'n'drop
// filled in add_slot_grid_data()
var data_slot_grid = [];

// keys on top or at the bottom of the grid representing the name of
// the labgroup
// (one element per labgroup and per day)
var data_grid_scale_gp = [];


// keys to the left representing the name of the row
// non-empty iff slot_case
//(one element per row and per hour)
var data_grid_scale_row = [];

// Garbage parameters
var garbage = {
  start: department_settings.time.day_finish_time,
  duration: 90,
  day: week_days.day_by_num(week_days.nb_days() - 2).ref
};


/*----------------------
  ------- BKNEWS -------
  ----------------------*/

// bknews = breaking news
var bknews = {
  time_height: 60,
  time_margin: 15,
  ratio_margin: .15, // ratio over course height 
  cont: [], // array of bknews contents
  nb_rows: 0, // maximum number of bknews in the same day
};

/*---------------------
  ------- QUOTE -------
  ---------------------*/

var quote = "";


/*----------------------
  ------- GROUPS -------
  ----------------------*/

// 2D data about groups [id_promo]["structural"][group_subname] -> Group
var groups = [];


// access to the root of each promo, and to the groups belonging
// to the same line 
var root_gp = []; // indexed by numpromo
var row_gp = []; // indexed by numrow

// set of promo numbers
var set_promos = [];
// set of promo short description
var set_promos_txt = [];
// set of row numbers
var set_rows = [];

// display parameters for buttons about groups
var butgp = {
  height: 20,
  width: 30,
  tlx: 640,
  mar_v: 10,
  mar_h: 10
};

/*--------------------
  ------ MENUS -------
  --------------------*/
// course and preference modification menus
var menus = {
  x: dsp_weeks.x + 20,
  y: dsp_weeks.y + 25,
  mx: 20,
  dx: 280,
  h: 30,
  sfac: 0.4,
  ifac: 0.7,
  coled: 100,
  colcb: 140
};

// course modification validation button
var edt_but;
// course modification feedback message
var edt_message;

// parameters for each checkbox
var ckbox = [];
// schedule modification
ckbox["edt-mod"] = {
  menu: "edt-mod",
  cked: false,
  txt: gettext("Modify"),
  disp: true,
  en: true
};
// preference modification
ckbox["dis-mod"] = {
  menu: "dis-mod",
  cked: false,
  txt: gettext("Modify"),
  disp: true,
  en: true
};


// for click propagation
var context_menu = {
  dispo_hold: false,
  room_tutor_hold: false
};

var splash_hold = false;

/*--------------------
   ------ MODULES ------
   --------------------*/
// modules (sel: selected, pl:scheduled (PLacé), pp: not scheduled (Pas Placé), all: all modules
var modules = {
  sel: "",
  pl: [],
  pp: [],
  all: [],
  old: []
};

/*--------------------
   ------ ROOMS ------
   --------------------*/
// salles (sel: selected, pl:scheduled (PLacé), pp: not scheduled (Pas Placé), all: all modules
var salles = {
  sel: "",
  pl: [],
  pp: [],
  all: []
};

var rooms;
var rooms_sel = {
  all: [],
  old: []
};

var unavailable_rooms = {};


/*---------------------
   ------ TUTORS ------
   --------------------*/

// tutors (sel: selected, pl:scheduled (PLacé), pp: not scheduled (Pas Placé), all: all modules
var tutors = {
  pp: [],
  pl: [],
  all: [],
  old: []
};

// instructors not blurried
var prof_displayed = [];

// display parameters

// exit button in filter selection panel
var but_exit = {
  side: 20,
  mar_side: 3,
  mar_next: 10
};
// filter selection panel
var sel_popup = {
  type: "",
  x: 640,
  y: -210,
  w: 0,
  h: 0,
  groups_w: 0,
  groups_h: 0,
  selw: 60,
  selh: 30,
  selx: 570,
  sely: -200,
  selmy: 8,
  mar_side: 5,
  tlx: 700,
  available: [],
  get_available: function (t) {
    var ret = this.available.find(function (d) {
      return d.type == t;
    });
    if (typeof ret === 'undefined') {
      console.log("type unknown");
      return;
    } else {
      return ret;
    }
  },
  panels: [], //{type, x, y, w, h, txt}
  but: [],
  active_filter: false
};
if (department_settings.mode.cosmo) {
  sel_popup.available = [{
    type: "group",
    buttxt: gettext('Filters')
  },
  {
    type: "tutor",
    buttxt: gettext('Employees')
  },
  {
    type: "module",
    buttxt: gettext('Posts')
  }];
} else {
  sel_popup.available = [{
    type: "group",
    buttxt: gettext('Groups')
  },
  {
    type: "tutor",
    buttxt: gettext('Teachers')
  },
  {
    type: "module",
    buttxt: gettext('Modules')
  },
  {
    type: "room",
    buttxt: gettext('Rooms')
  }];
}
sel_popup.available.forEach(function (f) {
  f.active = false;
});
sel_popup.but["tutor"] = {
  // selector dimensions
  h: 30,
  w: 70,
  // number of items per line
  perline: 5,
  // margins between selectors
  mar_x: 2,
  mar_y: 4,
};
sel_popup.but["room"] = {
  h: 30,
  w: 80,
  perline: 6,
  mar_x: 2,
  mar_y: 4,
};
sel_popup.but["module"] = {
  h: 30,
  w: 50,
  perline: 3,
  mar_x: 2,
  mar_y: 4,
};
sel_popup.available.forEach(function (panel) {
  panel.x = sel_popup.x;
  panel.y = sel_popup.y;
});

// has any instructor been fetched?
var first_fetch_prof = true;

// all tutors (to propose changes)
var all_tutors = [];

/*--------------------
   ------ SCALE ------
  --------------------*/
// listeners for Horizontal Scaling and Vertical Scaling buttons
var drag_listener_hs, drag_listener_vs;

/*-----------------------
   ------ COURSES -------
  -----------------------*/
// unscheduled courses
var cours_pp = [];
// scheduled courses
var cours_pl = [];
// all courses
var cours = [];

// courses of side weeks
// list of {year:int, week:int, days: list of days, courses: list of courses}
// note: main week is always taken from the server, any other may not and may
//       be outdated
var side_courses = [];


// listener for curses drag and drop 
var dragListener;
var drag_popup;

var cur_over = null;
var slots_over = null;

// helper for the d&d
var drag = {
  sel: [],
  x: 0,
  y: 0,
  init: 0,
  svg: null,
  svg_w: 0,
  svg_h: 0,
  set_selection: function(id_course) {
    this.sel = d3.selectAll(".cours")
      .filter(function(c) {return c.id_course == id_course;});
    this.x = 0 ;
    this.y = 0 ;
  }
};

// course being moved
var pending = {
  init_course: null,
  wanted_course: null,
  linked_courses: null,
  time: null,
  pass: {
    tutor: false,
    room: false,
    core: false
  },
  force: {
    tutor: true,
    room: true
  },
  clean: function () {
    this.init_course = null;
    this.wanted_course = null;
    this.linked_courses = null;
    this.time = null;
  },
  fork_course: function (d) {
    this.wanted_course = d;
    this.linked_courses = cours.filter(function(c){
      return c.id_course == d.id_course ;
    });
    this.update_linked();
    this.init_course = Object.assign({}, d);
    this.init_course.tutors = this.wanted_course.tutors.slice() ;
  },
  update_linked: function() {
    let w = this.wanted_course ;
    this.linked_courses.forEach(function(c){
      c.day =   w.day ;
      c.start = w.start ;
      c.room =  w.room ;
      c.tutors =  w.tutors ;
    });
  },
  prepare_dragndrop: function (d) {
    this.fork_course(d);
    this.pass.tutor = false;
    this.pass.room = false;
    this.pass.core = false;
    this.force.room = true;
    this.force.tutor = true;
  },
  prepare_modif: function (d) {
    this.fork_course(d);
    this.force.room = false;
    this.force.tutor = false;
  },
  rollback: function (t) {
    Object.assign(this.wanted_course, this.init_course);
    this.update_linked();
    this.clean();
  }
};

// stores the courses that has been moved
var cours_bouge = {};

// stores the constraints regarding course types
var constraints;
var rev_constraints = {};

// scale factor for vertical display: time*factor -> y 
var scale = 1;

/*----------------------
  ------- VALIDATE -----
  ----------------------*/

// display parameters
var valid = {
  margin_edt: 50,
  margin_h: 20,
  h: 40,
  w: 210
};

// acknowledgements when availability or courses are changed (ack.edt) ,
// or about the next possible regeneration of the planning (ack.regen)
var ack = {
  more: "",
  // regen infos
  regen: "",
  // for stype
  pref: "",
  status: "OK",
  predefined: {
    KO: gettext('KO'),
    OK: gettext('OK')
  },
  list: [],
  ongoing: []
};



/*--------------------
   ------ STYPE ------
  --------------------*/

// display parameters
var did = {
  h: 60,
  w: 15,
  mh: 5,
  mav: 10,
  tlx: 316,
  tly: -180,
  shift_s: 20
};
did.scale = did.h / (department_settings.time.day_finish_time
  - department_settings.time.lunch_break_finish_time
  + department_settings.time.lunch_break_start_time
  - department_settings.time.day_start_time);
var stbut = {
  w: 104,
  h: 60
};

/*--------------------
   ------ ALL -------
  --------------------*/

// version number of the schedule
var version;

logged_usr.dispo_all_see = false;
logged_usr.dispo_all_change = false;


if ((logged_usr.rights >> 0) % 2 == 1) {
  logged_usr.dispo_all_see = true;
}
if ((logged_usr.rights >> 1) % 2 == 1) {
  logged_usr.dispo_all_change = true;
}

var user = {
  name: logged_usr.name,
  dispos: [],
  dispos_bu: [],
  dispos_type: [],
  dispo_all_see: false,
  dispo_all_change: false
};

// will the week schedule be fully regenerated?
var total_regen = false;


// First context menu when right click on a course
var entry_cm_settings =
{
  type: 'entry',
  w: 100,
  h: 18,
  fs: 10,
  mx: 5,
  my: 3,
  ncol: 1,
  nlin: 2,
  txt_intro: { 'default': gettext('What to change ?') }
};
// list of tutors in the module of the selected course
var tutor_module_cm_settings =
{
  type: 'tutor_module',
  w: 45,
  h: 18,
  fs: 10,
  mx: 5,
  my: 3,
  ncol: 3,
  nlin: 0,
  txt_intro: { 'default': gettext('Module teacher ?') }
};
// all tutors in batches
var tutor_filters_cm_settings =
{
  type: 'tutor_filters',
  w: 120,
  h: 18,
  fs: 10,
  mx: 5,
  my: 3,
  ncol: 1,
  nlin: 0,
  txt_intro: { 'default': gettext('Alphabetical order') }
};
// some tutors
var tutor_cm_settings =
{
  type: 'tutor',
  w: 45,
  h: 18,
  fs: 10,
  mx: 5,
  my: 3,
  ncol: 3,
  nlin: 4,
  txt_intro: { 'default': gettext('Alphabetical order') }
};
var pref_links_cm_settings =
{
  type: 'preferred_links',
  w: 200,
  h: 18,
  fs: 10,
  mx: 5,
  my: 3,
  ncol: 1,
  nlin: 0,
  txt_intro: { 'default': gettext('Virtual classroom link ?') }
};
var pref_link_types_cm_settings =
{
  type: 'preferred_link_types',
  w: 120,
  h: 18,
  fs: 10,
  mx: 5,
  my: 3,
  ncol: 1,
  nlin: 0,
  txt_intro: { 'default': gettext('Relating to who ?') }
};
// rooms
// level=0: the proposed rooms are available and of the same type
//       1: the proposed rooms are available
//       2: all rooms are proposed
var room_cm_level = 0;
var room_cm_settings =
  [{
    type: 'room_available',
    txt_intro: {
      '0': gettext('No room available'),
      '1': gettext('Room available'),
      'default': gettext('Rooms available')
    }
  },
  {
    type: 'room_available_same_type',
    txt_intro: {
       '0': gettext('No room available (any type)'),
      '1': gettext('Room available (any type)'),
      'default': gettext('Rooms available (any type)')
    }
  },
  {
    type: 'room',
    txt_intro: {
      '0': gettext('No room'),
      '1': gettext('Room'),
      'default': gettext('Every rooms')
    }
  }];
for (var l = 0; l < room_cm_settings.length; l++) {
  room_cm_settings[l].w = 45;
  room_cm_settings[l].h = 18;
  room_cm_settings[l].fs = 10;
  room_cm_settings[l].mx = 5;
  room_cm_settings[l].my = 3;
  room_cm_settings[l].ncol = 3;
  room_cm_settings[l].nlin = 0;
}


var salarie_cm_settings = {
  type: 'tutor',
  w: 100,
  h: 18,
  fs: 10,
  mx: 5,
  my: 3,
  ncol: 3,
  nlin: 0,
  txt_intro: {'default':gettext('Who should do it ?')}
};

// level=0: salaries qui ont le même poste dans la semaine
//       1: tous les salaries
var salarie_cm_level = 0;

var course_cm_settings = {
  type: 'course',
  w: 100,
  h: 18,
  fs: 10,
  mx: 5,
  my: 3,
  ncol: 1,
  nlin: 0,
  txt_intro: {'default':gettext('What to change ?')}
};

var room_tutor_change = {
  course: [],    // 1-cell array for d3.js
  proposal: [],
  old_value: "",
  cur_value: "",
  cm_settings: {},
  top: 30,
  posv: 's',
  posh: 'w'
};

var arrow =
{
  right: "→",
  back: "↩"
};


var is_side_panel_open = false;

// for tutor contraints
var law_constraints = {
  max_variation: {
    week: 5 * 60,
    month: 5 * 60
  },
  sleep_time: 11 * 60,
  max_consec_days: 6,
  free_days_per_week: 2
};


// week transitions
var day_refs = ['m', 'tu', 'w', 'th', 'f', 'sa', 'su'];
var week_jump = 7 - (
  day_refs.indexOf(
    days.find(
      function (d) { return d.num == days.length - 1; }
    ).ref)
  - day_refs.indexOf(
    days.find(
      function (d) { return d.num == 0; }
    ).ref
  )
);
var day_shifts = [];
for (let i = 0; i < day_refs.length; i++) {
  day_shifts[day_refs[i]] = i;
}


// tutor working time in minutes
// dictionary tutor_username -> {week: int , month: int}
var working_time = {};

splash_hold = false;

var modules_info = {};
var tutors_info = {};


// rectangle colors
// cosmo mode 1: tutor_username -> {color_bg: color, color_txt: color}
// cosmo mode 2: module_abbrev -> {color_bg: color, color_txt: color}
// tutor mode: module_abbrev -> {color_bg: color, color_txt: color}
var colors = {} ;


var lunch_constraint = {} ;
lunch_constraint['groups'] = {};
lunch_constraint['tutors'] = {};

var preferred_links = {users: {}, groups: {}};
var links_by_id = {};

var nb_detailed_infos ;
