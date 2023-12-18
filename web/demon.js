// functions for gluex detector calibration monitoring page

const homedir = 'https://halldweb.jlab.org/gluex_demon/';

var RunPeriod = "";
var Version = "";
var Detector = "";
var Graph = "";

const default_RP = "RunPeriod-2022-05";

var graphs_filename = "";  // root file
var pagenames = "";

var graphs_this_page = [];

import { openFile, draw } from 'https://root.cern/js/latest/modules/main.mjs';

var RP_list = [];  // list of available run periods  in runperiods.txt
var ver_list = []; // list of available versions     in versions.txt inside RP's subdir

const RP_file = './runperiods.txt';

// just in case
let example_url = document.URL.split("?")[0] + '?RunPeriod=RunPeriod-2022-05&Version=24';
let errortext = `<a href="${example_url}">${example_url}</a>`;


$(document).ready(async function () {

    await get_url_args();

    RP_list = await readlist(RP_file);

    await fillmenu("select_rp",RP_list,RunPeriod);

    if ( RunPeriod === "" ) {

        show_problem('Choose Run Period & Version, or try ' + errortext);
        Version = "";
        Detector = "";
      
    } else {

        if (! RP_list.includes(RunPeriod) ) {

            show_problem(`${RunPeriod} is not known!<br/>Try ` + errortext);                
            RunPeriod = "";
            Version = "";
            Detector = "";
        }
    } 
    

    ver_list = [];

    if (RunPeriod != "") {

        ver_list = await readlist(`${RunPeriod}/versions.txt`);

        if (Version == "") { 

            show_problem('Incomplete url!<br/>Try ' + errortext);                
            Detector = "";

        } else if (Version != "") {

            if (! ver_list.includes(Version) ) {

                show_problem(`${RunPeriod} version ${Version} is not known!<br/>Try ` + errortext);        
                Version = "";
                Detector = "";

            }
        }

        await fillmenu("select_ver",ver_list,Version);

    }






    if ( RunPeriod != "" && Version != "") {

        document.getElementById("RunPeriod").innerHTML = RunPeriod;
        document.getElementById("Version").innerHTML = 'Version ' + Version;
        document.getElementById("loading").innerHTML = "Loading...";

        let year_month = RunPeriod.substring(10,17);
        let subtitle = Detector;
        let link_1 = "";
        let link_2 = "";

        graphs_filename = `./${RunPeriod}/${Version}/monitoring_graphs_${year_month}_ver${Version}.root`
        pagenames = `./${RunPeriod}/${Version}/monitoring_pagenames_${year_month}_ver${Version}.txt`
        let csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${year_month}_ver${Version}.csv`

        // what if a nonexistent detector name is supplied?

        if (Detector === "") {
            subtitle = "Overview";
            link_1 = `<a href="${graphs_filename}">Download ROOT file of graphs</a>`;
            link_2 = `<a href="${csv_filename}">Download CSV file of metrics</a>`;
        } else {
            link_1 = `<a href="${document.URL.split("&Detector")[0]}">Return to overview page</a>`;
        }

        document.getElementById("Detector").innerHTML = subtitle;
        document.getElementById("graphs_or_return").innerHTML = link_1;
        document.getElementById("csv").innerHTML = link_2;
        document.getElementById("loading").innerHTML = "Loading...";

        await getgraphnames();

        drawGraphs().then(
           function(text) { 
                console.log(Graph);
                if (Graph != "") {
                    document.getElementById(Graph).scrollIntoView();
                }
        });


    }

});


function get_url_args() {

    /* read in the url, split it into arguments */

    let par_from_url = { RunPeriod: "", Version: "", Detector: ""};
    let currentURL_split = "";

    if (document.URL.includes("#")) {
        Graph = document.URL.split("#")[1];
        currentURL_split = document.URL.split("#")[0].split("?");
    } else {
        Graph = "";
        currentURL_split = document.URL.split("?");
    }

    if (currentURL_split.length === 2) {
        let URL_AND_split = currentURL_split[1].split("&");
        for (let i = 0; i < URL_AND_split.length; i++) {
          let opt = URL_AND_split[i].split("=");
          par_from_url[opt[0]] = opt[1];
        }
    }

    RunPeriod = par_from_url['RunPeriod'];
    Version = par_from_url['Version'];
    Detector = par_from_url['Detector'];  // actually the python module title
    
}




async function fetchfiledata(filename) {


    const response = await fetch(filename);
    // waits until the request completes...

    let text = await response.text();
    // this will be 404 if the file doesn't exist
    console.log(text);

    if (text.includes('404 Not Found')) {
        console.log('ERROR: ' + filename + ' not found!');
        text = false;
    }

    return text;

}




async function getgraphnames() {


    let group = [];
    let statusgraphs = ['readiness'];
    let detectors = [];
    let styletext = ' class="graphpanel"';
    let divtext = '';
    let linkfile = '';
    let listoflinks = '';

    graphs_this_page = [];  // tells jsROOT which graphs to show

    let text = await fetchfiledata(pagenames);

    let lineArr = text.split('\r\n'); 
             // eg CDC - CPP,4,cdc_status,cdc_occ,cdc_missing,cdc_eff

    let npages = lineArr.length - 1;  // ignore the empty last line

    for (let i=0; i<npages; i++) {
        group.push(lineArr[i].split(','));
        let name_without_spaces = group[i][0].replaceAll(" ","_");         
        detectors.push(name_without_spaces);
            
        statusgraphs.push((group[i][2]));   // overall readiness is first
    }


    if (Detector != "") {  // detector page

        let found = false;

        for (let j = 0; j < detectors.length; j++) {

            if (Detector === detectors[j]) {

                const ngraphs = Number(group[j][1]);

                for (let i = 2; i < ngraphs+2 ; i++) {

                    let thisgraph =  group[j][i];

                    graphs_this_page.push(thisgraph);  // copy graph name into array for this page

                    divtext += `<div id="${thisgraph}" class="graph_top"></div>`;

                    divtext += '<div id=g_' + thisgraph + styletext + '>';
                    divtext += '</div>';
                    divtext += `<div class="graph_names">${thisgraph}</div>`;
                    listoflinks += `<a href = "#${thisgraph}">${thisgraph}</a> `;

                }
            }
        }          

        if (! found) {
            Detector = "";   // nonexistent
            document.getElementById("Detector").innerHTML = "";
        }


    } else  {    // overview page

        for (let i = 0; i < statusgraphs.length; i++) {

            let thisgraph = statusgraphs[i];

            graphs_this_page.push(thisgraph);  // copy graph name into array for this page

            //divtext += `<div id="${statusgraphs[i]}" class="graph_names">${statusgraphs[i]}</div>`;
            divtext += `<div id="${thisgraph}" class="graph_top"></div>`;
            divtext += `<div id=g_${thisgraph} ${styletext}></div>`;  // the graph gets inserted inside this later
            divtext += `<div class="graph_names">${thisgraph}</div>`;

            listoflinks += `<a href = "#${thisgraph}">${thisgraph}</a> `;

            if (i>0) { // no detector link for overall readiness

                let thisdetector = detectors[i-1];

                linkfile = document.URL.split("#")[0] + '&Detector=' + thisdetector;   // ignore #graphname
                divtext += '<span><a href=' + linkfile + '> ' + thisdetector + ' details </a>';
                divtext += '</span>';

            }
        }          

    } 

    document.getElementById("graphs").innerHTML = divtext;    
    document.getElementById("links_graphs_this_page").innerHTML = 'Graphs on this page: ' + listoflinks;    

}

    

async function readlist(listfile) {

    const text = await fetchfiledata(listfile);

    console.log('fetchfiledata result: '+ text);

    let returntext = '';

    if (!text) {  // file not found

        console.log('Error (readlist) - could not read the file '+listfile);
        returntext = false;

    } else {

        returntext = text.split('\n');    // array of lines,  with '' in last place
        
        if (returntext[returntext.length-1] === '') returntext.pop();

    }

    console.log('fillmenu returning ',returntext);
    return returntext;
}




async function fillmenu(select_id,list,preselect) {

    let x = document.getElementById(select_id);

    // remove existing list
    for (let i = x.options.length-1 ; i>=0; i-- ) {           
        x.options.remove(i);
    }


    for (let i=0; i<list.length; i++) {

         let c = document.createElement("option");
         c.text = list[i];
         x.options.add(c);
         if (list[i] == preselect) {
             c.selected = true;
         } 
    }

}


function show_problem(message) {
    document.getElementById("RunPeriod").innerHTML = "";
    document.getElementById("titles2").innerHTML = "";
    document.getElementById("problems").innerHTML = message; //'Choose Run Period & Version.';
}

    
async function drawGraphs() {

    let file = await openFile(graphs_filename);//'./RunPeriod-2023-01/v6/monitoring_graphs.root');

    if (file) {
        console.log('file opened');

        console.log(graphs_this_page);
            
        const obj = [];

            // this makes an object named after the graph, which populates the div with the same name

        for (let i = 0; i < graphs_this_page.length; i++) {
            let gname = graphs_this_page[i];  //graphnames[i]
            obj[i] = await file.readObject(gname);
            obj[i].fMarkerSize=0.7;
            obj[i].fMarkerStyle=8;
            obj[i].fMarkerColor=890;
            obj[i].fEditable=0;

            let divname = 'g_' + gname;
            await draw(divname, obj[i], 'ap;gridx;gridy;');
        }

        console.log('drawing completed');

    } else {
        console.log('cannot find file :-( ');  // I dont think this works
    }

}




select_rp.addEventListener('change', async function () {
    const selectedRP = select_rp.value;
    let listfile = `${selectedRP}/versions.txt`;

    Version = '';
    let ver_list = await readlist(listfile);

    await fillmenu("select_ver",ver_list,Version);

});





reload.addEventListener('click', function () {
    const RP = select_rp.value;
    const ver = select_ver.value;

    let new_url = document.URL.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}`;
    console.log(new_url);
    window.location.assign(new_url);
});


