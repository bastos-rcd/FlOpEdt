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
------- TRANSFORMATIONS ------
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
           \     */


/*------------------------
  ----- BKNEWS ----
  ------------------------*/

function bknews_top_y() {
  var t = department_settings.time;
  return nbRows * scale * (t.lunch_break_start_time - t.day_start_time);
}
function bknews_bot_y() {
  return bknews_top_y() + bknews_h();
}
function bknews_h() {
  var t = department_settings.time;
  if (t.lunch_break_finish_time == t.lunch_break_start_time
     && bknews.nb_rows == 0) {
    return 0;
  } else {
    return bknews.nb_rows * bknews_row_height()
      + 2 * bknews.time_margin * scale;
  }
}

function bknews_row_x(d) {
  return (d.x_beg * (rootgp_width * labgp.width
    + dim_dispo.plot * (dim_dispo.width + dim_dispo.right)));
}
function bknews_row_y(d) {
  return bknews_top_y() + bknews.time_margin * scale
    + d.y * bknews.time_height * scale;
}
function bknews_row_fill(d) {
  return d.fill_color;
}
function bknews_row_width(d) {
  return ((d.x_end - d.x_beg) * (rootgp_width * labgp.width
    + dim_dispo.plot * (dim_dispo.width + dim_dispo.right)));
}
function bknews_row_height(d) {
  return bknews.time_height * scale;
}
function bknews_row_txt(d) {
  return d.txt;
}
function bknews_row_txt_x(d) {
  return bknews_row_x(d) + .5 * bknews_row_width(d);
}
function bknews_row_txt_y(d) {
  return bknews_row_y(d) + .5 * bknews_row_height(d);
}
function bknews_row_txt_strk(d) {
  return d.strk_color;
}
function bknews_link(d) {
  return d.is_linked;
}


/*---------------------
  ------- ALL ------
  ---------------------*/

function svg_height() {
  //    return margin.top + ack_reg_y() + 4*margin.bot ;
  return dsp_svg.margin.top + grid_height() + dsp_svg.margin.bot
    + scale * garbage.duration * nbRows;
}

function svg_width() {
  //    return dsp_svg.margin.top + ack_reg_y() + 4*dsp_svg.margin.bot ;
  return dsp_svg.margin.left +
    rootgp_width * week_days.nb_days() * labgp.width + dsp_svg.margin.right;
}


/*---------------------
  ------- DISPOS ------
  ---------------------*/
function dispo_x(d) {
  return week_days.day_by_ref(d.day).num * (rootgp_width * labgp.width +
    dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
    rootgp_width * labgp.width;
}



// -- no slot --
// --  begin  --
// TO BE IMPROVED for multi-line, and lunch break
function dispo_y(d) {
  var t = department_settings.time;
  var ret = (d.start_time - t.day_start_time) * nbRows * scale;
  //	+ row_gp[root_gp[c.promo].row].y * rev_constraints[c.start.toString()] * scale ;
  if (d.start_time >= t.lunch_break_finish_time) {
    ret += bknews_h() - (t.lunch_break_finish_time - t.lunch_break_start_time) * nbRows * scale;
  }
  return ret;
}
// --   end   --
// -- no slot --

function dispo_w(d) {
  return dim_dispo.plot * dim_dispo.width;
}

function dispo_h(d) {
  return nbRows * d.duration * scale;
}

function dispo_fill(d) {
  return smi_fill(d.value);
}

function pref_sel_choice_x(d, i) {
  return 0;
}
function pref_sel_choice_y(d, i) {
  return i * pref_selection.choice.h;
}
function pref_sel_choice_opac() {
  var sel = pref_selection.choice.data.find(function (d) {
    return d.selected;
  });
  if (typeof sel === 'undefined') {
    return opac;
  } else {
    return 1;
  }
}
function pref_sel_choice_stkw(d) {
  if (d.selected) {
    return 4;
  } else {
    return 1;
  }
}



function dispo_short_fill(d) {
  var col = "green";
  if (dispos[user.name][d.day][d.hour] == 4) {
    col = "orange";
  } else if (dispos[user.name][d.day][d.hour] == 0) {
    col = "red";
  }
  return col;
}


function trans_dispo(d) {
  return "matrix(" +
    dim_dispo.plot +
    ",0,0,1," +
    dispo_x(d) +
    "," +
    dispo_y(d) +
    ")";
}


function dispo_more_h(d) {
  return .25 * dispo_h(d);
}

function dispo_more_y(d) {
  return dispo_y(d) + dispo_h(d) - 2*dispo_more_h(d);
}

function dispo_more_x(d) {
  return dispo_x(d) + dispo_w(d) - dispo_more_h(d);
}

function dispo_all_x(d) {
  return dispo_more_x(d) + dispo_more_h(d)
    - par_dispos.adv_red * dispo_w(d);
}

function dispo_all_h(d) {
  return 2 * dim_dispo.adv_v_margin + 2 * smiley.tete;
}

function dispo_all_y(d) {
  var ts = department_settings.time;
  if (d.start_time < ts.lunch_break_start_time) {
    return dispo_more_y(d) + d.off * dispo_all_h(d);
  } else {
    return dispo_more_y(d) - d.off * dispo_all_h(d);
  }
}

function dispo_all_w(d) {
  return par_dispos.adv_red * dispo_w(d);
}


function cross_l_x(d) {
  return cross_m_x(d) - par_dispos.red_cross * smiley.tete;
}

function cross_r_x(d) {
  return cross_m_x(d) + par_dispos.red_cross * smiley.tete;
}

function cross_m_x(d) {
  return dispo_x(d) + dispo_w(d) - 1.7 * par_dispos.rad_cross * smiley.tete;
}

function cross_t_y(d) {
  return cross_m_y(d) - par_dispos.red_cross * smiley.tete;
}

function cross_m_y(d) {
  return dispo_more_y(d) + .5 * dispo_more_h(d);
}

function cross_d_y(d) {
  return cross_m_y(d) + par_dispos.red_cross * smiley.tete;
}


function txt_reqDispos() {
  var ret = "";
  if (required_dispos > 0) {
    ret += gettext("You have to do  ") + min_to_hm_txt(required_dispos) + ".";
  } else if (required_dispos == 0) {
    ret += gettext("No course for you this week.");
  }
  return ret;
}

function txt_filDispos() {
  var ret = "";
  if (required_dispos > 0) {
    ret += gettext("You propose   ") + min_to_hm_txt(filled_dispos) + ". ";
  } else if (required_dispos == 0) {
    //ret += "Pas de problème." // pas de cours => pas de message ;-)
  }
  return ret;
}


function txt_comDispos() {
  var ret = "";
  if (required_dispos > 0) {
    if (filled_dispos >= required_dispos) {
      if (filled_dispos < 2 * required_dispos) {
        ret += gettext("Maybe you should free up more...");
      } else {
        ret += gettext("It seems OK.");
      }
    }
    else {
      ret += gettext("Thank you for adding some.");
    }
  }
  return ret;
}

function pref_opacity(d) {
  return pref_selection.start !== null && d.selected?opac:1;
}

function cursor_pref() {
  if (!ckbox["dis-mod"].cked) {
    return "default" ;
  }
  if (pref_selection.is_paint_mode()) {
    return "crosshair" ;
  } else {
    return "pointer" ;
  }
}

/*---------------------
  ------- SMILEY -------
  ---------------------*/


function availability_content(d) {
  return d.off < 0 ? d.value : d.off ;
}

//ratio content
function rc(d) {
  return availability_content(d) / par_dispos.nmax ;
}


function oeil_r(d) {
  return smiley.tete * (smiley.oeil_min + d * (smiley.oeil_max - smiley.oeil_min));
}

function sourcil_ext_x(d) {
  return smiley.tete * (smiley.oeil_x + d * smiley.sourcil);
}

function sourcil_int_x(d) {
  return smiley.tete * (smiley.oeil_x - (1 - d) * smiley.sourcil);
}

function sourcil_ext_y(d) {
  return smiley.tete * (smiley.oeil_y - (1 - d) * smiley.sourcil);
}

function sourcil_int_y(d) {
  return smiley.tete * (smiley.oeil_y - d * smiley.sourcil);
}

function sourcil_extg_x(d) {
  return -smiley.tete * ((smiley.oeil_x + d * smiley.sourcil));
}

function sourcil_intg_x(d) {
  return -smiley.tete * ((smiley.oeil_x - (1 - d) * smiley.sourcil));
}

function smile(d) {
  return "M" +
    (-smiley.tete * smiley.bouche_x) + " " + smile_coin_y(d) + " Q0 " +
    (smiley.tete * (2 * smiley.bouche_haut_y - smiley.bouche_bas_y +
      3 * d * (smiley.bouche_bas_y - smiley.bouche_haut_y))) + " " +
    (smiley.tete * smiley.bouche_x) + " " + smile_coin_y(d);
}


function smile_coin_y(d) {
  return smiley.tete * (smiley.bouche_bas_y +
    d * (smiley.bouche_haut_y - smiley.bouche_bas_y));
}

function smi_fill(d) {
  // remote teaching
  if (d == 1) {
    return "rgb(0,191,255)" ;
  }
  let val = d / par_dispos.nmax ;
  if (val <= .5) {
    return "rgb(" +
      100 + "%," +
      2 * val * smiley.mid_o_v + "%," +
      0 + "%)";
  } else {
    return "rgb(" +
      200 * (1 - val) + "%," +
      ((smiley.min_v - smiley.mid_y_v) * (-1 + 2 * val) + smiley.mid_y_v) + "%," +
      0 + "%)";
  }
}

function tete_str(d) {
  return d == 0 ? "white" : "black";
}

function eye_str_width(d) {
  return availability_content(d) < 1 ? 0 : 1;
}

function mouth_str_width(d) {
  return availability_content(d) < 2 ? 0 : 1;
}

function brow_str_width(d) {
  let v = availability_content(d) ;
  return v < 2 || v > 4 ? 0 : 1;
}

function interdit_w(d) {
  return d == 0 ? smiley.rect_w * smiley.tete : 0;
}

function smile_trans(d, i) {
  if (d.off == -1) {
    return "translate(" +
      (dispo_x(d) + .5 * dim_dispo.width) + "," +
      (dispo_y(d) + .5 * dispo_h(d)) + ")";
  } else if (d.off == -2) {
    return "translate(" +
      (pref_sel_choice_x(d, i) + .5 * pref_selection.choice.w) + "," +
      (pref_sel_choice_y(d, i) + .5 * pref_selection.choice.h) + ")";
  } else {
    return "translate(" +
      (dispo_x(d) + (1 - .5 * par_dispos.adv_red) * dispo_w(d)) + "," +
      (dispo_all_y(d) + smiley.tete + dim_dispo.adv_v_margin) + ")";
  }
}

function path_hpr() {
  let mid_hp = smiley.tete * smiley.headphone.ear ;
  return "M " + smiley.tete + "," + mid_hp
    + " a " + mid_hp + " " + mid_hp
    + " 0 1 0 " + "0,-" + 2*mid_hp ;
}

function path_hpl() {
  let mid_hp = smiley.tete * smiley.headphone.ear ;
  return "M -" + smiley.tete + "," + mid_hp
    + " a " + mid_hp + " " + mid_hp
    + " 0 1 1 " + "0,-" + 2*mid_hp ;
}

function path_hpt() {
  let mid_hp = smiley.tete * smiley.headphone.ear ;
  return "M -" + smiley.headphone.top*smiley.tete + ",-" + .5*mid_hp
    + " a " + smiley.tete + " " + smiley.tete
    + " 0 1 1 " + 2*smiley.headphone.top*smiley.tete + ",0" ;
}

function hp_stroke_width(d) {
  let v = availability_content(d) ;
  return v == 1 ? 3 : 0 ;
}

function hp_fill(d) {
  let v = availability_content(d) ;
  return v == 1 ? "black" : "none" ;
}

function hp_mouth_w(d) {
  let val = availability_content(d) ;
  return val == 1 ? smiley.headphone.mouth_w * smiley.tete : 0 ;
}

function hp_mouth_sw(d) {
  let val = availability_content(d) ;
  return val == 1 ? 2 : 0 ;
}

/*----------------------
  -------- GRID --------
  ----------------------*/

function gs_fill(d) {
  if (d.display) {
    return d.dispo ? "green" : "red";
  } else {
    return "none";
  }
}

function gs_sc(d) {
  return d.dispo ? "green" : "red";
}


function gscg_x(datum) {
  return datum.day * (rootgp_width * labgp.width +
    dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
    datum.gp.x * labgp.width +
    .5 * labgp.width ;
}

function gscg_y(datum) {
  if (datum.gp.promo == 0 || set_rows.length == 1) {
    return -.25 * labgp.height_init;
  } else {
    // if (datum.day == 3) {
    //     return .5 * grid_height() + .25 * labgp.height_init;
    // }
    return grid_height() + .25 * labgp.height_init;
  }
}

function gscg_txt(datum) {
  if (datum.gp.buttxt !== null) {
    return datum.gp.buttxt;
  } else {
    return datum.gp.name;
  }
}

function gscp_x(datum) {
  return -.7 * labgp.width_init;
}

function gscp_y(d) {
  var t = department_settings.time;
  var ret = (d.start - t.day_start_time) * nbRows * scale
    + row_gp[d.row].y * rev_constraints[d.start.toString()] * scale;
  if (d.start >= t.lunch_break_finish_time) {
    ret += bknews_h() - (t.lunch_break_finish_time - t.lunch_break_start_time) * nbRows * scale;
  }
  return ret + .5 * d.duration * scale;
}

function gscp_txt(d) {
  return d.name;
}



function grid_height() {
  return scale * nb_minutes_in_grid();
}

function nb_minutes_in_grid() {
  var t = department_settings.time;
  var minutes = bknews.nb_rows * bknews.time_height
    + nbRows * (t.lunch_break_start_time - t.day_start_time
      + t.day_finish_time - t.lunch_break_finish_time);
  if (t.lunch_break_finish_time != t.lunch_break_start_time
     || bknews.nb_rows > 0) {
    minutes += 2 * bknews.time_margin;
  }
  return minutes;
}

function scale_from_grid_height(gh) {
  return gh / nb_minutes_in_grid();
}




function grid_width() {
  return (rootgp_width * labgp.width +
    dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) * week_days.nb_days();
}





/*----------------------
  ------- GROUPS -------
  ----------------------*/
function butgp_x(gp) {
  return (gp.bx - root_gp[gp.promo].minx) * butgp.width;
}

function butgp_y(gp) {
  return gp.by * butgp.height;
}

function butgp_width(gp) {
  return gp.bw * butgp.width;
}

function butgp_height(gp) {
  return butgp.height * gp.buth;
}

function butgp_txt_x(gp) {
  return butgp_x(gp) + 0.5 * butgp_width(gp);
}

function butgp_txt_y(gp) {
  return butgp_y(gp) + 0.5 * butgp_height(gp);
}

function butgp_txt(gp) {
  return gp.buttxt;
}

function fill_gp_button(gp) {
  return (is_no_hidden_grp ? "#999999" : (gp.display ? "forestgreen" : "firebrick"));
}

function class_gp_button(gp) {
  return (is_no_hidden_grp ? "inactive" : (gp.display ? "active" : "inactive"));
}

/*--------------------
  ------ MENUS -------
  --------------------*/

function menu_cks_y(dk, i) {
  return menus.h - .5 * menus.h * menus.sfac - 10;
}

function menu_cks_x(dk, i) {
  return menus.dx * i + menus.coled;
}

function menu_ckd_y(dk, i) {
  return menus.h - .5 * menus.h * menus.sfac * menus.ifac - 10;
}

function menu_ckd_x(dk, i) {
  return menus.dx * i + menus.coled + 0.5 * (1 - menus.ifac) * menus.sfac * menus.h;
}



function menu_ckd_fill(dk) {
  var ret = "none";
  if (ckbox[dk].disp &&
    ckbox[dk].cked) {
    if (ckbox[dk].en) {
      ret = "black";
    } else {
      ret = "grey";
    }
  }
  return ret;
}

function menu_ck_txt_x(dk, i) {
  return menus.dx * i + menus.coled + menus.sfac * menus.h + menus.mx;
}

function menu_ck_txt_y(dk, i) {
  return menus.h - 10;
}

function menu_cks_stw(dk) {
  return ckbox[dk].disp ? 2 : 0;
}

function menu_cks_fill(dk) {
  return ckbox[dk].en ? "black" : "grey";
}

function menu_cks_txt(dk) {
  return ckbox[dk].disp ? ckbox[dk].txt : "";
}

function menu_curs(dk) {
  return ckbox[dk].en ? "pointer" : "default";
}


/*--------------------
  ------ PROFS -------
  --------------------*/
function but_sel_x(p, i) {
  return but_sel_type_x(i, p.panel.type);
}
function but_sel_type_x(i, t) {
  return ((i + 1) % sel_popup.but[t].perline)
    * (sel_popup.but[t].w + sel_popup.but[t].mar_x);
}

function but_sel_y(p, i) {
  return but_sel_type_y(i, p.panel.type);
}
function but_sel_type_y(i, t) {
  return Math.floor((i + 1) / sel_popup.but[t].perline)
    * (sel_popup.but[t].h + sel_popup.but[t].mar_y);
}

function but_sel_txt_x(p, i) {
  var t = p.panel.type;
  return but_sel_type_x(i, t) + .5 * sel_popup.but[t].w;
}

function but_sel_txt_y(p, i, j) {
  var t = p.panel.type;
  return but_sel_type_y(i, t) + .5 * sel_popup.but[t].h;
}

function but_sel_class(p) {
  var ret = "select-standard";
  if (typeof p.relevant !== 'undefined' && p.relevant) {
    ret = "select-highlight";
  }
  return ret;
}

function but_open_sel_txt(d) {
  return d.buttxt;
}

/*--------------------
  ------ COURS -------
  --------------------*/
function cours_x(c) {
  return week_days.day_by_ref(c.day).num * (rootgp_width * labgp.width +
    dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
    groups[c.promo]["structural"][c.group].x * labgp.width;
}

function cours_y(c) {
  var t = department_settings.time;
  var ret = (c.start - t.day_start_time) * nbRows * scale
    + row_gp[root_gp[c.promo].row].y * c.duration * scale;
  if (c.start >= t.lunch_break_finish_time) {
    ret += bknews_h() - (t.lunch_break_finish_time - t.lunch_break_start_time) * nbRows * scale;
  }
  return ret;
}

function cours_reverse_y(y) {
  let t = department_settings.time;
  let break_start = (t.lunch_break_start_time - t.day_start_time)
    * (nbRows * scale) ;
  let i = 0 ;
  let break_finish = break_start + bknews_h();

  // nothing during lunch break or outside
  if (y > break_start && y < break_finish
      || y < 0
      || y > grid_height()) {
    return "" ;
  }

  // 1 row: compare with last cut
  if (nbRows == 1) {
    if (y <= break_start) {
      return min_to_hm_txt(t.day_start_time
                           + y/scale);
    } else {
      return min_to_hm_txt(t.lunch_break_finish_time
                     + (y-break_finish)/scale);
    }
  }

  // several rows: based on rev_constraints

  // y coordinate for every constraint start
  let rev_cst_y = Object.keys(rev_constraints).map(function(c) {
    if (c <= t.lunch_break_start_time) {
      return (c - t.day_start_time) * (nbRows * scale) ;
    } else {
      if (c < t.lunch_break_finish_time) {
        console.log("Course during lunch break?");
      } else {
        return (t.lunch_break_start_time - t.day_start_time) * (nbRows * scale)
          + bknews_h()
          + (c - t.lunch_break_finish_time) * (nbRows * scale) ;
      }
    }
  });

  // get last constraint before y
  while (i+1 < rev_cst_y.length
         && rev_cst_y[i+1] < y) {
    i = i+1 ;
  }
  let before_last_slot = Object.keys(rev_constraints)[i];

  // get time since last constraint
  y -= rev_cst_y[i] ;
  while (y > 0) {
    y -= rev_constraints[before_last_slot] * scale ;
  }

  return min_to_hm_txt(+before_last_slot
                       + rev_constraints[before_last_slot]
                       + y / scale );

}

function cours_width(c) {
  var gp = groups[c.promo]["structural"][c.group];
  return (gp.maxx - gp.x) * labgp.width;
}

function cours_height(c) {
  return scale * constraints[c.c_type].duration;
}

function cours_txt_x(c) {
  return cours_x(c) + .5 * cours_width(c);
}
function get_color(c){
  let col = 'white' ;
  if (department_settings.mode.cosmo===1 && c.tutors.length) {
    col = colors[c.tutors[0]] ;
  } else {
    col = colors[c.mod] ;
  }
  return col ;
}
function cours_txt_fill(c) {
  let coco = get_color(c) ;
  return (typeof coco === 'undefined')?"black":coco.color_txt;
}
function cours_fill(c) {
  let coco = get_color(c) ;
  return (typeof coco === 'undefined')?"white":coco.color_bg;
}
function is_exam(c) {
  return c.graded;
}

function cours_txt_weight(c) {
  return is_exam(c) ? "bold" : "normal";
}
function cours_txt_size(c) {
  return is_exam(c) ? 14 : 10;
}

function cours_txt_top_y(c) {
  return cours_y(c) + .25 * cours_height(c);
}
function cours_txt_top_txt(c) {
  var ret = c.pay_mod? c.mod+" ("+c.pay_mod+")": c.mod;
  return ret;
}
function cours_txt_mid_y(c) {
  return cours_y(c) + .5 * cours_height(c);
}
function cours_txt_mid_txt(c) {
  return c.tutors.join(',');
}
function cours_txt_bot_y(c) {
  return cours_y(c) + .75 * cours_height(c);
}
function cours_txt_bot_txt(c) {
  if (c.room !== null && c.id_visio != -1) {
    //console.log(c, 'Both on site and remote?');
    1;
  } else {
    if (c.id_visio > -1) {
      return 'Visio' ;
    } else {
      return c.room ;
    }
  }
}
function cours_opac(c) {
  return (c.display || !sel_popup.active_filter) ? 1 : opac;
}
function cours_stk(c) {
  return (c.display && sel_popup.active_filter) ? "black" : "none";
}

/*--------------------
  ------ ROOMS -------
  --------------------*/

function cm_chg_bg_width() {
  return room_tutor_change.cm_settings.mx * (room_tutor_change.cm_settings.ncol + 1)
    + room_tutor_change.cm_settings.w * room_tutor_change.cm_settings.ncol;
}
function cm_chg_bg_height() {
  return room_tutor_change.cm_settings.my * (room_tutor_change.cm_settings.nlin + 1)
    + room_tutor_change.cm_settings.h * room_tutor_change.cm_settings.nlin
    + room_tutor_change.top;
}

function cm_chg_bg_x() {
  var c = pending.wanted_course;
  if (room_tutor_change.posh == 'w') {
    return cours_x(c) + .5 * cours_width(c) - cm_chg_bg_width();
  } else {
    return cours_x(c) + .5 * cours_width(c);
  }
}
function cm_chg_bg_y() {
  var c = pending.wanted_course;
  if (room_tutor_change.posv == 's') {
    return cours_y(c) + .5 * cours_height(c);
  } else {
    return cours_y(c) + .5 * cours_height(c) - cm_chg_bg_height();
  }
}

///////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////

function detail_wdw_width() {
  return .25 * grid_width() ;
}
function detail_wdw_height() {
  return .3 * grid_height() ;
}
function detail_wdw_x(cours) {
  let ret = cours_x(cours) + .5 * cours_width(cours) ;
  if (cours_x(cours) > .5 * grid_width()) {
    ret -=  detail_wdw_width();
  }
  return ret ;
}
function detail_wdw_y(cours) {
  let ret = cours_y(cours) + .5 * cours_height(cours) ;
  if (cours_y(cours) > .5 * grid_height()) {
    ret -= detail_wdw_height();
  }
  return ret ;
}
function detail_txt_y(cours, i_info) {
  return detail_wdw_y(cours)
    + (i_info + 1) * detail_wdw_height() / (nb_detailed_infos + 1) ;
}
function detail_txt_x(cours) {
  return detail_wdw_x(cours) + .5 * detail_wdw_width() ;
}



///////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////

function cm_chg_txt_x() {
  return cm_chg_bg_x() + .5 * cm_chg_bg_width();
}
function cm_chg_txt_y() {
  return cm_chg_bg_y() + .5 * room_tutor_change.top;
}
function cm_chg_txt() {
  if (Object
    .keys(room_tutor_change.cm_settings.txt_intro)
    .indexOf(room_tutor_change.proposal.length.toString())
    != -1) {
    return room_tutor_change.cm_settings.txt_intro[room_tutor_change.proposal.length.toString()];
  } else {
    return room_tutor_change.cm_settings.txt_intro['default'];
  }
}


function cm_chg_but_width() {
  return room_tutor_change.cm_settings.w;
}
function cm_chg_but_height() {
  return room_tutor_change.cm_settings.h;
}

function cm_chg_but_x(d, i) {
  var c = i % room_tutor_change.cm_settings.ncol;
  var ret = cm_chg_bg_x() + room_tutor_change.cm_settings.mx
    + (room_tutor_change.cm_settings.mx + cm_chg_but_width(d, i)) * c;
  return ret;
}
function cm_chg_but_y(d, i) {
  var l = Math.floor(i / room_tutor_change.cm_settings.ncol);
  return cm_chg_bg_y() + room_tutor_change.top + room_tutor_change.cm_settings.my
    + (room_tutor_change.cm_settings.my + cm_chg_but_height(d, i)) * l;
}

function cm_chg_but_txt_x(d, i) {
  return cm_chg_but_x(d, i) + .5 * cm_chg_but_width(d, i);
}
function cm_chg_but_txt_y(d, i) {
  return cm_chg_but_y(d, i) + .5 * cm_chg_but_height(d, i);
}
function cm_chg_but_txt(d, i) {
  return d.content;
}
function cm_chg_but_stk(d) {
  if (d.content == room_tutor_change.cur_value) {
    return 3;
  } else {
    return 0;
  }
}

function cm_chg_but_pref(d) {
  var cur_dispo;
  var cur_course = pending.wanted_course;
  if (room_tutor_change.cm_settings.type == 'tutor_module'
    || room_tutor_change.cm_settings.type == 'tutor') {
    cur_dispo = find_in_pref(dispos, d.content, cur_course);
    if (cur_dispo == -1 || cur_dispo === undefined) {
      cur_dispo = 0;
    }
    if (cur_dispo > 0) {
      let extra_dispo = find_in_pref(extra_pref.tutors, d.content, cur_course);
      if (extra_dispo == 0) {
        cur_dispo = 0;
      }
    }
  } else if (room_tutor_change.cm_settings.type == 'room') {
    if (are_rooms_free([d.content], cur_course).length > 0) {
      cur_dispo = par_dispos.nmax ;
    } else {
      cur_dispo = 0 ;
    }
  }
  return cur_dispo;
}

function cm_chg_but_fill(d) {
  var ret = "steelblue";
  if (["+", arrow.right, arrow.back].includes(d.content)) {
    ret = "steelblue";
  } else if (['tutor_module', 'tutor', 'room'].includes(room_tutor_change.cm_settings.type)) {
    ret = smi_fill(cm_chg_but_pref(d));
  } else if (room_tutor_change.cm_settings.type == "preferred_links") {
    ret = visio_btn_fill(d);
  }
  return ret;
}

function visio_btn_fill(d) {
  let ret = "steelblue";
  if (d.type == "users") {
    ret = "green";
  }
  return ret ;
}

function cm_chg_but_txt_fill(d) {
  var ret = "black";
  if (d.content == room_tutor_change.old_value) {
    ret = "black";
  } else if (["+", arrow.right, arrow.back].includes(d.content)) {
    ret = "black";
  } else if (['tutor_module', 'tutor', 'room'].includes(room_tutor_change.cm_settings.type)) {
    var cur_dispo = cm_chg_but_pref(d);
    if (cur_dispo == 0) {
      ret = "white";
    }
  }
  return ret;
}


/*--------------------
   ------ SCALE -------
  --------------------*/

function but_sca_h_mid_x() {
  return grid_width();
}

function but_sca_h_x() {
  return but_sca_h_mid_x();
}

function but_sca_h_y() {
  return .5 * grid_height() - .5 * but_sca_long();
}

function but_sca_thick() {
  return .5 * labgp.width_init;
}

function but_sca_long() {
  return 1.2 * labgp.height_init;
}

function but_sca_v_x() {
  return .5 * but_sca_h_mid_x() - .5 * but_sca_long();
}

function but_sca_v_y() {
  return grid_height();
}

function but_sca_tri_h(add) {
  var midx, midy, thick, lon;
  midx = but_sca_h_mid_x();
  midy = .5 * grid_height();
  thick = but_sca_thick();
  lon = but_sca_long();
  return "M" +
    (add + midx + .3 * thick) + " " +
    (midy - .2 * lon) + " L" +
    (add + midx + .7 * thick) + " " +
    (midy) + " L" +
    (add + midx + .3 * thick) + " " +
    (midy + .2 * lon) + " Z";
}

function but_sca_tri_v(add) {
  var midx, midy, thick, lon;
  midx = .5 * but_sca_h_mid_x();
  midy = grid_height();
  thick = but_sca_thick();
  lon = but_sca_long();

  return "M" +
    (midx + .2 * lon) + " " +
    (add + midy + .3 * thick) + " L" +
    (midx) + " " +
    (add + midy + .7 * thick) + " L" +
    (midx - .2 * lon) + " " +
    (add + midy + .3 * thick) + " Z";
}



/*--------------------
   ------ STYPE ------
  --------------------*/
function dispot_x(d) {
  return week_days.day_by_ref(d.day).num * (did.w + did.mh);
}

function dispot_y(d) {
  var ts = department_settings.time;
  var ret = 1.25 * valid.h
    + (d.start_time - ts.day_start_time) * did.scale;
  if (d.start_time >= ts.lunch_break_finish_time) {
    ret -= (ts.lunch_break_finish_time
      - ts.lunch_break_start_time)
      * did.scale;
  }
  return ret;
}

function dispot_w(d) {
  return did.w;
}

function dispot_h(d) {
  return d.duration * did.scale;
}

function dispot_more_h(d) {
  return did.shift_s * did.scale;
}

function dispot_more_y(d) {
  return dispot_y(d) + dispot_h(d) - dispot_more_h(d);
}

function dispot_more_x(d) {
  return dispot_x(d) + dispot_w(d) - dispot_more_h(d);
}

function dispot_all_x(d) {
  return dispot_more_x(d) + dispot_more_h(d) -
    par_dispos.adv_red * dispot_w(d);
}

function dispot_all_h(d) {
  return 2 * did.mav + 2 * smiley.tete;
}

function dispot_all_y(d) {
  return dispot_more_y(d) + d.off * dispot_all_h(d);
}

function dispot_all_w(d) {
  return par_dispos.adv_red * dispot_w(d);
}

function gsclbt_y() {
  return dispot_y({
    start_time:
      department_settings.time.lunch_break_start_time
  });
}

function gsclbt_x() {
  return (did.w + did.mh) * week_days.nb_days() - did.mh;
}

function dispot_but_x() {
  return did.tlx + week_days.nb_days() * (did.w + did.mh) + did.mh;
}

function dispot_but_y(but) {
  var ret = did.tly + valid.h * 1.25;
  if (but != "app") {
    ret += did.mav;
  }
  return ret;
}

function dispot_but_txt_x() {
  return dispot_but_x() + .5 * stbut.w;
}

function dispot_but_txt_y(but) {
  return dispot_but_y(but) + .5 * stbut.h;
}


function st_but_ptr() {
  if (ckbox["dis-mod"].cked) {
    return "pointer";
  } else {
    return "default";
  }
}

function st_but_bold() {
  if (ckbox["dis-mod"].cked) {
    d3
      .select(this)
      .select("rect")
      .attr("stroke-width", 4);
  }
}

function st_but_back() {
  d3
    .select(this)
    .select("rect")
    .attr("stroke-width", 2);
}


/*---------------------
  ------- REGEN -----
  ---------------------*/

function ack_reg_y() {
  var ret = grid_height() + 20 * scale;
  if (row_gp.length > 1) {
    ret += 50 * scale;
  }
  return ret;
}

/*---------------------
  ------- QUOTE -----
  ---------------------*/

function quote_y() {
  return ack_reg_y();
}
function quote_x() {
  return 0;
}

/*--------------------
   ------ ALL -------
  --------------------*/

function classic_x(d) { return d.x; }
function classic_y(d) { return d.y; }
function classic_w(d) { return d.w; }
function classic_h(d) { return d.h; }
function classic_txt_x(d) { return classic_x(d) + .5 * classic_w(d); }
function classic_txt_y(d) { return classic_y(d) + .5 * classic_h(d); }
function classic_txt(d) { return d.txt; }


function sel_trans(d, i) {
  var ret = "translate(";
  ret += sel_popup.selx;
  ret += ",";
  ret += sel_popup.sely
    + i * (sel_popup.selh + sel_popup.selmy);
  ret += ")";
  return ret;
}
function sel_forall_trans() {
  var ret = "translate(";
  ret += sel_popup.selx + .5 * sel_popup.selw;
  ret += ",";
  ret += sel_popup.sely - sel_popup.selh - sel_popup.selmy;
  ret += ")";
  return ret;
}

function but_sel_opac(d) {
  return d.display ? 1 : opac;
}

function popup_trans(d) {
  return "translate(" + d.x + "," + d.y + ")";
}

function popup_exit_trans(d) {
  return "translate(" + popup_exit_trans_x(d) + ","
    + popup_exit_trans_y(d) + ")";
}
function popup_exit_trans_x(d) {
  return popup_bg_w(d) - 2 * sel_popup.mar_side - but_exit.side;
}
function popup_exit_trans_y(d) {
  return - (but_exit.side + but_exit.mar_next);
}


function popup_all_w(d) {
  return sel_popup.but[d.type].w;
}
function popup_all_h(d) {
  return sel_popup.but[d.type].h;
}
function popup_all_txt_x(d) {
  return .5 * popup_all_w(d);
}
function popup_all_txt_y(d) {
  return .5 * popup_all_h(d);
}

function popup_bg_h(d) {
  var margins = sel_popup.mar_side + but_exit.side + but_exit.mar_next
    + sel_popup.mar_side;
  if (d.type == "group") {
    return sel_popup.groups_h + margins;
  }
  var nb_el = d.list.length;
  return but_sel_type_y(nb_el - 1, d.type)
    + sel_popup.but[d.type].h
    + margins;
}

function popup_bg_w(d) {
  var t = d.type;
  var margins = 2 * sel_popup.mar_side;
  if (t == "group") {
    return sel_popup.groups_w + margins;
  }
  return (sel_popup.but[t].perline) * (sel_popup.but[t].w + sel_popup.but[t].mar_x)
    - sel_popup.but[t].mar_x + margins;
}

function popup_type_id(t) {
  return "popup-" + t;
}
function popup_panel_type_id(d) {
  return popup_type_id(d.type);
}

function popup_choice_w(d) {
  var t = d.panel.type;
  return sel_popup.but[t].w;
}
function popup_choice_h(d) {
  var t = d.panel.type;
  return sel_popup.but[t].h;
}
function popup_title_txt(d) {
  return d.txt;
}
function popup_title_x(d) {
  return .5 * popup_exit_trans_x(d);
}
function popup_title_y(d) {
  return .5 * (popup_exit_trans_y(d) - sel_popup.mar_side);
}


function depts_trans(d, i) {
  return "translate("
    + (departments.topx + i * (departments.marh + departments.h)) + ","
    + departments.topy + ")";
}
function dept_txt(d) {
  return d;
}


function pmg_x() {
  let wid = 0 ;
  if (pref_only) {
    if (pref_fetched) {
      let last_day = {day: week_days.last_day().ref} ;
      return dispo_x(last_day) + dispo_w(last_day) + 2 * dim_dispo.mh ;
    } else {
      wid = dsp_svg.w - dsp_svg.margin.left - 10 ;
    }
  } else {
    wid = grid_width();
  }
  return wid
    - 2 * pref_selection.marx
    - pref_selection.choice.w
    - pref_selection.butw ;
}
function pmg_y() {
  if (pref_only) {
    return 0;
  } else {
    return dsp_weeks.y;
  }
}
function pmg_trans() {
  return "translate(" + pmg_x() + "," + pmg_y() + ")";
}
function pref_mode_trans() {
  return "translate(0,"
    + (-.5 * dsp_weeks.y -
      (pref_selection.mode.length * (pref_selection.mary + pref_selection.buth)
        - pref_selection.mary))
    + ")";
}
function pref_mode_choice_trans_x() {
  return pref_selection.butw + pref_selection.marx ;
}
function pref_mode_choice_trans() {
  return "translate(" + pref_mode_choice_trans_x() + ", 0)";
}

function pref_mode_but_txt(d) {
  return d.txt;
}
function pref_mode_but_y(d, i) {
  return i * (pref_selection.mary + pref_selection.buth);
}
function pref_mode_but_txt_y(d, i) {
  return pref_mode_but_y(d, i) + .5 * pref_selection.buth;
}
function pref_mode_but_txt_x() {
  return .5 * pref_selection.butw;
}
function pref_mode_but_cls(d) {
  if (d.selected) {
    return "select-highlight";
  } else {
    return "select-standard";
  }
}


function constraint_y(d) {
  return cours_y({
    'start': d,
    'promo': root_gp.findIndex(function(g) {
      return g.row == 0 ;
    }),
    'duration': 0
  });
}
