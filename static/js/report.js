/*
===========================================================
Universal Test Report Analyzer
report.js
===========================================================
*/

let currentFilter = "all";

/*
===========================================================
Expand / Collapse Class
===========================================================
*/

function toggleClass(header){

    const classBox = header.parentElement;

    classBox.classList.toggle("collapsed");

}


/*
===========================================================
Show / Hide Failure Details
===========================================================
*/

function toggleFailure(button){

    const currentRow = button.closest("tr");

    const detailRow = currentRow.nextElementSibling;

    if(!detailRow){

        return;

    }

    if(detailRow.style.display==="none" ||
        detailRow.style.display===""){

        detailRow.style.display="table-row";

        button.innerHTML="Hide Details";

    }

    else{

        detailRow.style.display="none";

        button.innerHTML="Show Details";

    }

}


/*
===========================================================
Filter Tests
===========================================================
*/

function filterTests(status, button){

    currentFilter = status;

    document.querySelectorAll(".filter-btn")
        .forEach(btn=>btn.classList.remove("active"));

    button.classList.add("active");

    applyFilters();

}


/*
===========================================================
Search
===========================================================
*/

const searchBox = document.getElementById("searchBox");

if(searchBox){

    searchBox.addEventListener("keyup",function(){

        applyFilters();

    });

}


/*
===========================================================
Apply Search + Filter
===========================================================
*/

function applyFilters(){

    const keyword = searchBox.value
        .toLowerCase()
        .trim();

    const classBoxes = document.querySelectorAll(".class-box");

    classBoxes.forEach(classBox=>{

        let visibleRows = 0;

        const rows = classBox.querySelectorAll("tr.test-row");

        rows.forEach(row=>{

            const status = row.dataset.status;

            const name = row.dataset.name;

            let show = true;

            /*
            -------------------------
            Status Filter
            -------------------------
            */

            if(currentFilter!=="all"){

                show = status===currentFilter;

            }

            /*
            -------------------------
            Search
            -------------------------
            */

            if(show && keyword.length>0){

                show = name.includes(keyword);

            }

            /*
            -------------------------
            Show / Hide
            -------------------------
            */

            row.style.display = show ? "" : "none";

            /*
            Hide failure row if parent hidden
            */

            const failureRow = row.nextElementSibling;

            if(failureRow &&
                failureRow.classList.contains("failure-row")){

                if(show){

                    failureRow.style.display="none";

                    const btn=row.querySelector(".details-btn");

                    if(btn){

                        btn.innerHTML="Show Details";

                    }

                }

                else{

                    failureRow.style.display="none";

                }

            }

            if(show){

                visibleRows++;

            }

        });

        /*
        Hide entire class
        */

        if(visibleRows===0){

            classBox.style.display="none";

        }

        else{

            classBox.style.display="";

        }

    });

}


/*
===========================================================
Expand All
===========================================================
*/

function expandAll(){

    document.querySelectorAll(".class-box")
        .forEach(box=>{

            box.classList.remove("collapsed");

        });

}


/*
===========================================================
Collapse All
===========================================================
*/

function collapseAll(){

    document.querySelectorAll(".class-box")
        .forEach(box=>{

            box.classList.add("collapsed");

        });

}


/*
===========================================================
Show Only Failed Classes
===========================================================
*/

function showFailedClasses(){

    document.querySelectorAll(".class-box")
        .forEach(box=>{

            const failBadge =
                box.querySelector(".badge.fail");

            if(failBadge){

                box.style.display="";

            }

            else{

                box.style.display="none";

            }

        });

}


/*
===========================================================
Reset View
===========================================================
*/

function resetView(){

    currentFilter="all";

    searchBox.value="";

    document.querySelectorAll(".filter-btn")
        .forEach(btn=>btn.classList.remove("active"));

    document.querySelector(".filter-btn")
        .classList.add("active");

    applyFilters();

}


/*
===========================================================
Keyboard Shortcut

Ctrl + F

Focus Search
===========================================================
*/

document.addEventListener("keydown",function(e){

    if(e.ctrlKey && e.key==="f"){

        e.preventDefault();

        searchBox.focus();

    }

});


/*
===========================================================
Page Loaded
===========================================================
*/

window.onload=function(){

    applyFilters();

};