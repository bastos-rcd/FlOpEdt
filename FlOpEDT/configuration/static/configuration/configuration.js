
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
                    $('#dropdown_dpt_5').append($('<option>', option));
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
    var selectPlanifDept = document.getElementById("dropdown_dpt_5");
    let selectedDepartmentAbbrev = selectPlanifDept.options[selectPlanifDept.selectedIndex].value;
    let selectTrainingPeriods = document.getElementById("dropdown_training_periods");
    selectTrainingPeriods.innerHTML = '';
    for (let training_period of training_periods) {
        if (training_period.department === selectedDepartmentAbbrev) {
            let opt = document.createElement('option');
            opt.value = training_period.name;
            opt.innerHTML = training_period.name;
            selectTrainingPeriods.appendChild(opt);
        }
    }
    let selectSchedulingPeriods = document.getElementById("dropdown_scheduling_periods");
    selectSchedulingPeriods.innerHTML = '';
    for (let scheduling_period of scheduling_periods) {
        if (scheduling_period.department === selectedDepartmentAbbrev) {
            let opt = document.createElement('option');
            opt.value = scheduling_period.name;
            opt.innerHTML = scheduling_period.name;
            selectSchedulingPeriods.appendChild(opt);
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
let schedulingPeriodsDiv = document.getElementById("choose_scheduling_periods");
let schedulingPeriodsCheckbox = schedulingPeriodsDiv.querySelector("input[type=checkbox]");
let schedulingPeriodsInput = schedulingPeriodsDiv.querySelectorAll("input[type=number]");
schedulingPeriodsInput.forEach( (c) => {
        c.addEventListener('change', (event) => {
            schedulingPeriodsCheckbox.checked = true;
            scheduling_periods_text_pattern[c.id] = c.value;
            confirm_text.scheduling_periods = scheduling_periods_text_pattern.join(' ');
        })
})
schedulingPeriodsCheckbox.addEventListener('change', (event) => {
            if (schedulingPeriodsCheckbox.checked === true){
                confirm_text.scheduling_periods = scheduling_periods_text_pattern.join(' ');
            }
            else {
                confirm_text.scheduling_periods = translated_all;
            }
})

// Period div gesture
let trainingPeriodsDiv = document.getElementById("choose_training_periods");
let trainingPeriodsCheckbox = trainingPeriodsDiv.querySelector("input[type=checkbox]");
let trainingPeriodsInput = trainingPeriodsDiv.querySelectorAll("select");
trainingPeriodsInput.forEach( (c) => {
        c.addEventListener('change', (event) => {
            trainingPeriodsCheckbox.checked = true;
            confirm_text.training_periods = Array.from(c.selectedOptions).map(el => el.value);
        })
})
trainingPeriodsCheckbox.addEventListener('change', (event) => {
            if (trainingPeriodsCheckbox.checked === true){
                confirm_text.training_periods = Array.from(c.selectedOptions).map(el => el.value);
            }
            else {
                confirm_text.training_periods = translated_all;
            }
})

let selectPlanifDepartment = document.getElementById("dropdown_dpt_5");
selectPlanifDepartment.addEventListener('change', () => {
		handlePlanifDeptChanges();
		}
        )

init_departement_manager();
handlePlanifDeptChanges();
