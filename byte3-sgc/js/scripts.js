function updateTable(str) {
console.log("in update header");
console.log(str);
check = str.substr(0, 5);
console.log(check);

button = document.getElementById(str);
console.log(button.className);
if (button.className.includes("btn-info")) {
    button.className = "btn btn-space btn-primary";
} else {
    button.className = "btn btn-space btn-info";
     }
buttons = document.getElementById("buttonList").children;
cols = [];
for (button in buttons) {
    id = buttons[button].id;
    if (buttons[button].id != null) {
        var isPrimary = buttons[button].className.includes("btn-primary");
        if (isPrimary && (cols.indexOf(id) == -1)) {
        cols.push(id);
        }
    }
}
cleanButtons = document.getElementById("cleanButtonList").children;
cleanCols = [];
for (button in cleanButtons) {
    id = cleanButtons[button].id;
    if (cleanButtons[button].id != null) {
        var isPrimary = cleanButtons[button].className.includes("btn-primary");
        if (isPrimary && (cleanCols.indexOf(id) == -1)) {
        cleanCols.push(id);
        }
    }
}
console.log(JSON.stringify({'cols':cols,'cleanCols':cleanCols}));
console.log("Ajax Start");
$.ajax({
    url: '/_update_table',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify({'cols' : cols,'cleanCols':cleanCols}),
    type: 'POST',
    success: function (res, status) {
    console.log("successrunning");
    console.log(res['content']);
    console.log(res['headers']);
    var cols = res['headers'];
    var rows = res['content'];

    var cleanCols = res['cleanHeaders'];
    var cleanRows = res['cleanContent'];
    // On Success
    if (check != "clean") {
    table = document.getElementById("data");
    headers = document.getElementById("cols");
    body = document.getElementById("rows");

    headers.innerHTML='';
    body.innerHTML='';


    for (col in cols){
        cell = document.createElement('th');
        cell.innerHTML = cols[col];
        headers.appendChild(cell);
    }
    for (row in rows) {
        tr = document.createElement('tr');
        for (item in rows[row]) {
            td = document.createElement("td");
            td.innerHTML =rows[row][item];
            tr.appendChild(td);
        }
        body.appendChild(tr);
    }
    } else {

    cleanHeaders = document.getElementById("cleanCols");
    cleanBody = document.getElementById("cleanRows");

    cleanHeaders.innerHTML='';
    cleanBody.innerHTML='';

    for (col in cleanCols){
        cell = document.createElement('th');
        cell.innerHTML = cleanCols[col];
        cleanHeaders.appendChild(cell);
    }
    for (row in cleanRows) {
        tr = document.createElement('tr');
        for (item in cleanRows[row]) {
            td = document.createElement("td");
            td.innerHTML =cleanRows[row][item];
            tr.appendChild(td);
        }
        cleanBody.appendChild(tr);
    }
    }

    },
    error: function (res,status) { 
        alert('error')
    }
});

}