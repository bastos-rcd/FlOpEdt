
function send_form(form) {
    $("#"+form).submit(function(event){
        event.preventDefault();
        let post_url = $(this).attr("action");
        let request_method = $(this).attr("method");
        let data = new FormData($("#"+form).get(0));
        let form_enctype = $(this).attr("enctype");
        show_loader(true);
        $.ajax({
            url : post_url,
            type: request_method,
            data : data,
            enctype : form_enctype,
            contentType: false,
            processData: false,
            cache: false,
            success: function (data) {
                if(data.status === "ok") {
                    tmp = "";
                    if (data.data instanceof Array) {
                        for (er of data.data) {
                        tmp += er + "<br>";
                    }
                    } else {
                        tmp = data.data;
                    }
                    $("#error_"+form+" p").html(tmp);
                } else {
                    var obj = $("#error_"+form+" p").text(data.data);
                    // FIXME : la ligne suivante doit pouvoir être amélioré avec `white-space: pre-line;` dans les css
                    //  Cf https://stackoverflow.com/questions/4535888/jquery-text-and-newlines
                    obj.html(obj.html().replace(/\n/g,'<br/>'));
                }
                var option = {value:data.dept_abbrev, text:data.dept_fullname} ;
                if (form == 'config') {
                    $('#dropdown_dpt_1').append($('<option>', option));
                    $('#dropdown_dpt_2').append($('<option>', option));
                }
                show_loader(false);
            },
            error: function (data) {
                console.log(data);
                $("#error_"+form+" p").text("Error");
                show_loader(false);
            },
        })
    });
}

send_form("config");
send_form("planif");

function handleRadioChanges(value) {
    if (value === "1") {
        document.getElementById("depart_choice").innerHTML = "" +
            "<tr><th><label for=\"id_nom\">Nom:</label></th><td><input type=\"text\" name=\"name\" required id=\"id_nom\"></td></tr>" +
            "<tr><th><label for=\"id_abbrev\">Abbrev:</label></th><td><input type=\"text\" name=\"abbrev\" maxlength=\"7\" required id=\"id_abbrev\"></td></tr>\n"
    } else if (value === "2") {
        opts = "";
        for(let dep of departements) {
            opts += "<option value='"+ dep.abbrev +"'>" + dep.name + "</option>\n"
        }
        document.getElementById("depart_choice").innerHTML = "" +
            "<select name='abbrev'>\n" +
            opts +
            "</select>"
    }
}


function handlePlanifDeptChanges() {
    var selectPlanifDept = document.getElementById("dropdown_dpt_2");
    let selectedDepartmentAbbrev = selectPlanifDept.options[selectPlanifDept.selectedIndex].value;
    let selectPeriods = document.getElementById("dropdown_periods");
    selectPeriods.innerHTML = '';
    for (let period of periods) {
        if (period.department === selectedDepartmentAbbrev) {
            let opt = document.createElement('option');
            opt.value = period.name;
            opt.innerHTML = period.name;
            selectPeriods.appendChild(opt);
        }
    }
    confirm_text.department = selectedDepartmentAbbrev;
}

function init_departement_manager() {
    rBut = document.querySelector("#config input[type=radio]:checked");
    if (rBut === null) {
        rBut = document.querySelector("#config input[type=radio]");
        rBut.checked = true
    }
    handleRadioChanges(rBut.value);
}

document.querySelectorAll("#config input[type=radio]").forEach((i) => {
    i.addEventListener('change', (event) => {
        handleRadioChanges(event.target.value);
    })
})


// Weeks div gesture
let weeksDiv = document.getElementById("choose_weeks");
let weeksCheckbox = weeksDiv.querySelector("input[type=checkbox]");
let weeksInput = weeksDiv.querySelectorAll("input[type=number]");
weeksInput.forEach( (c) => {
        c.addEventListener('change', (event) => {
            weeksCheckbox.checked = true;
            weeks_text_pattern[c.id] = c.value;
            confirm_text.weeks = weeks_text_pattern.join(' ');
        })
})
weeksCheckbox.addEventListener('change', (event) => {
            if (weeksCheckbox.checked === true){
                confirm_text.weeks = weeks_text_pattern.join(' ');
            }
            else {
                confirm_text.weeks = translated_all;
            }
})

// Period div gesture
let periodsDiv = document.getElementById("choose_periods");
let periodsCheckbox = periodsDiv.querySelector("input[type=checkbox]");
let periodsInput = periodsDiv.querySelectorAll("select");
periodsInput.forEach( (c) => {
        c.addEventListener('change', (event) => {
            periodsCheckbox.checked = true;
            confirm_text.periods = Array.from(c.selectedOptions).map(el => el.value);
        })
})
periodsCheckbox.addEventListener('change', (event) => {
            if (periodsCheckbox.checked === true){
                confirm_text.periods = Array.from(c.selectedOptions).map(el => el.value);
            }
            else {
                confirm_text.periods = translated_all;
            }
})

let selectPlanifDepartment = document.getElementById("dropdown_dpt_2");
selectPlanifDepartment.addEventListener('change', () => {
		handlePlanifDeptChanges();
		}
        )

init_departement_manager();
handlePlanifDeptChanges();
