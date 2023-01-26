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
----------  UPDATE -----------
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

// update all preferences
function go_pref(quick) {
  var t, dat, datdi, datsmi;

  if (quick) {
    t = d3.transition()
      .duration(0);
  } else {
    t = d3.transition();
  }


  // preferences: background color, and smiley

  dat = svg.get_dom("edt-mg").selectAll(".dispo")
    .data(
      user.dispos,
      function (d) {
        return [d.day, d.start_time, d.duration, d.value].join('-');
      });

  datdi = dat
    .enter()
    .append("g")
    .attr("class", "dispo");

  datdi.merge(dat)
    .attr("opacity", pref_opacity)
    .attr("cursor", cursor_pref());

  var datdisi = datdi
    .append("g")
    .attr("class", "dispo-si");

  datdisi
    .merge(dat.select(".dispo-si"))
    .on("mousedown", function(d) { pref_selection.start = d; })
    .on("mouseover", update_pref_selection)
    .on("mouseup", apply_change_simple_pref);

  datdisi
    .append("rect")
    .attr("class", "dispo-bg")
    .attr("stroke", "black")
    .attr("stroke-width", 1)
    .attr("width", dispo_w)
    .attr("height", 0)
    .attr("x", dispo_x)
    .attr("y", dispo_y)
    .attr("fill", dispo_fill)
    .merge(dat.select(".dispo-bg"))
    .transition(t)
    .attr("width", dispo_w)
    .attr("height", dispo_h)
    .attr("x", dispo_x)
    .attr("y", dispo_y)
    .attr("fill", dispo_fill);

  var datex = dat
    .exit();

  datex
    .select(".dispo-bg")
    .transition(t)
    .attr("height", 0);

  datex
    .remove();

  go_smiley(dat, datdisi, t);



  // detailed view

  datadvdi = datdi
    .append("g")
    .attr("class", "dispo-a");

  datadvdi
    .merge(dat.select(".dispo-a"))
    .on("click", function (d) {
      if (ckbox["dis-mod"].cked) {
        context_menu.dispo_hold = true;
        data_dispo_adv_cur = data_dispo_adv_init.map(
          function (c) {
            return {
              day: d.day,
              start_time: d.start_time,
              duration: d.duration,
              off: c.off
            };
          });
        go_cm_advanced_pref(true);
      }
    });


  datadvdi
    .append("rect")
    .attr("stroke", "none")
    .attr("stroke-width", 1)
    .attr("fill", "black")
    .attr("opacity", 0)
    .merge(dat.select(".dispo-a").select("rect"))
    .attr("width", dispo_more_h)
    .attr("height", dispo_more_h)
    .attr("x", dispo_more_x)
    .attr("y", dispo_more_y);

  datadvdi
    .append("line")
    .attr("stroke-linecap", "butt")
    .attr("stroke", "antiquewhite")
    .attr("stroke-width", 2)
    .attr("li", "h")
    .attr("x1", cross_l_x)
    .attr("y1", cross_m_y)
    .attr("x2", cross_r_x)
    .attr("y2", cross_m_y)
    .merge(dat.select(".dispo-a").select("[li=h]"))
    .transition(t)
    .attr("x1", cross_l_x)
    .attr("y1", cross_m_y)
    .attr("x2", cross_r_x)
    .attr("y2", cross_m_y);

  datadvdi
    .append("line")
    .attr("stroke-linecap", "butt")
    .attr("stroke", "antiquewhite")
    .attr("stroke-width", 2)
    .attr("li", "v")
    .attr("x1", cross_m_x)
    .attr("y1", cross_t_y)
    .attr("x2", cross_m_x)
    .attr("y2", cross_d_y)
    .merge(dat.select(".dispo-a").select("[li=v]"))
    .transition(t)
    .attr("x1", cross_m_x)
    .attr("y1", cross_t_y)
    .attr("x2", cross_m_x)
    .attr("y2", cross_d_y);

  datadvdi
    .append("circle")
    .attr("fill", "none")
    .attr("stroke", "antiquewhite")
    .attr("stroke-width", 2)
    .attr("cx", cross_m_x)
    .attr("cy", cross_m_y)
    .attr("r", par_dispos.rad_cross * smiley.tete)
    .merge(dat.select(".dispo-a").select("circle"))
    .transition(t)
    .attr("cx", cross_m_x)
    .attr("cy", cross_m_y)
    .attr("r", par_dispos.rad_cross * smiley.tete);


  go_cm_advanced_pref(quick);

  go_alarm_pref() ;
}


// recompute the total duration of availability
function compare_required_filled_pref() {
  if (user.dispos.length > 0) {
    filled_dispos = user.dispos.reduce(
      function(accu, pref) {
        let r = accu ;
        if (pref.value > 0) {
          r += pref.duration ;
        }
        return r ;
      },
      0
    ) ;
  }

  required_dispos = cours.reduce(
      function(partial_result, c){
        let r = partial_result;
        if (c.tutors.includes(user.name)) {
          r += c.duration;
        }
        return r
      },
      0
  ) ;
}



// top: container issued from selecting all the .dispo
// mid: container with new smileys
// t:   transition
function go_smiley(top, mid, t) {

  var datsmi = mid
    .append("g")
    .attr("class", "smiley")
    .attr("stroke-width", 1)
    .attr("transform", smile_trans)
    .attr("stroke", "black");

  datsmi
    .merge(top.select(".smiley"))
    .transition(t)
    .attr("transform", smile_trans)
    .attr("stroke", "black");

  datsmi
    .append("circle")
    .attr("st", "t")
    .merge(top.select("[st=t]"))
    .attr("cx", 0)
    .attr("cy", 0)
    .attr("r", smiley.tete)
    .attr("stroke", function (d) {
      return tete_str(rc(d));
    })
    .attr("fill", function (d) {
      return smi_fill(availability_content(d));
    });

  datsmi
    .append("circle")
    .attr("st", "od")
    .attr("fill", "none")
    .merge(top.select("[st=od]"))
    .attr("cx", smiley.tete * smiley.oeil_x)
    .attr("cy", smiley.tete * smiley.oeil_y)
    .attr("r", function (d) {
      return oeil_r(rc(d));
    })
    .attr("stroke-width", function (d) {
      return eye_str_width(d);
    });

  datsmi
    .append("circle")
    .attr("st", "og")
    .attr("fill", "none")
    .merge(top.select("[st=og]"))
    .attr("cx", -smiley.tete * smiley.oeil_x)
    .attr("cy", smiley.tete * smiley.oeil_y)
    .attr("r", function (d) {
      return oeil_r(rc(d));
    })
    .attr("stroke-width", function (d) {
      return eye_str_width(d);
    });


  datsmi
    .append("line")
    .attr("st", "sd")
    .merge(top.select("[st=sd]"))
    .attr("x1", function (d) {
      return sourcil_int_x(rc(d));
    })
    .attr("y1", function (d) {
      return sourcil_int_y(rc(d));
    })
    .attr("x2", function (d) {
      return sourcil_ext_x(rc(d));
    })
    .attr("y2", function (d) {
      return sourcil_ext_y(rc(d));
    })
    .attr("stroke-width", function (d) {
      return brow_str_width(d);
    });

  datsmi
    .append("line")
    .attr("st", "sg")
    .merge(top.select("[st=sg]"))
    .attr("x1", function (d) {
      return sourcil_intg_x(rc(d));
    })
    .attr("y1", function (d) {
      return sourcil_int_y(rc(d));
    })
    .attr("x2", function (d) {
      return sourcil_extg_x(rc(d));
    })
    .attr("y2", function (d) {
      return sourcil_ext_y(rc(d));
    })
    .attr("stroke-width", function (d) {
      return brow_str_width(d);
    });

  datsmi
    .append("rect")
    .attr("st", "si")
    .merge(top.select("[st=si]"))
    .attr("x", -.5 * smiley.rect_w * smiley.tete)
    .attr("y", -.5 * smiley.rect_h * smiley.tete)
    .attr("width", function (d) {
      return interdit_w(rc(d));
    })
    .attr("height", smiley.rect_h * smiley.tete)
    .attr("fill", "white")
    .attr("stroke", "none");

  datsmi
    .append("path")
    .attr("st", "b")
    .merge(top.select("[st=b]"))
    .attr("d", function (d) {
      return smile(rc(d));
    })
    .attr("fill", "none")
    .attr("stroke-width", function (d) {
      return mouth_str_width(d);
    });

  datsmi
    .append("path")
    .attr("st", "hpr")
    .attr("fill", hp_fill)
    .merge(top.select("[st=hpr]"))
    .attr("d", path_hpr)
    .attr("stroke-width", hp_stroke_width);

  datsmi
    .append("path")
    .attr("st", "hpl")
    .attr("fill", hp_fill)
    .merge(top.select("[st=hpl]"))
    .attr("d", path_hpl)
    .attr("stroke-width", hp_stroke_width);

  datsmi
    .append("path")
    .attr("st", "hpt")
    .attr("fill", "none")
    .merge(top.select("[st=hpt]"))
    .attr("d", path_hpt)
    .attr("stroke-width", hp_stroke_width);

  datsmi
    .append("rect")
    .attr("st", "hpm")
    .merge(top.select("[st=hpm]"))
    .attr("x", -.5 * smiley.headphone.mouth_w * smiley.tete)
    .attr("y", .5 * smiley.headphone.mouth_h * smiley.tete)
    .attr("rx", 2)
    .attr("width", hp_mouth_w)
    .attr("height", smiley.headphone.mouth_h * smiley.tete)
    .attr("fill", "black")
    .attr("stroke", "none");

  datsmi
    .append("line")
    .attr("st", "hpmr")
    .merge(top.select("[st=hpmr]"))
    .attr("x1", .45 * smiley.headphone.mouth_w * smiley.tete)
    .attr("y1", smiley.headphone.mouth_h * smiley.tete)
    .attr("x2", smiley.tete)
    .attr("y2", 0)
    .attr("stroke", "black")
    .attr("stroke-width", hp_mouth_sw);
  

}


// advanced preference menu
function go_cm_advanced_pref(quick) {
  if (quick) {
    t = d3.transition()
      .duration(0);
  } else {
    t = d3.transition();
  }

  var dis_men_dat = svg.get_dom("cmpg")
    .selectAll(".dispo-menu")
    .data(data_dispo_adv_cur);

  var dis_men = dis_men_dat
    .enter()
    .append("g")
    .attr("class", "dispo-menu")
    .attr("cursor", "pointer")
    .on("click", function (d) {
      update_pref_interval(user.name, d.day, d.start_time, d.duration, d.off);
      data_dispo_adv_cur = [];
      go_pref(true);
    });

  dis_men
    .append("rect")
    .attr("class", "dis-men-bg")
    .merge(dis_men_dat.select(".dis-men-bg"))
    .transition(t)
    .attr("x", dispo_all_x)
    .attr("y", dispo_all_y)
    .attr("width", dispo_all_w)
    .attr("height", dispo_all_h)
    .attr("fill", function (d) {
      return smi_fill(d.off);
    })
    .attr("stroke", "darkslategrey")
    .attr("stroke-width", 2);

  go_smiley(dis_men_dat, dis_men, t);


  dis_men_dat.exit().remove();
}


// check and inform whenever there is not enough available slots
function go_alarm_pref() {

  compare_required_filled_pref() ;


  var dig = svg.get_dom("dig");

  // escape if there is no alarm 
  if (typeof dig === 'undefined') {
    return ;
  }
  
  dig
    .select(".disp-info").select(".disp-required")
    .text(txt_reqDispos)
    .attr("x", menus.x + menus.mx - 5)
    .attr("y", did.tly + valid.h * 1.5);
  dig
    .select(".disp-info").select(".disp-filled")
    .text(txt_filDispos)
    .attr("x", menus.x + menus.mx - 5)
    .attr("y", did.tly + valid.h * 1.5 + valid.margin_h);
  dig
    .select(".disp-info").select(".disp-comm")
    .text(txt_comDispos)
    .attr("x", menus.x + menus.mx - 5)
    .attr("y", did.tly + valid.h * 1.5 + 2 * valid.margin_h);


  if (required_dispos > filled_dispos) {
    dig
      .select(".disp-info").select(".disp-filled")
      .attr("font-weight", "bold").attr("fill", "red");
    dig
      .select(".disp-info").select(".disp-comm")
      .attr("font-weight", "bold").attr("fill", "red");
    dig
      .select(".disp-info").select(".disp-required")
      .attr("font-weight", "bold");
  } else {
    dig
      .select(".disp-info").select(".disp-filled")
      .attr("font-weight", "normal").attr("fill", "black");
    dig
      .select(".disp-info").select(".disp-comm")
      .attr("font-weight", "normal").attr("fill", "black");
    dig
      .select(".disp-info").select(".disp-required")
      .attr("font-weight", "normal");
  }
}


function go_pref_mode() {

  var selall = svg.get_dom("pmg")
    .select("#pm-but-head")
    .selectAll(".pm-but")
    .data(pref_selection.mode);

  var g_new = selall
    .enter()
    .append("g")
    .attr("cursor", "pointer")
    .attr("class", "pm-but")
    .on("click", apply_pref_mode);

  var rect_new = g_new
    .append("rect")
    .attr("x", 0)
    .attr("y", pref_mode_but_y)
    .attr("rx", 5)
    .attr("ry", 10)
    .attr("width", pref_selection.butw)
    .attr("height", pref_selection.buth);

  g_new
    .append("text")
    .attr("x", pref_mode_but_txt_x)
    .attr("y", pref_mode_but_txt_y)
    .text(pref_mode_but_txt);

  rect_new
    .merge(selall.select("rect"))
    .attr("class", pref_mode_but_cls);

  go_paint_pref_mode_choices(false);
}

// smileys in paint preference mode
function go_paint_pref_mode_choices(quick) {
  var t, dat, datdi, datsmi;

  if (quick) {
    t = d3.transition()
      .duration(0);
  } else {
    t = d3.transition();
  }

  var parent = svg.get_dom("pmg")
    .select("#pm-choices");

  parent
    .attr("opacity", pref_sel_choice_opac);

  // preferences: background color, and smiley
  dat = parent
    .selectAll(".dispo")
    .data(pref_selection.choice.data);

  datdi = dat
    .enter()
    .append("g")
    .attr("cursor", "pointer")
    .attr("class", "dispo");

  var datdisi = datdi
    .append("g")
    .attr("class", "dispo-si")
    .on("click", apply_pref_mode_choice);

  datdisi
    .append("rect")
    .attr("class", "dispo-bg")
    .attr("stroke", "black")
    .attr("width", pref_selection.choice.w)
    .attr("height", pref_selection.choice.h)
    .attr("x", pref_sel_choice_x)
    .attr("y", 0)
    .attr("fill", dispo_fill)
    .merge(dat.select(".dispo-bg"))
    .transition(t)
    .attr("width", pref_selection.choice.w)
    .attr("height", pref_selection.choice.w)
    .attr("x", pref_sel_choice_x)
    .attr("y", pref_sel_choice_y)
    .attr("fill", dispo_fill)
    .attr("stroke-width", pref_sel_choice_stkw);

  go_smiley(dat, datdisi, t);

}


/*---------------------
  ------- WEEKS -------
  ---------------------*/





/*----------------------
  -------- GRID --------
  ----------------------*/


function go_grid(quick) {
  var t;
  if (quick) {
    t = d3.transition()
      .duration(0);
  } else {
    t = d3.transition();
  }

  var fg = svg.get_dom("edt-fg");

  svg.get_dom("edt-bg")
    .select("rbg")
    .attr("x", 0)
    .attr("y", 0)
    .attr("height", grid_height())
    .attr("width", grid_width());


  if (plot_constraint_lines) {
    let constraint_d = svg.get_dom("edt-fg").selectAll(".cst")
      .data(
        Object.keys(rev_constraints).map(function(c){return +c ;})
      );
    
    let constraint_g = constraint_d
      .enter()
      .append("line")
      .attr("class", "cst");
    
    constraint_g
      .merge(constraint_d)
      .attr("stroke", "black")
      .attr("stroke-width", 2)
      .attr("x1", 0)
      .attr("y1", constraint_y)
      .attr("x2", grid_width())
      .attr("y2", constraint_y);
  }


  var grid = fg.selectAll(".grids")
    .data(
      data_slot_grid.filter(function (d) {
        return groups[d.promo]["structural"][d.group].display;
      }),
      function (d) { return d.day + d.start + d.group + d.promo; }
    );

  var gridg = grid
    .enter()
    .append("g")
    .attr("class", "grids")
    .style("cursor", "default");


  gridg
    .append("rect")
    .attr("stroke", gs_sc)
    .merge(grid.select("rect"))
    .attr("x", cours_x)
    .attr("y", cours_y)
    .attr("width", cours_width)
    .attr("height", cours_height)
    .attr("fill", gs_fill);

  grid
    .exit()
    .remove();




  grid = svg.get_dom("edt-bg").selectAll(".gridscg")
    .data(
      data_grid_scale_gp
        .filter(function (d) {
          return d.gp.display;
        }),
      function (d) {
        return d.gp.promo + "," + d.day + "," +
          d.gp.name;
      }
    );

  grid
    .enter()
    .append("text")
    .attr("class", "gridscg")
    .attr("x", gscg_x)
    .attr("y", gscg_y)
    .text(gscg_txt)
    .merge(grid)
    .transition(t)
    .attr("x", gscg_x)
    .attr("y", gscg_y);

  grid.exit().remove();


  grid = svg.get_dom("edt-bg").selectAll(".gridscp")
    .data(
      data_grid_scale_row
        .filter(function (d) {
          return row_gp[d.row].display;
        }),
      function (d) {
        return d.row + "," + d.start;
      }
    );

  grid
    .enter()
    .append("text")
    .attr("class", "gridscp")
    .attr("x", gscp_x)
    .attr("y", gscp_y)
    .text(gscp_txt)
    .merge(grid)
    .transition(t)
    .attr("x", gscp_x)
    .attr("y", gscp_y);

  grid.exit().remove();


  go_days(quick, true);



  fg.select(".h-sca").select("rect")
    .transition(t)
    .attr("x", but_sca_h_x())
    .attr("y", but_sca_h_y());
  fg.select(".h-sca").select("path")
    .transition(t)
    .attr("d", but_sca_tri_h(0));

  fg.select(".v-sca").select("rect")
    .transition(t)
    .attr("x", but_sca_v_x())
    .attr("y", but_sca_v_y());
  fg.select(".v-sca").select("path")
    .transition(t)
    .attr("d", but_sca_tri_v(0));



}

/*--------------------------
  ------- TIME ------
  --------------------------*/

// display day names, and a rectangle per half day
// if half_day_rect is true
// layer: fg
// data: days, department_settings.time, side_time
// class: gridsckd, txt_scl, day_am,
//        gridsckhb, gridsckhlam, gridsckhlpm
//        gridsckh, gridsckhl
// trans: gsckd: txt, x, y,
//        grid_day_am: x, y, height, width
//        grid_day_pm: x, y, height, width
//        bknews_top_y, bknews_bot_y, grid_height
//        gsckh: x1, y, x2, txt
function go_days(quick) {

  var t = get_transition(quick);

  days_header.update(quick);

  hours_header.update(quick);
}

/*----------------------
  ------- BKNEWS -------
  ----------------------*/


function go_bknews(quick) {
  var t;
  if (quick) {
    t = d3.transition()
      .duration(0);
  } else {
    t = d3.transition();
  }

  svg.get_dom("edt-fig")
    .select(".top-bar")
    .transition(t)
    .attr("x1", 0)
    .attr("y1", bknews_top_y())
    .attr("x2", grid_width())
    .attr("y2", bknews_top_y());

  svg.get_dom("edt-fig")
    .select(".bot-bar")
    .transition(t)
    .attr("x1", 0)
    .attr("y1", bknews_bot_y())
    .attr("x2", grid_width())
    .attr("y2", bknews_bot_y());

  var flash = svg.get_dom("edt-fig").select(".txt-info");

  var fl_all = flash
    .selectAll(".bn-all")
    .data(
      bknews.cont,
      function (d) { return d.id; }
    );

  var ffl = fl_all
    .enter()
    .append("g")
    .attr("class", "bn-all")
    .append("a")
    .attr("xlink:href", bknews_link);

  ffl
    .append("rect")
    .attr("class", "bn-rec")
    .attr("fill", bknews_row_fill)
    .attr("stroke", bknews_row_fill)
    .attr("stroke-width", 1)
    .attr("y", bknews_row_y)
    .merge(fl_all.select(".bn-rec"))
    .transition(t)
    .attr("x", bknews_row_x)
    .attr("y", bknews_row_y)
    .attr("width", bknews_row_width)
    .attr("height", bknews_row_height);



  ffl
    .append("text")
    .attr("class", "bn-txt")
    .attr("fill", bknews_row_txt_strk)
    .text(bknews_row_txt)
    .attr("y", bknews_row_txt_y)
    .merge(fl_all.select(".bn-txt"))
    .transition(t)
    .attr("x", bknews_row_txt_x)
    .attr("y", bknews_row_txt_y);

  fl_all.exit().remove();

}


/*----------------------
  ------- QUOTES -------
  ----------------------*/


function go_quote() {
  svg.get_dom("vg").select(".quote").select("text")
    .transition(d3.transition())
    .attr("x", quote_x())
    .attr("y", quote_y());
}




/*----------------------
  ------- GROUPS -------
  ----------------------*/

function go_gp_buttons() {
  for (var p = 0; p < set_promos.length; p++) {
    var cont = svg.get_dom("selg")
      .select(".sel-pop-g#" + popup_type_id("group"))
      .selectAll('[train_prog="' + set_promos[p] + '"]')
      .data(Object.keys(groups[p]["structural"]).map(function (k) {
        return groups[p]["structural"][k];
      }));

    var contg = cont
      .enter()
      .append("g")
      .attr("train_prog", set_promos[p])
      .attr("transform", function (gp) {
        return "translate(" + (root_gp[gp.promo].butx) + ","
          + (root_gp[gp.promo].buty) + ")";
      })
      .attr("gpe", function (gp) {
        return gp.name;
      })
      .attr("promo", function (gp) {
        return gp.promo;
      })
      .on("click", function (gp) {
        apply_gp_display(gp, false, true);
      });


    contg.append("rect")
      .attr("x", butgp_x)
      .attr("y", butgp_y)
      .attr("width", butgp_width)
      .attr("height", butgp_height)
      .merge(cont.select("rect"))
      .attr("fill", fill_gp_button)
      .attr("class", class_gp_button)
      .attr("stroke-width", 1)
      .attr("stroke", "black");

    contg.append("text")
      .attr("x", butgp_txt_x)
      .attr("y", butgp_txt_y)
      .text(butgp_txt);

  }



}


/*--------------------
  ------ MENUS -------
  --------------------*/
function go_menus() {

  var init = svg.get_dom("meg")
    .selectAll(".ckline")
    .data(Object.keys(ckbox));


  var ent = init
    .enter()
    .append("g")
    .attr("class", "ckline")
    .on("click", apply_ckbox);



  var cs = ent
    .append("g")
    .attr("class", "ckstat");

  var cd = ent.
    append("g")
    .attr("class", "ckdyn");


  cs
    .append("rect")
    .attr("x", menu_cks_x)
    .attr("y", menu_cks_y)
    .attr("rx", 2)
    .attr("ry", 2)
    .attr("width", menus.sfac * menus.h)
    .attr("height", menus.sfac * menus.h)
    .merge(init.select(".ckstat").select("rect"))
    .attr("stroke", menu_cks_fill)
    .attr("stroke-width", menu_cks_stw);

  cs
    .append("text")
    .attr("x", menu_ck_txt_x)
    .attr("y", menu_ck_txt_y)
    .merge(init.select(".ckstat").select("text"))
    .attr("fill", menu_cks_fill)
    .text(menu_cks_txt);


  cd
    .append("rect")
    .attr("stroke", "none")
    .attr("x", menu_ckd_x)
    .attr("y", menu_ckd_y)
    .attr("width", menus.ifac * menus.sfac * menus.h)
    .attr("height", menus.ifac * menus.sfac * menus.h)
    .merge(init.select(".ckdyn").select("rect"))
    .attr("fill", menu_ckd_fill);


  svg.get_dom("meg")
    .selectAll(".ckline")
    .data(Object.keys(ckbox))
    .attr("cursor", menu_curs);

}


/*--------------------
  ------ MODULES -------
  --------------------*/


/*--------------------
  ------ ROOMS -------
  --------------------*/

/*--------------------
  ------ TUTORS ------
  --------------------*/


/*--------------------
  ------ COURS -------
  --------------------*/

// update display cours attribute according to current selections
// if its module, tutor or room does not appear in selection lists,
// the course is not displayed
function update_selection() {
  cours.forEach(function(c) {
    var mod = modules.all.find(function(d) {
      return d.name == c.mod ;
    });
    let tut_display = false ;
    for(let it = 0 ; it < tutors.all.length && !tut_display ; it++) {
      if (c.tutors.includes(tutors.all[it].name) &&
         tutors.all[it].display) {
        tut_display = true ;
      }
    }
    var tut = tutors.all.find(function(d) {
      return c.tutors.includes(d.name) ;
    });
    var roo = rooms_sel.all.filter(function(d) {
      // visio room
      if (c.room === null) {
        return true ;
      }
      // physical room
      if (c.room in rooms.roomgroups) {
        return rooms.roomgroups[c.room].includes(d.name) ;
      } else {
        return false;
      }
    });
    const reducer = (p, c) => (p || c.display);
    let display_room = roo.reduce(reducer, false);
    if (typeof mod === 'undefined') {
      c.display = false ;
    } else {
      c.display = mod.display && tut_display && display_room ;
    }
  });
}

// update active flags for selections
function update_active() {
  var tut_av = sel_popup.get_available("tutor");
  var mod_av = sel_popup.get_available("module");

  if (typeof tut_av !== 'undefined') {
    tut_av.active = tutors.all.filter(function (d) {
      return d.display;
    }).length != tutors.all.length;
  } else {
    tut_av = {active: false} ;
  }
  if (typeof mod_av !== 'undefined') {
    mod_av.active = modules.all.filter(function (d) {
      return d.display;
    }).length != modules.all.length;
  } else {
    mod_av = {active: false} ;
  }

  sel_popup.active_filter = tut_av.active || mod_av.active;

  if (!department_settings.mode.cosmo) {
    var room_av = sel_popup.get_available("room");
    room_av.active = rooms_sel.all.filter(function (d) {
      return d.display;
    }).length != rooms_sel.all.length;
    sel_popup.active_filter = sel_popup.active_filter || room_av.active;
  }

}

function go_courses(quick) {
  var t;
  if (quick) {
    t = d3.transition()
      .duration(0);
  } else {
    t = d3.transition();
  }


  update_selection();

  var cg = svg.get_dom("edt-mg")
    .selectAll(".cours")
    .data(
      cours.filter(function (d) {
        return groups[d.promo]["structural"][d.group].display;
      }),
      function (d) { return d.group + d.id_course; }
    )
    .attr("cursor", ckbox["edt-mod"].cked ? "pointer" : "default");

  var incg = cg.enter()
    .append("g")
    .attr("class", "cours")
    .attr("cursor", ckbox["edt-mod"].cked ? "pointer" : "default")
    .on("contextmenu", function (d) {
      if (ckbox["edt-mod"].cked) {
        d3.event.preventDefault();
        if (!department_settings.mode.cosmo) {
          room_tutor_change.cm_settings = entry_cm_settings;
        }
        pending.prepare_modif(d);
        compute_cm_room_tutor_direction();
        //select_room_change(d);
        if (!department_settings.mode.cosmo) {
          select_entry_cm();
        } else {
          salarie_cm_level = 0;
          select_salarie_change();
        }
        go_cm_room_tutor_change();
      }
    })
    .call(dragListener)
    .on("dblclick", show_detailed_courses);

  incg
    .merge(cg)
    .attr("opacity", cours_opac);

  incg
    .append("rect")
    .attr("class", "crect")
    .attr("x", cours_x)
    .attr("y", cours_y)
  // rx and ry regular attributes...
    .attr("rx", 3)
    .attr("ry", 3)
    .attr("width", 0)
    .merge(cg.select("rect"))
    .attr("fill", cours_fill)
    .attr("stroke", cours_stk)
    .transition(t)
    .attr("x", cours_x)
    .attr("y", cours_y)
    .attr("width", cours_width)
    .attr("height", cours_height);

  if (ckbox["edt-mod"].cked
      && logged_usr.dispo_all_see) {
    d3.selectAll("rect.crect").attr("fill", function (d) {
      try {
        lDis = get_preference(dispos[d.tutors[0]][d.day], d.duration);
      } catch (e) {
        lDis = par_dispos.nmax;
      }

      return smi_fill(lDis);
    });
  } else {
    d3.selectAll("rect.crect").attr("fill", cours_fill);
  }

  // Tutor's fullname 

  // var divtip = d3.select("body").append("div")
  // .attr("class", "tooltip")
  // .style("opacity", 0);

  // 
  // d3.selectAll("g.cours")
  // .on("mouseover", function(d) {
  //     divtip.transition()
  //         .duration(500)
  //         .style("opacity", .95);
  //     divtip.html(d.prof_full_name + " : "  + d.mod)
  //         .style("left", (d3.event.pageX) + "px")
  //         .style("top", (d3.event.pageY+15) + "px");
  //     })
  // .on("mouseout", function(d) {
  //     divtip.transition()
  //         .duration(200)
  //         .style("opacity", 0);
  // })

  // if cosmo_mode is 2, we put only module, in the middle!
   if (department_settings.mode.cosmo === 2) {
     incg
       .append("text")
       .attr("st", "p")
       .attr("font-size", cours_txt_size)
       .merge(cg.select("[st=p]"))
       .transition(t)
       .attr("font-weight", cours_txt_weight)
       .attr("fill", cours_txt_fill)
       .attr("x", cours_txt_x)
       .attr("y", cours_txt_mid_y)
       .attr("x", cours_txt_x)
       .attr("y", cours_txt_mid_y)
       .text(cours_txt_top_txt);
   }
   else {
     incg
       .append("text")
       .attr("st", "p")
       .merge(cg.select("[st=p]"))
       .transition(t)
       .attr("font-size", cours_txt_size)
       .attr("font-weight", cours_txt_weight)
       .attr("fill", cours_txt_fill)
       .attr("x", cours_txt_x)
       .attr("y", cours_txt_mid_y)
       .attr("x", cours_txt_x)
       .attr("y", cours_txt_mid_y)
       .text(cours_txt_mid_txt);
   }


  if (!department_settings.mode.cosmo) {
    incg
      .append("text")
      .attr("st", "m")
      .attr("x", cours_txt_x)
      .attr("y", cours_txt_top_y)
      .text(cours_txt_top_txt)
      .merge(cg.select("[st=m]"))
      .attr("fill", cours_txt_fill)
      .transition(t)
      .attr("font-size", cours_txt_size)
      .attr("font-weight", cours_txt_weight)
      .attr("x", cours_txt_x)
      .attr("y", cours_txt_top_y);

    incg
      .append("text")
      .attr("st", "r")
      .attr("x", cours_txt_x)
      .attr("y", cours_txt_bot_y)
      .merge(cg.select("[st=r]"))
      .text(cours_txt_bot_txt)
      .attr("fill", cours_txt_fill)
      .attr("font-weight", cours_txt_weight)
      .attr("font-size", cours_txt_size)
      .transition(t)
      .attr("x", cours_txt_x)
      .attr("y", cours_txt_bot_y);
  }

  cg.exit()
    .remove();

  go_cm_room_tutor_change();
}


/*-----------------------
  ------ VALIDATE ------
  -----------------------*/

// update acknowledgment message
function go_ack_msg() {
  if (ack.ongoing.length == 0) {
    
    let btn_txt = "Super";
    let ack_list = typeof ack.list !== 'undefined' ;
    let com_list = [] ;

    if (ack_list) {
      if(typeof ack.list.find(function(a) { return a.status == 'KO'; })
         === 'undefined') {
        ack.status = 'OK' ;
      } else {
        ack.status = 'KO' ;
      }
    }
    
    if (ack.status == 'KO') {
      btn_txt = "Ok";
    }

    if (ack_list) {
      ack.list.filter(function(a) {
        return a.status == 'KO' ;
      }).map(function(a) {
        return {'txt': a.more} ;
      });
    } else {
      if (ack.more != '') {
        com_list.append(ack.more);
      }
    }
    
    if (com_list.length == 0) {
      com_list.push({txt: ack.predefined[ack.status]});
    }
    var splash_ack = {
      id: "ack-edt-mod",
      but: { list: [{ txt: btn_txt, click: function (d) {
        ack.list = [] ;
      } }] },
      com: { list: com_list }
    };
    splash(splash_ack);
  }
}


// update info about re-generation
function go_regen(s) {
  if (s != null) {
    total_regen = false;
    var txt = "";
    var elements = s.split(/,/);
    var regen_id = elements[elements.length - 1];
    if (elements[0] == 'N') {
      txt = gettext('No planned re-generation');
    } else if (elements[0] == 'C') {
      var total_regen = true;
      if (elements.length > 2 && elements[2] == 'S') {
        txt = gettext("Full (minor) generation planned on ") + elements[1] +
          "(" + elements[3] + ")";
      } else {
        txt = gettext("Full generation planned (probably on ") + elements[1] + ")";
      }
    } else if (elements[0] == 'S') {
      txt = gettext("Minor generation planned (probably on ") + elements[1] + ")";
    }

    ack.regen = txt;

    svg.get_dom("vg").select(".ack-reg").select("text")
      .text(ack.regen);
    svg.get_dom("vg").select(".ack-reg")
        .attr('href', '/admin/base/regen/'+regen_id)
        .attr('target', "_blank");
  }
  svg.get_dom("vg").select(".ack-reg").select("text")
    .transition(d3.transition())
    .attr("x", grid_width())
    .attr("y", ack_reg_y());

}


function but_bold() {
  d3
    .select(this)
    .select("rect")
    .attr("stroke-width", 4);
}

function but_back() {
  d3
    .select(this)
    .select("rect")
    .attr("stroke-width", 2);
}



/*--------------------
  ------ ALL -------
  --------------------*/

// update everything
function go_edt(t) {
  go_grid(t);
  go_courses(t);
  //go_tutors();
  go_pref(t);
  //go_ack_msg(t);
  go_bknews(t);
  go_alarm_pref();
  go_regen(null);
  go_quote();
}


function go_selection_buttons() {

  var cont = svg.get_dom("selg")
    .selectAll(".sel-pop-g")
    .data(sel_popup.panels, function (p) {
      return p.type;
    })
    .selectAll(".sel-button")
    .data(function (p) {
      p.list.forEach(function (c) {
        c.panel = p;
      });
      return p.list;
    }, function (c) {
      return c.name;
    });

  var contg = cont
    .enter()
    .append("g")
    .attr("class", "sel-button")
    .on("click", apply_selection_display);

  var concon = contg
    .merge(cont)
    .attr("opacity", but_sel_opac);



  contg
    .append("rect")
    .attr("ty", "ch")
    .attr("width", popup_choice_w)
    .attr("height", popup_choice_h)
    .attr("rx", 5)
    .attr("ry", 10)
    .merge(cont.select("rect"))
    .attr("class", but_sel_class)
    .attr("x", but_sel_x)
    .attr("y", but_sel_y);

  contg
    .append("text")
    .attr("class", but_sel_class)
    .text(function (d) {
      return d.name;
    })
    .merge(cont.select("text"))
    .attr("class", but_sel_class)
    .attr("x", but_sel_txt_x)
    .attr("y", but_sel_txt_y);

  cont.exit().remove();

}


// update relevant modules according to selected tutors
// ---
// tutor(s) selected -> any taught module
// no selected tutor -> module taught by logged user if any
function update_relevant() {
  modules.all.forEach(function (m) {
    m.relevant = false;
  });
  var tut_act = sel_popup.get_available("tutor").active;
  cours.forEach(function (c) {
    var mod = modules.all.find(function (d) {
      return d.name == c.mod;
    });
    var tut = tutors.all.find(function (d) {
      return c.tutors.includes(d.name);
    });
    if (!tut_act) {
      if (c.tutors.includes(user.name)) {
        mod.relevant = true;
      }
    } else if (typeof mod !== 'undefined'
               && typeof tut !== 'undefined' && tut.display) {
      mod.relevant = true;
    }
  });
}
