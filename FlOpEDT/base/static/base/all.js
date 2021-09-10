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

/*-------------------
  ---- VARIABLES ----
  -------------------*/



// {"tot":15,
//  "colors":[]},
// {"tot":16,
//  "colors":[]},
// {"tot":18,
//  "colors":[]},
// {"tot":19,
//  "colors":[]},
// {"tot":20,
//  "colors":[]}





var user = {
  name: logged_usr.name,
  dispos: [],
  dispos_bu: [],
  dispos_type: []
};



dsp_svg.margin = {
  top: 250,     // - TOP BANNER - //
  left: 50,
  right: 110,
  bot: 10,
  but: -200
};
dsp_svg.h = window.innerHeight;
dsp_svg.w = window.innerWidth + dsp_svg.margin.left; //- 20 ;

dsp_svg.cadastre = [
  // menus ground
  ["svg", "meg"],

  // weeks ground
  ["svg", "wg"],
  ["wg", "wg-bg"],
  ["wg", "wg-fg"],

  // selection categories button ground
  ["svg", "catg"],

  // semaine type ground
  ["svg", "stg"],

  // dispos info ground
  ["svg", "dig"],

  // dispos info ground
  ["svg", "pmg"],

  // valider
  ["svg", "vg"],

  // background, middleground, foreground, dragground
  ["svg", "edtg"],
  ["edtg", "edt-bg"],
  ["edtg", "edt-mg"],
  ["edtg", "edt-fig"],
  ["edtg", "edt-fg"],

  // selection ground
  ["svg", "selg"],


  // context menus ground
  ["svg", "cmg"],
  ["cmg", "cmpg"],
  ["cmg", "cmtg"],


  // drag ground
  ["svg", "dg"]
];


svg = new Svg(dsp_svg.layout_tree, false);
svg.create_container();
svg.create_layouts(dsp_svg.cadastre);

wdw_weeks.add_full_weeks(week_year_list);
var week_banner = new WeekBanner(svg, "wg", "wg-fg", "wg-bg", wdw_weeks, dsp_weeks);
week_banner.spawn();

var days_header = new WeekDayHeader(
  svg, "edt-fg", week_days, true, null,
  url_fetch_physical_presence, url_change_physical_presence
);

var hours_header = new HourHeader(svg, "edt-fg", hours);


var labgp = { height: 40, width: 30, tot: 8, height_init: 40, width_init: 30, hm: 40, wm: 15 };

//dim_dispo.height = 2*labgp.height ;



butgp.tly = dsp_svg.margin.but;//-butgp.mar_v-6*butgp.height-80 ;
sel_popup.tly = dsp_svg.margin.but;


modules.x = sel_popup.selx + sel_popup.selx;
modules.y = dsp_svg.margin.top + days_header.mix.gsckd_y() - 40;
modules.width = 170;
modules.height = 0;


salles.x = modules.x - 1.2 * modules.width; //5*butpr.width;
salles.y = modules.y - modules.height;//.6*butpr.height;
salles.width = 150;
salles.height = modules.height;

pref_only = false;

/*-------------------
  ------ BUILD ------
  -------------------*/


file_fetch.groups.callback = function () {

  
  create_structural_groups(this.data);

  create_edt_grid();

  create_alarm_dispos();
  create_val_but();
  create_regen();

  //    go_ack_msg();

  create_bknews();

  go_promo_gp_init();

  fetch_status.course_saved = false;
  fetch_all(true, false);


  fetch_status.groups_ok = true;
  create_grid_data();

  if (nbRows > 1) {
    hours_header.hours.clear() ;
    hours_header.hours.add_times(Object.keys(rev_constraints));
    hours_header.hours.add_times(
      Object.keys(rev_constraints).map(function(r){
        return +r + rev_constraints[r];
      }));
    let t = department_settings.time ;
    hours_header.hours.add_times([
      t.day_start_time,
      t.lunch_break_start_time,
      t.lunch_break_finish_time,
      t.day_finish_time
    ]);
  }

  //need set_promos
  fetch_lunch_constraints();

  //need nbRows
  hours_header.create_indicator();
};



file_fetch.transversal_groups.callback = function () {
  create_transversal_groups(this.data);
}

/*---------------------
  ------ STARTER ------
  ---------------------*/



create_quote();

def_drag();
def_cm_change();

//create_clipweek();



create_menus();

create_selections();

fetch_dispos_type();

fetch_preferred_links();


d3.json(build_url(rooms_fi, context_dept),
  function (d) { main('rooms', d); });

d3.json(build_url(constraints_fi, context_dept),
  function (d) { main('constraints', d); });

d3.json(build_url(groupes_fi, context_dept),
  function (d) { main('groups', d); });
  
/* Il faudrait un jour remplacer groupes par groups! J'ai mis transversal_groupEs par soucis de consistence */  
  
d3.json(build_url(transversal_groupes_fi, context_dept),
  function (d) { main('transversal_groups', d); });


d3.select("body")
  .on("click", function (d) {
    if (splash_hold) {
      splash_hold = false;
      return;
    }
    cancel_cm_adv_preferences();
    cancel_cm_room_tutor_change();
  })
  .on("mouseup", function(d) {
    pref_selection.start = null ;
  });




