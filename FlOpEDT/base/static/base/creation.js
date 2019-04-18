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
-------    CREATION    -------
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
                 */


/*----------------------
  -------   TIME  -------
  ----------------------*/

function get_day(ref){
    var nd = days.filter(function(dd) {
	return dd.ref == ref;
    });
    if (nd.length != 1) {
	return null ;
    }
    return nd[0];
}


/*----------------------
  -------   SVG  -------
  ----------------------*/



function create_general_svg(light) {
    var tot;

    if (light) {
        tot = d3.select("body");
    } else {
        tot = d3.select("body").append("div");
    }

    svg_cont = tot
        .append("svg")
        .attr("width", svg.width)
        .attr("height", svg.height)
        .attr("id", "edt-main")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    create_layouts(svg_cont, light);

}




function create_layouts(svg_cont, light) {
    // menus ground
    meg = svg_cont.append("g")
        .attr("id", "lay-meg");

    // weeks ground
    wg.upper = svg_cont.append("g")
        .attr("id", "lay-wg");
    wg.bg = wg.upper.append("g")
        .attr("id", "wg-bg");
    wg.fg = wg.upper.append("g")
        .attr("id", "wg-fg");

    // groupes ground
    gpg = svg_cont.append("g")
        .attr("id", "lay-gpg");

    // selection categories button ground
    catg = svg_cont.append("g")
        .attr("id", "lay-catg");

    if (!light) {

        $("#div-mod").css("width", modules.width);
        $("#div-mod").css({
            position: "relative",
            left: modules.x,
            top: modules.y
        });
        $("#div-mod").css("height", modules.height);

        $("#div-sal").css("width", salles.width);
        $("#div-sal").css({
            position: "relative",
            left: salles.x,
            top: salles.y
        });
        $("#div-sal").css("height", salles.height);

    }



    // semaine type ground
    stg = svg_cont.append("g")
        .attr("id", "lay-stg");


    // dispos info ground
    dig = svg_cont.append("g")
        .attr("id", "lay-dg");


    // valider
    vg = svg_cont.append("g")
        .attr("id", "lay-vg");

    // background, middleground, foreground, dragground
    var edtg = svg_cont.append("g")
        .attr("id", "lay-edtg");
    bg = edtg.append("g")
        .attr("id", "lay-bg");
    mg = edtg.append("g")
        .attr("id", "lay-mg");
    fig = edtg.append("g")
        .attr("id", "lay-fig");
    fg = edtg.append("g")
        .attr("id", "lay-fg");

    // selection ground
    selg = svg_cont.append("g")
        .attr("id", "lay-selg");

    
    // context menus ground
    var cmg = svg_cont.append("g")
        .attr("id", "lay-cmg");
    cmpg = cmg.append("g")
	.attr("id", "lay-cmpg");
    cmtg = cmg.append("g")
	.attr("id", "lay-cmtg");
    

    // logo ground
    log = edtg.append("g")
        .attr("id", "lay-log");

    // drag ground
    dg = svg_cont.append("g")
        .attr("id", "lay-dg");

    bg
	.append("rect")
	.attr("class","rbg");
}




/*---------------------------
  ------- PREFERENCES -------
  ---------------------------*/

function create_alarm_dispos() {
    di = dig
        .append("g")
        .attr("text-anchor", "start")
        .attr("class", "disp-info");

    di
        .append("text")
        .attr("class", "disp-required")
        .text(txt_reqDispos);

    di
        .append("text")
        .attr("class", "disp-filled")
        .text(txt_filDispos);
}


/*---------------------
  ------- WEEKS -------
  ---------------------*/



// PRECONDITION: semaine_init, week_init, weeks.init_data
function find_week(week_list) {
    var i, up;
    i = 0;
    up = false ;
    
    while (i < week_list.length && !up) {
        if (an_init < week_list[i].an ||
            (an_init == week_list[i].an &&
                semaine_init < week_list[i].semaine)) {
            up = true;
        } else {
            i++;
        }
    }
    if (!up) {
        i = 0;
    }
    return i;
}




function create_clipweek() {

    weeks.init_data = semaine_an_list;

    var min = weeks.init_data[0];
    var max = weeks.init_data[weeks.init_data.length - 1];

    weeks.ndisp = Math.min(weeks.ndisp, weeks.init_data.length);

    weeks.init_data.push({
        an: max.an,
        semaine: max.semaine + 1
    });
    weeks.init_data.unshift({
        an: min.an,
        semaine: min.semaine - 1,
    });

    var fw ;

    if (min.an > an_init ||
	(min.an == an_init && min.semaine > semaine_init)) {
	weeks.cur_data = weeks.init_data.slice(1,
					       1 + weeks.ndisp + 2);
	weeks.fdisp = 1;
	weeks.sel[0] = 2 ;
	
    } else if (max.an < an_init ||
	(max.an == an_init && max.semaine < semaine_init)) {
	weeks.cur_data = weeks.init_data.slice(weeks.init_data.length - 1  - 2 - weeks.ndisp,
					       weeks.init_data.length -1);
	weeks.fdisp = weeks.init_data.length - 1  - 2 - weeks.ndisp ;
	weeks.sel[0] = weeks.ndisp ;
    } else {
	var fw = find_week(weeks.init_data);
	
	fw = Math.max(
            Math.min(fw - 2,
		     weeks.init_data.length - 1 - (weeks.ndisp + 1)),
            0);
	
	weeks.cur_data = weeks.init_data.slice(fw,
					       fw + weeks.ndisp + 2);
	
	weeks.fdisp = fw;
	
	weeks.sel[0] = fw + find_week(weeks.cur_data) - 1 ;
    }


    wg.upper
        .attr("transform", "translate(" + weeks.x + "," + weeks.y + ")");


    wg.fg
        .selectAll(".sel_wk")
        .data(weeks.sel)
        .enter()
        .append("g")
        .attr("class", "sel_wk")
        .attr("clip-path", "url(#clipwk)")
        .attr("pointer-events", "none")
        .append("ellipse")
        .attr("cx", week_sel_x)
        .attr("cy", .5 * weeks.height)
        .attr("rx", .5 * weeks.wfac * weeks.width)
        .attr("ry", .5 * weeks.hfac * weeks.height);



    var but =
        wg.fg
        .append("g")
        .attr("class", "cir_wk")
        .on("click", week_left);


    but
        .append("circle")
        .attr("stroke", "white")
        .attr("stroke-width", 1)
        .attr("cx", 0)
        .attr("cy", .5 * weeks.height)
        .attr("r", weeks.rad * .5 * weeks.height);

    but
        .append("text")
        .attr("fill", "white")
        .attr("x", 0)
        .attr("y", .5 * weeks.height)
        .text("<");


    but =
        wg.fg
        .append("g")
        .attr("class", "cir_wk")
        .on("click", week_right);

    but
        .append("circle")
        .attr("stroke", "white")
        .attr("stroke-width", 1)
        .attr("cx", (weeks.ndisp + 1) * weeks.width)
        .attr("cy", .5 * weeks.height)
        .attr("r", weeks.rad * .5 * weeks.height)

    but
        .append("text")
        .attr("fill", "white")
        .attr("x", (weeks.ndisp + 1) * weeks.width)
        .attr("y", .5 * weeks.height)
        .text(">");


    wg.bg
        .append("rect")
        .attr("class", "cir_wk")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", (weeks.ndisp + 1) * weeks.width)
        .attr("height", weeks.height);

    wg.bg
        .append("g")
        .append("clipPath")
        .attr("id", "clipwk")
        .append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("height", weeks.height)
        .attr("width", (weeks.ndisp + 1) * weeks.width);

    weeks.cont = wg.bg
        .append("g")
        .attr("clip-path", "url(#clipwk)");


    go_week_menu(true);
}






/*----------------------
  -------- GRID --------
  ----------------------*/


// PRE: groups
function create_edt_grid() {
    create_grid_data();
    //go_grid(false);
}



function add_garbage(){

    if(slot_case) {
	
	var garbage_dsg = {
	    day: garbage.day,
	    start: garbage.start,
	    duration: rev_constraints[garbage.start],
	    display: false,
	    dispo: false,
	    pop: false,
	    reason: ""
	};
	
	data_slot_grid.push(garbage_dsg);

    }
}
function remove_garbage(){
    var found = false ;
    var i  = 0 ;
    while(!found && i < data_slot_grid.length){
	if (data_slot_grid[i].day == garbage.day
	    && data_slot_grid[i].slot == garbage.slot) {
	    found = true ;
	    data_slot_grid.splice(i,1);
	}
	i += 1 ;
    }
}


function create_grid_data() {
    if(fetch.constraints_ok && fetch.groups_ok) {
	if (slot_case) {
	    for(var i = 0 ; i<days.length ; i++) {
		for (var s = 0; s < Object.keys(rev_constraints).length ; s++) {
		    var start = Object.keys(rev_constraints)[s] ;
		    if (start < time_settings.time.day_finish_time){
			var gs = {
			    day: days[i].ref,
			    start: +start,
			    duration: rev_constraints[start],
			    display: false,
			    dispo: false,
			    pop: false,
			    reason: ""
			};
			data_slot_grid.push(gs);
		    }
		}
	    }
	}
	
	for (var p = 0; p < set_promos.length; p++) {
            compute_promo_leaves(root_gp[p].gp);
	}
	
	
	if (slot_case) {
	    for (var s = 0; s < Object.keys(rev_constraints).length ; s++) {
		for (var r = 0; r < set_rows.length; r++) {
		    var start = Object.keys(rev_constraints)[s] ;
		    if (start < time_settings.time.day_finish_time) {
			var gscp = {
			    row: r,
			    start: start,
			    duration: rev_constraints[start],
			    name: set_promos_txt[row_gp[r].promos[0]]
			} ;
			for (var p = 1; p < row_gp[r].promos.length; p++) {
			    gscp.name += "|";
			    gscp.name += set_promos_txt[row_gp[r].promos[p]];
			}
			data_grid_scale_row.push(gscp);
		    }
		}
	    }
	}
	
    }
}


/*----------------------
  -------- SCALE -------
  ----------------------*/

function create_but_scale() {
    def_drag_sca();

    var grp = fg
        .append("g")
        .attr("class", "h-sca")
        .attr("cursor", "pointer")
        .call(drag_listener_hs);

    grp
        .append("rect")
        .attr("fill", "darkslategrey")
        .attr("x", but_sca_h_x())
        .attr("y", but_sca_h_y())
        .attr("width", but_sca_thick())
        .attr("height", but_sca_long());

    grp
        .append("path")
        .attr("d", but_sca_tri_h(0))
        .attr("stroke", "white")
        .attr("fill", "white");



    grp = fg
        .append("g")
        .attr("class", "v-sca")
        .attr("cursor", "pointer")
        .call(drag_listener_vs);
    grp
        .append("rect")
        .attr("fill", "darkslategrey")
        .attr("x", but_sca_v_x())
        .attr("y", but_sca_v_y())
        .attr("width", but_sca_long())
        .attr("height", but_sca_thick());

    grp
        .append("path")
        .attr("d", but_sca_tri_v(0))
        .attr("stroke", "white")
        .attr("fill", "white");


}


function def_drag_sca() {
    drag_listener_hs = d3.drag()
        .on("start", function(c) {
            if (fetch.done) {
                drag.sel = d3.select(this);
                drag.x = 0;
                drag.y = 0;
                drag.svg = d3.select("#edt-main");
                drag.svg_w = +drag.svg.attr("width");
                drag.init = +drag.sel.select("rect").attr("x");
                dg.node().appendChild(drag.sel.node());


                drag.sel
                    .append("g")
                    .attr("class", "h-sca-l")
                    .append("line")
                    .attr("x1", drag.init)
                    .attr("y1", 0)
                    .attr("x2", drag.init)
                    .attr("y2", grid_height())
                    .attr("stroke", "black")
                    .attr("stroke-width", 2)
                    .attr("stroke-dasharray", "21,3,3,3");

            }
        })
        .on("drag", function(c) {
            if (fetch.done) {
                drag.x += d3.event.dx;
                if (drag.x + drag.init > 0) {
                    drag.sel.attr("transform", "translate(" + drag.x + "," + drag.y + ")");
                    if (drag.init + drag.x + margin.left + margin.right > drag.svg_w) {
                        drag.svg.attr("width", drag.init + drag.x + margin.left + margin.right);
                    }
                }
            }
        })
        .on("end", function(c) {
            if (fetch.done) {
                if (drag.x + drag.init <= 0) {
                    drag.x = -drag.init;
                }
                drag.sel.attr("transform", "translate(0,0)");
                drag.sel.select("rect").attr("x", drag.init + drag.x);
                if (rootgp_width != 0) {
                    labgp.width = ((drag.x + drag.init) / nbPer - dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) / rootgp_width;
                }
                drag.sel.select("path").attr("d", but_sca_tri_h(0));
                //(drag.x+drag.init)/(grid_width());
                go_edt(false);
                fg.node().appendChild(drag.sel.node());
                drag.sel.select(".h-sca-l").remove();
            }
        });

    drag_listener_vs = d3.drag()
        .on("start", function(c) {
            if (fetch.done) {
                drag.sel = d3.select(this);
                drag.x = 0;
                drag.y = 0;
                drag.init = +drag.sel.select("rect").attr("y");
                dg.node().appendChild(drag.sel.node());
                drag.svg = d3.select("#edt-main")
                drag.svg_h = +drag.svg.attr("height"); //+200;

                drag.sel
                    .append("g")
                    .attr("class", "v-sca-l")
                    .append("line")
                    .attr("x1", 0)
                    .attr("y1", drag.init)
                    .attr("x2", but_sca_h_mid_x())
                    .attr("y2", drag.init)
                    .attr("stroke", "black")
                    .attr("stroke-width", 2)
                    .attr("stroke-dasharray", "21,3,3,3");

            }
        })
        .on("drag", function(c) {
            if (fetch.done) {
                drag.y += d3.event.dy;
                if (drag.init + drag.y >= 0) {
                    drag.sel.attr("transform",
				  "translate(" + drag.x + "," + drag.y + ")");
                    drag.svg.attr("height", drag.svg_h + drag.y);
                }
            }
        })
        .on("end", function(c) {
            if (fetch.done) {
                if (drag.init + drag.y < 0) {
                    drag.y = -(drag.init);
                }
                scale = scale_from_grid_height(drag.init + drag.y) ;
                drag.sel.attr("transform", "translate(0,0)");
                drag.sel.select("rect").attr("y", grid_height());
		drag.sel.select("path").attr("d", but_sca_tri_v(0));
                go_edt(false);
                fg.node().appendChild(drag.sel.node());
                drag.sel.select(".v-sca-l").remove();

		svg.height = svg_height() ;
		d3.select("#edt-main").attr("height", svg.height);

            }
        });

}



/*----------------------
  ------- GROUPS -------
  ----------------------*/

// Only for the current case
function set_butgp() {
    var topx = 0 ;//615 + 4*30;

    var cur_buty = 0 ;
    var cur_rootgp ;
    for (var nrow=0 ; nrow<set_rows.length ; nrow++) {
	var cur_maxby = 0 ;
	var tot_row_gp = 0 ;
	var cur_butx = topx ;
        
	for (var npro=0 ; npro<row_gp[nrow].promos.length ; npro++){
	    cur_rootgp = root_gp[row_gp[nrow].promos[npro]] ;
	    cur_rootgp.buty = cur_buty ;
	    if (cur_rootgp.maxby > cur_maxby) {
		cur_maxby = cur_rootgp.maxby ; 
	    }
	    tot_row_gp += cur_rootgp.gp.width*butgp.width ;
	    tot_row_gp += (npro==0)?0:(margin_but.hor) ;
            console.log(cur_rootgp.gp.width, butgp.width);
	    cur_rootgp.butx = cur_butx ;
            cur_butx += margin_but.hor + cur_rootgp.gp.width*butgp.width ;
	}
	cur_buty += margin_but.ver + cur_maxby*butgp.height ;
    }


    // Compute dimensions of the group selection popup
    
    var minx, maxx, miny, maxy, curminx, curmaxx, curminy, curmaxy, curp ;
    
    for (var p = 0; p < set_promos.length; p++) {
        curp = root_gp[p] ;
        curminx = curp.butx ;
        curminy = curp.buty ;
        if(p==0 || curminx<minx) {
            minx = curminx ;
        }
        if(p==0 || curminy<miny) {
            miny = curminy ;
        }
        curmaxx = curminx + curp.gp.bw * butgp.width ;
        curmaxy = curminy + curp.maxby * butgp.height ;
        if(p==0 || curmaxx>maxx) {
            maxx = curmaxx ;
        }
        if(p==0 || curmaxy>maxy) {
            maxy = curmaxy ;
        }
    }

    sel_popup.groups_w = maxx-minx ;
    sel_popup.groups_h = maxy-miny ;

}



function indexOf_promo(promo) {
    for (var p = 0 ; p < set_promos.length ; p++ ) {
	if (set_promos[p] == promo_init ) {
	    return p ;
	}
    }
    return -1 ;
}

function go_promo_gp_init(button_available) {
    var gp_2_click = [] ;
    var found_gp, gpk, gpc, gpa ;

    promo_init = indexOf_promo(promo_init) ;
    if (promo_init >= 0){
	if (gp_init == "") {
	    gp_init = root_gp[promo_init].gp.nom ;
	}
	if (Object.keys(groups[promo_init]).map(function(g) { return groups[promo_init][g].nom ; }).indexOf(gp_init) != -1) {
	    apply_gp_display(groups[promo_init][gp_init], true, button_available);
	}
    } else if (gp_init != "") {
	if (Object.keys(groups[0]).map(function(g) { return groups[0][g].nom ; }).indexOf(gp_init) != -1) {
	    apply_gp_display(groups[0][gp_init], true, button_available);
	}
    }
}


function create_groups(data_groups) {
    var root ;
    
    extract_all_groups_structure(data_groups);

    for (var r = 0; r < set_rows.length; r++) {
        for (var p = 0; p < row_gp[r].promos.length; p++) {
            root = root_gp[row_gp[r].promos[p]].gp;
            create_static_att_groups(root);
        }
    }
    
    update_all_groups();

    for (var r = 0; r < set_rows.length; r++) {
        for (var p = 0; p < row_gp[r].promos.length; p++) {
            root = root_gp[row_gp[r].promos[p]];
            root.minx = root.gp.x ;
        }
    }
    for (var p = 0 ; p < set_promos.length ; p++) {
        var keys = Object.keys(groups[p]) ;
        for (var g = 0 ; g < keys.length ; g++) {
            groups[p][keys[g]].bx = groups[p][keys[g]].x ;
            groups[p][keys[g]].bw = groups[p][keys[g]].width ;
        }
    }
    
    set_butgp();
}


function extract_all_groups_structure(r) {
    var init_nbPromos = r.length;
    for (var npro = 0; npro < init_nbPromos; npro++) {
        extract_groups_structure(r[npro], -1, -1);
    }
    var sorted_rows = set_rows.sort() ;
    for(var npro = 0 ; npro<set_promos.length ; npro++){
	root_gp[npro].row = sorted_rows.indexOf(set_rows[root_gp[npro].row]) ;
    }
    set_rows = sorted_rows ;
}

function extract_groups_structure(r, npro, nrow) {
    var gr = {
        nom: r.name,
        ancetres: null,
        descendants: null,
        display: true,
        parent: null,
        children: null,
        x: 0,
        maxx: 0,
        width: 0,
        est: 0,
        lft: 0,
    }

    if ("undefined" === typeof r.buth) {
        gr.buth = 1;
    } else {
        gr.buth = r.buth * .01;
    }

    if ("undefined" === typeof r.buttxt) {
        gr.buttxt = gr.nom;
    } else {
        gr.buttxt = r.buttxt;
    }
    

    if (r.parent == "null") {

        // promo number should be unique
        set_promos.push(r.promo);
        set_promos_txt.push(r.promotxt);

        npro = set_promos.indexOf(r.promo);


        // promo number should be unique
        groups[npro] = [];
        root_gp[npro] = {};


        root_gp[npro].gp = gr;

        if (set_rows.indexOf(r.row) == -1) {
            set_rows.push(r.row);
            row_gp[set_rows.indexOf(r.row)] = {};
            row_gp[set_rows.indexOf(r.row)].promos = [];
        }
        nrow = set_rows.indexOf(r.row);

        root_gp[npro].row = nrow;

        row_gp[nrow].promos.push(npro);

    } else {
        gr.parent = r.parent;
    }

    gr.promo = npro;


    if ("undefined" === typeof r.children || r.children.length == 0) {
        gr.children = [];
    } else {
        gr.children = r.children.map(function(d) {
            return d.name;
        });
        for (var i = 0; i < r.children.length; i++) {
            extract_groups_structure(r.children[i], npro, nrow);
        }
    }
    groups[npro][gr.nom] = gr;
}



function create_static_att_groups(node) {
    var child;

    if (node.parent == null) {
        node.by = 0;
	root_gp[node.promo].maxby = node.by + node.buth ;
    } else {
	if (node.by + node.buth > root_gp[node.promo].maxby) {
	    root_gp[node.promo].maxby = node.by + node.buth ;
	}
    }
    node.descendants = [];


    if (node.children.length != 0) {
        for (var i = 0; i < node.children.length; i++) {
            child = groups[node.promo][node.children[i]];
            child.by = node.by + node.buth;
            create_static_att_groups(child);
        }
    }

}


// Earliest Starting Time (i.e. leftest possible position)
// for a node and its descendance, given node.est
function compute_promo_est_n_wh(node) {
    var child;


    if (node.parent == null) {
        node.ancetres = [];
    }
    node.descendants = [];


    node.width = 0;
    if (node.children.length == 0) {
	if (node.display) {
            node.width = 1;
	} else {
            node.width = 0;
	}
    } else {
        for (var i = 0; i < node.children.length; i++) {
            child = groups[node.promo][node.children[i]];
            child.est = node.est + node.width;
            if (!child.display) {
                child.width = 0;
            } else {
                child.ancetres = node.ancetres.slice(0);
                child.ancetres.push(node.nom);
                compute_promo_est_n_wh(child);
                node.descendants = node.descendants.concat(child.descendants);
                node.descendants.push(child.nom);
            }
            node.width += child.width;
        }
    }
}

// Latest Finishing Time (i.e. rightest possible position)
// for a node and its descendance, given node.lft
function compute_promo_lft(node) {
    var child;
    var eaten = 0;
    for (var i = node.children.length - 1; i >= 0; i--) {
        child = groups[node.promo][node.children[i]];
        child.lft = node.lft - eaten;
        compute_promo_lft(child);
        eaten += child.width;
    }
}


// Least Mobile X 
function compute_promo_lmx(node) {
    var child;

    //    console.log(node.promo,node.nom,node.x,node.maxx);

    if (node.x < node.est) {
        node.x = node.est;
    }
    if (node.x + node.width > node.lft) {
        node.x = node.lft - node.width;
    }

    if (node.children.length == 0) {
        node.maxx = node.x + node.width;
    } else {
        var lastmax = node.x;
        var lastmin = -1;
        for (var i = 0; i < node.children.length; i++) {
            child = groups[node.promo][node.children[i]];
            if (child.display) {
                if (child.x < lastmax) {
                    child.x = lastmax;
                }
                compute_promo_lmx(child);
                if (lastmin == -1) {
                    lastmin = child.x;
                }
                lastmax = child.maxx;
            }
        }
        if (node.display) {
            node.maxx = lastmax;
            node.x = lastmin;
        }
    }
}



function update_all_groups() {
    var max_rw = 0;
    var cur_rw, root, disp;

    // compute EST and width, and compute display row
    for (var r = 0; r < set_rows.length; r++) {
        cur_rw = 0;
        disp = false;
        for (var p = 0; p < row_gp[r].promos.length; p++) {
            root = root_gp[row_gp[r].promos[p]].gp;
            root.est = cur_rw;
            compute_promo_est_n_wh(root);
            cur_rw += root.width;
            if (root.display) {
                row_gp[r].display = true;
            }
        }
        if (cur_rw > max_rw) {
            max_rw = cur_rw;
        }
    }
    rootgp_width = max_rw;

    if (rootgp_width > 0) {
        if (pos_rootgp_width == 0) {
            pos_rootgp_width = rootgp_width;
        }
        labgp.width *= pos_rootgp_width / rootgp_width;
        pos_rootgp_width = rootgp_width;
    }



    // compute LFT
    for (var r = 0; r < set_rows.length; r++) {
        cur_rw = max_rw;
        for (var p = row_gp[r].promos.length - 1; p >= 0; p--) {
            root = root_gp[row_gp[r].promos[p]].gp;
            root.lft = cur_rw;
            compute_promo_lft(root);
            cur_rw -= root.width;
        }
    }
    // move x if necessary
    for (var r = 0; r < set_rows.length; r++) {
        cur_rw = 0;
        for (var p = 0; p < row_gp[r].promos.length; p++) {
            root = root_gp[row_gp[r].promos[p]].gp;
            if (root.x < cur_rw) {
                root.x = cur_rw;
            }
            compute_promo_lmx(root);
            cur_rw = root.maxx;
        }
    }

    // move y if necessary
    nbRows = 0;
    for (var r = 0; r < set_rows.length; r++) {
        root = row_gp[r];
        root.display = false;
        root.y = nbRows;
        for (var p = 0; p < row_gp[r].promos.length; p++) {
            root.display = root.display || root_gp[root.promos[p]].gp.display;
        }
        if (root.display) {
            nbRows += 1;
        }
    }

    if (nbRows > 0) {
        if (pos_nbRows == 0) {
            pos_nbRows = nbRows;
        }
        scale *= pos_nbRows / nbRows;
        pos_nbRows = nbRows;
    }
}



// data related to leaves
function compute_promo_leaves(node) {
    var gp;

    if (node.children.length == 0) {
        for (var j = 0; j < nbPer; j++) {
            data_grid_scale_gp.push({
                day: j,
                gp: node
            });
        }
    }

    for (var i = 0; i < node.children.length; i++) {
        child = groups[node.promo][node.children[i]];
        compute_promo_leaves(child);
    }
}


/*--------------------
  ------ MENUS -------
  --------------------*/



function create_menus() {

    meg
        .attr("transform", "translate(" + menus.x + "," + menus.y + ")")
        .attr("text-anchor", "start")
        .attr("font-size", 18);

    meg
        .append("rect")
        .attr("class", "menu")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", menus.coled + menus.colcb)
        .attr("height", 160) //(Object.keys(ckbox).length+1)*menus.h)
        .attr("rx", 10)
        .attr("ry", 10);

    meg
        .append("rect")
        .attr("class", "menu")
        .attr("x", menus.dx)
        .attr("y", 0)
        .attr("width", menus.coled + menus.colcb)
        .attr("height", 160) //(Object.keys(ckbox).length+1)*menus.h)
        .attr("rx", 10)
        .attr("ry", 10);

    meg
        .append("text")
        .attr("x", menus.mx)
        .attr("y", menus.h - 10)
        .attr("fill", "black")
        .text("Cours :");

    meg
        .append("text")
        .attr("x", menus.mx + menus.dx)
        .attr("y", menus.h - 10)
        .attr("fill", "black")
        .text("Dispos :");

    go_menus();
}



/*---------------------
  ------- BKNEWS ------
  ---------------------*/

function create_regen() {
    vg
        .append("g")
        .attr("class", "ack-reg")
        .append("text");
}




function create_bknews() {
    var flash = fig
	.append("g")
	.attr("class", "flashinfo");


    flash
	.append("line")
	.attr("class","bot-bar")
        .attr("stroke", "black")
        .attr("stroke-width", 4)
        .attr("x1", 0)
        .attr("y1", bknews_bot_y())
        .attr("x2", grid_width())
        .attr("y2", bknews_bot_y());

    flash
	.append("line")
	.attr("class","top-bar")
        .attr("stroke", "black")
        .attr("stroke-width", 4)
        .attr("x1", 0)
        .attr("y1", bknews_top_y())
        .attr("x2", grid_width())
        .attr("y2", bknews_top_y());

    var fl_txt = flash
	.append("g")
	.attr("class","txt-info");


    
}


/*---------------------
  ------- QUOTES ------
  ---------------------*/

function create_quote() {
    vg
	.append("g")
	.attr("class", "quote")
	.append("text");

    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_quote,
        async: true,
        contentType: "text/csv",
        success: function(msg) {
            console.log(msg);

            var quotes = d3.csvParse(msg, translate_quote_from_csv);
	    if(quotes.length > 0){
		quote = quotes[0] ; 
	    } else {
		quote = '' ;
	    }
		
	    vg.select(".quote").select("text")
		.text(quote);


            show_loader(false);

        },
        error: function(msg) {
            console.log("error");
            show_loader(false);
        }
    });
}

function translate_quote_from_csv(d) {
    return d.txt;
}



/*----------------------
   ------ COURSES ------
  ----------------------*/


function def_drag() {
    var cur_over = null;
    var sl = null;
    dragListener = d3.drag()
        .on("start", function(c) {
	    cancel_cm_adv_preferences();
	    cancel_cm_room_tutor_change();
            if (ckbox["edt-mod"].cked && fetch.done) {

		// no data_slot_grid when uniline
                data_slot_grid.forEach(function(sl) {
                    fill_grid_slot(c, sl);
                });

		console.log(data_slot_grid);

                drag.x = 0;
                drag.y = 0;

                // raise the course to the drag layer
                drag.sel = d3.select(this);
                dg.node().appendChild(drag.sel.node());

            }
        })
        .on("drag", function(d) {
            if (ckbox["edt-mod"].cked && fetch.done) {
                cur_over = which_slot(drag.x +
				      parseInt(drag.sel.select("rect")
					       .attr("x")),
				      drag.y +
				      parseInt(drag.sel.select("rect")
					       .attr("y")),
				      d);
		console.log(cur_over.day, cur_over.start_time);

                if (!is_garbage(cur_over)) {
                    sl = data_slot_grid.filter(function(c) {
                        return c.day == cur_over.day
			    && c.start == cur_over.start_time;
                    });
                    if (sl != null && sl.length == 1) {
                        if (!sl[0].display) {
                            data_slot_grid.forEach(function(s) {
                                s.display = false;
                            });
                            sl[0].display = true;
                        }
                    }
                } else {
                    data_slot_grid.forEach(function(s) {
                        s.display = false;
                    });
                }
                go_grid(true);

                drag.x += d3.event.dx;
                drag.y += d3.event.dy;
                drag.sel.attr("transform", "translate(" + drag.x + "," + drag.y + ")");
            }
        })
	.on("end", function(d) {

            // click => end. So if real drag
            if(drag.sel != null) {

            // lower the course to the middleground layer
            mg.node().appendChild(drag.sel.node());

            if (cur_over != null && ckbox["edt-mod"].cked && fetch.done) {

                data_slot_grid.forEach(function(s) {
                    s.display = false;
                });


                if (!is_garbage(cur_over)) {

		    console.log("not garbage");
		    
                    // var gs = data_slot_grid.filter(function(s) {
                    //     return s.day == cur_over.day
		    // 	    && s.start == cur_over.start_time;
                    // });
		    
		    var warn_check = warning_check(d, cur_over.day, cur_over.start_time);
		    
		    
		    console.log(cur_over.day, cur_over.start_time/60);
		    console.log(warn_check);
		    
		    //                    if (ngs.dispo) {
		    if (warn_check == "") {

			add_bouge(d);
                        d.day = cur_over.day;
                        d.start = cur_over.start_time;
			room_tutor_change.course.push(d) ;
			compute_cm_room_tutor_direction() ;
			room_cm_level = 0 ;
			var disp_cont_menu = select_room_change() ;
			if (disp_cont_menu) {
			    go_cm_room_tutor_change();
			} else {
			    room_tutor_change.course = [] ;
			    room_tutor_change.proposal = [] ;
			}

		    } else  { //if (!ngs.dispo) {
			// -- no slot --
			// && (logged_usr.rights >> 2) % 2 == 1) {

			
			
			console.log(warn_check);

			var splash_violate_constraint ;

			if ((logged_usr.rights >> 2) % 2 == 1) {
			
			    splash_violate_constraint = {
				id: "viol_constraint",
				but: {
				    list: [{txt: "Confirmer",
					    click:
					    function(d){
						add_bouge(d.saved_data.course);
						d.saved_data.course.day = d.saved_data.grid_slot.day;
						d.saved_data.course.start = d.saved_data.grid_slot.start_time;
						go_grid(true);
						go_courses(true);
						return ;
					    },
					    saved_data:
					    {course: d,
					     grid_slot: {day: cur_over.day, start_time: cur_over.start_time}}
					   },
					   {txt: "Annuler",
					    click: function(d){
						return ;
					    }
					   }]
				},
				com: {list: [{txt: "Attention", ftsi: 23},
					     {txt: ""},
					     {txt: "Des privilèges vous ont été accordés, et vous en profitez pour outrepasser la contrainte suivante :"},
					     {txt: warn_check},
					     {txt: "Confirmer la modification ?"}]
				     }
			    }
			    splash(splash_violate_constraint);

			
			} else {
			    if (slot_case) {
				var gs = data_slot_grid.filter(function(s) {
				    return s.day == cur_over.day
		    			&& s.start == cur_over.start_time;
				});
				console.log(gs);
				if (gs.length==1) {
				    gs[0].pop = true;
				}
			    } else {
				splash_violate_constraint = {
				    id: "viol_constraint",
				    but: {
					list: [{txt: "Ah ok",
						click: function(d){
						    return ;
						}
					       }]
				    },
				    com: {list: [{txt: "Vous tentez d'outrepasser la contrainte suivante :", ftsi: 23},
						 {txt: warn_check},
						 {txt: "Vous n'avez pas les droits pour le faire..."}]
					 }
				}
				splash(splash_violate_constraint);
			    }
			    
			}
			
                    }
                } else {
                    d.day = cur_over.day ;
                    d.start = cur_over.start_time ;
		}

                drag.sel.attr("transform", "translate(0,0)");

                drag.x = 0;
                drag.y = 0;
                drag.sel = null;
                cur_over = null;

                go_grid(true);
                go_courses(true);
            }
            }
        });

    drag_popup = d3.drag()
        .on("start", function(d) {
            drag.sel = d3.select(this);
            drag.sel.raise() ;
        })
        .on("drag", function(d) {
            d.x += d3.event.dx;
            d.y += d3.event.dy;
            drag.sel.attr("transform", popup_trans(d));
        })
    // save pannel position
        .on("end", function(d) {
            var infos = sel_popup.get_available(d.type) ;
            if (typeof infos !== 'undefined') {
                infos.x = d.x ;
                infos.y = d.y ;
            }
            drag.sel = null ;
        });
}




function fill_grid_slot(c2m, grid_slot) {
    grid_slot.dispo = true;
    grid_slot.reason = "";

    // // the user has the right to do whatever s/he wants
    // if ((logged_usr.rights >> 2) % 2 == 1) {
    // 	return ;
    // }

    var check = check_course(c2m, {day:grid_slot.day, start_time:grid_slot.start});
    
    if (check.constraints_ok) {
	return ;
    } else {
	grid_slot.dispo = false;
	if (check.nok_type == 'stable') {
	    grid_slot.reason = "Cours fixe";
	} else if (check.nok_type == 'train_prog_unavailable') {
            grid_slot.reason = "CRENEAU NON DISPO POUR " + check.train_prog;
	} else if (check.nok_type == 'tutor_busy') {
            grid_slot.reason = "PB PROF OCCUPE";
	} else if (check.nok_type == 'group_busy') {
            grid_slot.reason = "PB GROUPE";
	} else if (check.nok_type == 'tutor_unavailable') {
            grid_slot.reason = "PB PROF PAS DISPO";
	} else if (check.nok_type == 'tutor_availability_unknown') {
            grid_slot.reason = "PB DISPO NON DECLAREE";
        }
	return ;
    }

}

function warning_check(c2m, day, start_time) {
    var ret = '';
    var check = check_course(c2m, {day:day, start_time:start_time});
    if (check.nok_type == 'stable') {
	ret = "Le cours était censé être fixe.";
    } else if (check.nok_type == 'train_prog_unavailable') {
        ret = "La promo " + check.train_prog + " ne devait pas avoir cours à ce moment-là.";
    } else if (check.nok_type == 'tutor_busy') {
        ret = "L'enseignant·e " + check.tutor + " avait déjà un cours prévu.";
    } else if (check.nok_type == 'group_busy') {
        ret = "Le groupe " + check.group + " avait déjà un cours prévu.";
    } else if (check.nok_type == 'tutor_unavailable') {
        ret = "L'enseignant·e " + check.tutor + " s'était déclaré·e indisponible.";
    } else if (check.nok_type == 'tutor_availability_unknown') {
        ret = "L'enseignant·e " + check.tutor + " n'a pas déclaré ses dispos.";
    }
    return ret ;
}



function simultaneous_courses(day, start_time, duration, id) {
    return cours.filter(function(c) {
        return (c.day == day 
		&& ((c.start < start_time+duration
		     && c.start >= start_time)
		    || (c.start + c.duration < start_time+duration
			&& c.start +c.duration > start_time)
		    || (c.start <= start_time
			&& c.start + c.duration > start_time + duration))
		&& c.id_cours != id);
    });
}

/*
 check whether it is possible to schedule c2m on slot slot, day day. 
 returns an object containing at least contraints_ok: true iff it is, and
 - nok_type: 'stable' -> course cannot be moved
 - nok_type: 'train_prog_unavailable', train_prog: abbrev_train_prog -> students
   from training programme abbrev_train_prog are not available
 - nok_type: 'tutor_busy', tutor: tutor_username -> the tutor has already
   another course
 - nok_type: 'group_busy', group: gp_name -> the group has already another course
 - nok_type: 'tutor_unavailable', tutor: tutor_username -> the tutor is 
   unavailable
*/
// c2m element of course
// date {day, start_time}
function check_course(c2m, date) {

    var ret = {constraints_ok: false};
    var possible_conflicts = [] ;
    var conflicts = [] ;


    if (is_garbage(date)) {
	ret.constraints_ok = true ;
	return ret ;
    }

    // if ((logged_usr.rights >> 2) % 2 == 1) {
    // 	return ;
    // }

    if (c2m.id_cours == -1) {
	ret.nok_type = 'stable' ;
	return ret;
    }

    if (is_free(date, c2m.promo)) {
	ret.nok_type = 'train_prog_unavailable' ;
	ret.train_prog = set_promos[c2m.promo] ;
        return ret;
    }


    possible_conflicts = simultaneous_courses(date.day,
					      date.start_time,
					      c2m.duration,
					      c2m.id_cours) ;

    // console.log("CHECK", c2m, date);
    // console.log(possible_conflicts.map(function(d){return {s:d.start, d:d.duration}}));

    conflicts = possible_conflicts.filter(function(c) {
        return (c.prof == c2m.prof);
    });
    
    if (conflicts.length > 0) {
	ret.nok_type = 'tutor_busy';
	ret.tutor = c2m.prof;
        return ret;
    }


    conflicts = possible_conflicts.filter(function(c) {
        return ((c.group == c2m.group
		 || groups[c2m.promo][c2m.group].ancetres.indexOf(c.group) > -1
		 || groups[c2m.promo][c2m.group].descendants.indexOf(c.group) > -1)
		&& c.promo == c2m.promo);
    });
    
    if (conflicts.length > 0) {
	ret.nok_type = 'group_busy';
	ret.group = c2m.group;
        return ret;
    }

    if (dispos[c2m.prof] !== undefined) {
        var pref_tut = get_preference(date.day, date.start_time, c2m.duration,
			              c2m.prof);
	if (pref_tut == 0) {
	    ret.nok_type = 'tutor_unavailable' ;
	    ret.tutor = c2m.prof ;
            return ret;
	} else if (pref_tut == -1) {
	    ret.nok_type = 'tutor_availability_unknown' ;
	    ret.tutor = c2m.prof ;
            return ret;
        }
    }

    ret.constraints_ok = true ;
    return ret ;

}

function which_slot(x, y, c) {
    var wday = (rootgp_width * labgp.width +
        dim_dispo.plot *
        (dim_dispo.width + dim_dispo.right));
    var iday = Math.floor((x + .5 * cours_width(c)) / wday);
    return {
        day: days[iday].ref,
        start_time: indexOf_constraints(c, y) // day-independent
    };
}

// date {day, start_time}
function is_garbage(date) {
    var t = time_settings.time ;
    return (date.start_time < t.day_start_time
	    || date.start_time >= t.day_finish_time) ;
}

function is_free(date, promo) {
    return false ;
//    return (promo < 2 && (day == 3 && hour > 2));
}

// find the closest possible start_time in the current day,
// in terms of distance on the screen
function indexOf_constraints(c, y){
    var course_duration_y = c.duration * nbRows * scale ;
    var cst = constraints[c.c_type].allowed_st.map(
	function(d){
	    return {y:cours_y({
		start:d,
		promo:c.promo,
	    }),
		    start:d};
	}
    );
    var t = time_settings.time ;
    
    var after = false ;
    var i = 0 ;
    while(! after && i < cst.length) {
	if (cst[i].y > y) {
	    after = true ;
	} else {
	    i ++ ;
	}
    }
    if (i==cst.length) {
	if (y < cst[cst.length-1].y + course_duration_y) {
	    return cst[cst.length-1].start ;
	} else {
	    return t.day_finish_time ;
	}
    } else if (i==0) {
	// if (y < 0 - course_duration_y) {
	//     return t.day_start_time - c.duration ;
	// } else {
	    return t.day_start_time ;
	// }
    } else {
	if (y - cst[i-1].y > cst[i].y - y) {
	    return cst[i].start;
	} else {
	    return cst[i-1].start;
	}
    }
}


/*---------------------
  ------- ROOMS -------
   ---------------------*/

function clean_unavailable_rooms() {
    unavailable_rooms = {} ;
}


/*--------------------
  ------- TUTORS -----
  --------------------*/


/*---------------------
  ------- VALIDER -----
  ---------------------*/

function create_val_but() {

    edt_but = vg
        .append("g")
        .attr("but", "edt")
        .on("mouseover", but_bold)
        .on("mouseout", but_back)
        .on("click", confirm_change)
        .attr("cursor", "pointer");

    edt_but
        .append("rect")
        .attr("width", valid.w)
        .attr("height", valid.h)
        .attr("fill", "steelblue")
        .attr("stroke", "black")
        .attr("stroke-width", 2)
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", menus.x + menus.mx - 5)
        .attr("y", did.tly);

    edt_but
        .append("text")
        .attr("font-size", 18)
        .attr("fill", "white")
        .text("Valider EdT")
        .attr("x", menus.x + menus.mx + .5 * valid.w)
        .attr("y", did.tly + .5 * valid.h);

    edt_but.attr("visibility", "hidden");


    edt_message = vg
        .append("g")
        .attr("message", "edt");

    edt_message
        .append("rect")
        .attr("width", menus.coled + menus.colcb)
        .attr("height", 30)
        .attr("fill", "white")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1)
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", menus.x)
        .attr("y", did.tly + 94);

    edt_message
        .append("g")
        .attr("class", "ack-edt")
        .append("text")
        .attr("x", menus.x + (menus.coled + menus.colcb) * 0.5)
        .attr("y", did.tly + 94 + 15);

    edt_message.attr("visibility", "hidden");

}




/*--------------------
   ------ STYPE ------
  --------------------*/

function create_stype() {
    var t, dat, datdi, datsmi;

    // -- no slot --
    // --  begin  --
    // TO BE CHECKED: fill missing preferences if needed

    // sometimes, all preferences are not in the database
    // -> by default, not available

    // --   end   --
    // -- no slot --

    
    dat = stg.selectAll(".dispot")
        .data(user.dispos_type);

    datdi = dat
        .enter()
        .append("g")
        .attr("class", "dispot")
        .attr("transform", "translate(" +
            did.tlx + "," +
            did.tly + ")");

    var datdisi = datdi
        .append("g")
        .attr("class", "dispot-si");



    datdisi
        .append("rect")
        .attr("class", "dispot-bg")
        .attr("stroke", "#555555")
        .attr("stroke-width", 1)
        .attr("fill", function(d) {
            return smi_fill(d.val / par_dispos.nmax);
        })
        .attr("width", dispot_w)
        .attr("height", dispot_h)
        .attr("x", dispot_x)
        .attr("y", dispot_y)
        .attr("fill", function(d) {
            return smi_fill(d.val / par_dispos.nmax);
        });

    datdisi
        .append("line")
        .attr("stroke", "#555555")
        .attr("stroke-width", 2)
        .attr("x1", 0)
        .attr("y1", gsclbt_y)
        .attr("x2", gsclbt_x)
        .attr("y2", gsclbt_y);

    stg.attr("visibility", "hidden");

    var dis_but = stg
        .append("g")
        .attr("but", "dis")
        .on("mouseover", but_bold)
        .on("mouseout", but_back)
        .on("click", send_dis_change)
        .attr("cursor", "pointer");

    dis_but
        .append("rect")
        .attr("width", valid.w)
        .attr("height", valid.h)
        .attr("fill", "steelblue")
        .attr("stroke", "black")
        .attr("stroke-width", 2)
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", did.tlx)
        .attr("y", did.tly);

    dis_but
        .append("text")
        .attr("font-size", 18)
        .attr("fill", "white")
        .text("Valider disponibilités")
        .attr("x", did.tlx + .5 * valid.w)
        .attr("y", did.tly + .5 * valid.h);

    var stap_but = stg
        .append("g")
        .attr("but", "st-ap")
        .on("mouseover", st_but_bold)
        .on("mouseout", st_but_back)
        .on("click", apply_stype)
        .attr("cursor", st_but_ptr);

    stap_but
        .append("rect")
        .attr("width", stbut.w)
        .attr("height", stbut.h)
        .attr("x", dispot_but_x)
        .attr("y", dispot_but_y("app"))
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("fill", "steelblue")
        .attr("stroke", "black")
        .attr("stroke-width", 2);

    stap_but
        .append("text")
        .attr("font-size", 18)
        .attr("fill", "white")
        .attr("x", dispot_but_txt_x)
        .attr("y", dispot_but_txt_y("app") - 10)
        .text("Appliquer");

    stap_but
        .append("text")
        .attr("font-size", 18)
        .attr("fill", "white")
        .attr("x", dispot_but_txt_x)
        .attr("y", dispot_but_txt_y("app") + 10)
        .text("Semaine type");

}



function fetch_dispos_type() {
    if (user.nom != "") {
        show_loader(true);
        $.ajax({
            type: "GET", //rest Type
            dataType: 'text',
            url: url_fetch_stype,
            async: true,
            contentType: "text/csv",
            success: function(msg) {
                user.dispos_type = [] ;

                user.dispos_type = d3.csvParse(msg, translate_dispos_type_from_csv);
                create_stype();
                show_loader(false);
            },
            error: function(xhr, error) {
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
}


function translate_dispos_type_from_csv(d) {
    return {
        day: d.day,
	start_time: +d.start_time,
	duration: +d.duration,
        val: +d.valeur,
        off: -1
    };
}

// -- no slot --
// --  begin  --
// to be extended: intervals could be different
// dt {day, start_time}
function get_dispos_type(dt) {
    var s = user.dispos_type.filter(function(d){
	return d.day==dt.day && d.start_time==dt.start_time;
    });
    if (s.length!=1) {
	return null;
    } else {
	return s[0];
    }
}
// --   end   --
// -- no slot --




/*--------------------
   ------ ALL ------
   --------------------*/

// function cm_room_launch(d) {
//     if (ckbox["edt-mod"].cked) {
// 	d3.event.preventDefault();
// 	context_menu.room_tutor_hold = true ;
// 	compute_cm_room_tutor_direction();
// 	select_room_change(d);
// 	go_cm_room_tutor_change();
//     }
// }

function select_entry_cm(d) {
    room_tutor_change.cm_settings = entry_cm_settings;
    room_tutor_change.course = [d];
    var fake_id = new Date() ;
    fake_id = fake_id.getMilliseconds() + "-" + d.id_cours ;
    room_tutor_change.proposal = [{fid:fake_id,
				   content:"Prof"},
				   {fid:fake_id,
				    content:"Salle"}] ;
}




function def_cm_change() {
    entry_cm_settings.click = function(d) {
	context_menu.room_tutor_hold = true ;
	if(d.content == 'Salle') {
	    room_cm_level = 0 ;
	    select_room_change();
	} else {
	    select_tutor_module_change();
	}
	go_cm_room_tutor_change();
    };
    
    tutor_module_cm_settings.click = function(d) {
	context_menu.room_tutor_hold = true ;
	if(d.content == '+') {
	    select_tutor_filters_change();
	} else {
	    confirm_tutor_change(d);
	}
	go_cm_room_tutor_change();
    };

    tutor_filters_cm_settings.click = function(d) {
	context_menu.room_tutor_hold = true ;
	select_tutor_change(d);
	go_cm_room_tutor_change();
    };
    
    tutor_cm_settings.click = function(d) {
	context_menu.room_tutor_hold = true ;
	if (d.content == arrow.back) {
	    select_tutor_filters_change();
	} else {
	    confirm_tutor_change(d);
	}
	go_cm_room_tutor_change();
    };

    for (var level = 0 ; level<room_cm_settings.length ; level++) {
	room_cm_settings[level].click = function(d) {
	    context_menu.room_tutor_hold = true ;
	    if(d.content == '+') {
		room_cm_level += 1 ;
		select_room_change();
	    } else {
		confirm_room_change(d) ;
	    }
	    go_cm_room_tutor_change();
	}
    }

}


// buttons to open selection view
function create_selections() {

    var avg = catg
        .selectAll(".gen-selection")
        .data(sel_popup.available);

    var contg = avg
        .enter()
        .append("g")
        .attr("class", "gen-selection")
        .attr("transform", sel_trans)
        .attr("cursor", "pointer")
        .on("click", add_pannel);
    
    contg
        .append("rect")
        .attr("width", sel_popup.selw)
        .attr("height", sel_popup.selh)
        .attr("rx", 5)
        .attr("ry", 10)
        .attr("fill", "forestgreen")
        .attr("x", 0)
        .attr("y", 0);

    contg
        .append("text")
        .text(but_open_sel_txt)
        .attr("x", .5 * sel_popup.selw)
        .attr("y", .5 * sel_popup.selh);

    var forall = catg
        .append("g")
        .attr("class", "sel_forall")
        .attr("transform", sel_forall_trans())
        .attr("cursor", "pointer")
        .on("click", apply_cancel_selections);
    
    forall
        .append("rect")
        .attr("width", .5*sel_popup.selw)
        .attr("height", sel_popup.selh)
        .attr("class", "select-highlight")
        .attr("rx", 5)
        .attr("ry", 10)
        .attr("x", 0)
        .attr("y", 0);

    forall
        .append("text")
        .text("\u2200")
        .attr("x", .25*sel_popup.selw)
        .attr("y", .5*sel_popup.selh);

}

// add data related to a new filter pannel if not
// already present
function add_pannel(d) {

    var same = sel_popup.pannels.find(function(p) {
        return p.type == d.type ;
    }) ;

    if(typeof same === 'undefined') {
        var title = "" ;
        var px = sel_popup.x;
        var py = sel_popup.y;
        var infos = sel_popup.get_available(d.type) ;
        if (typeof infos !== 'undefined') {
            title = infos.buttxt ;
            px = infos.x ;
            py = infos.y ;
        }
        var pannel = {type: d.type,
                      x: px,
                      y: py,
                      list: popup_data(d.type),
                      txt: title};

        sel_popup.pannels.push(pannel);
        
        go_selection_popup();

        if (pannel.type == "group") {
            go_gp_buttons() ;
        }
    }
}

// returns the data related to a given filter type
function popup_data(type) {
    switch(type) {
    case "tutor":
        return tutors.all ;
    case "module":
        return modules.all ;
    case "room":
        return rooms_sel.all ;
    default:
        return [] ;
    }
}


// refreshes filter pannels
function go_selection_popup(){
    
    var bound = selg
        .selectAll(".sel-pop-g")
        .data(sel_popup.pannels, function(p) {
            return p.type ;
        }) ;


    var g_new = bound
        .enter()
        .append("g")
        .attr("class", "sel-pop-g")
        .attr("id", popup_pannel_type_id)
        .call(drag_popup);

    g_new
        .merge(bound)
        .attr("transform", popup_trans);

    var bg_new = g_new
        .append("rect")
        .attr("class", "sel-pop-bg")
        .attr("x",  - sel_popup.mar_side )
        .attr("y",  - (sel_popup.mar_side + but_exit.side + but_exit.mar_next))
        .attr("width", popup_bg_w);
    
    bg_new
        .merge(bound.select(".sel-pop-bg"))
        .attr("height", popup_bg_h);

    var exit_new = g_new
        .append("g")
        .attr("class", "sel-pop-exit")
        .attr("cursor", "pointer");

    exit_new
        .merge(bound.select(".sel-pop-exit"))
        .attr("transform", popup_exit_trans)
        .on("click", remove_pannel);

    exit_new
        .append("rect")
        .attr("stroke", "none")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", but_exit.side)
        .attr("height", but_exit.side);

    exit_new
        .append("line")
        .attr("stroke","black")
        .attr("stroke-width", 4)
        .attr("x1", but_exit.mar_side)
        .attr("y1", but_exit.mar_side)
        .attr("x2", but_exit.side-but_exit.mar_side)
        .attr("y2", but_exit.side-but_exit.mar_side);

    exit_new
        .append("line")
        .attr("stroke","black")
        .attr("stroke-width", 4)
        .attr("x1", but_exit.mar_side)              
        .attr("y1", but_exit.side-but_exit.mar_side)
        .attr("x2", but_exit.side-but_exit.mar_side)              
        .attr("y2", but_exit.mar_side);


    g_new
        .append("text")
        .text(popup_title_txt)
        .attr("class", "popup-title")
        .attr("x", popup_title_x)
        .attr("y", popup_title_y);
    

    var contg = g_new
        .filter(function(p){
            return p.type != "group" ;
        })
        .append("g")
        .attr("class", "sel-pop-all")
        .attr("cursor", "pointer")
        .on("click", apply_selection_display_all);
    
    contg
        .append("rect")
        .attr("width", popup_all_w)
        .attr("height", popup_all_h)
        .attr("class", "select-highlight")
        .attr("rx", 5)
        .attr("ry", 10)
        .attr("x", 0)
        .attr("y", 0);

    contg
        .append("text")
        .text("\u2200")
        .attr("x", popup_all_txt_x)
        .attr("y", popup_all_txt_y);

    bound.exit().remove() ;

    go_selection_buttons();

}
