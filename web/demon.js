// functions for gluex detector calibration monitoring page

const homedir = 'https://halldweb.jlab.org/gluex_demon/';
const RP_file = './runperiods.txt';

var RP_list = [];  // list of available run periods  in runperiods.txt
var ver_list = []; // list of available versions     in versions.txt inside RP's subdir
var det_list = []; // list of available detectors/modules   in pagenames 

var graph_collection = [];  // vast 2D list of graphs             in pagenames
var graphs_this_page = [];   // list of graphs on the current page

var RunPeriod = "";
var Version = "";
var Detector = "";
var Graph = "";

var graphs_filename = "";  // root file
var csv_filename = "";
var pagenames = "";  // file containing lists of graphs


import { openFile, draw } from 'https://root.cern/js/latest/modules/main.mjs';


$(document).ready(async function () {

    await get_url_args();

    RP_list = await readlist(RP_file);

    if ( RunPeriod === "" ) {

        RunPeriod = RP_list[0];
        Version = "";
        Detector = "";
      
    } else if (! RP_list.includes(RunPeriod) ) {

        show_problem(`${RunPeriod} is not known!`);

        RunPeriod = RP_list[0];
        Version = "";
        Detector = "";
    } 
    
    await fillmenu("select_rp",RP_list,RunPeriod);

    ver_list = [];

    ver_list = await readlist(`${RunPeriod}/versions.txt`);

    if (Version === "") { 

        Version = ver_list[0];                
        Detector = "";

    } else if (! ver_list.includes(Version) ) {

        show_problem(`${RunPeriod} version ${Version} is not known!`);
        Version = ver_list[0];                
        Detector = "";
    }

    await fillmenu("select_ver",ver_list,Version);


    document.getElementById("RunPeriod").innerHTML = RunPeriod;
    document.getElementById("Version").innerHTML = 'Version ' + Version;


    let year_month = RunPeriod.substring(10,17);

    graphs_filename = `./${RunPeriod}/${Version}/monitoring_graphs_${year_month}_ver${Version}.root`;
    csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${year_month}_ver${Version}.csv`;
    pagenames = `./${RunPeriod}/${Version}/monitoring_pagenames_${year_month}_ver${Version}.txt`;

    await getdetectornames();	// this fills det_list and graph_collection


    if (! det_list.includes(Detector) ) {   //det_list[0] is ""
        show_problem(`${RunPeriod} version ${Version} does not include ${Detector}!`);
        Detector = "";
    }

    await fillmenu("select_det",det_list,Detector);


    console.log('filled detector menu');

    let subtitle = "Overview";
    let link_1 = `<a href="${graphs_filename}">Download ROOT file of graphs</a>`;
    let link_2 = `<a href="${csv_filename}">Download CSV file of metrics</a>`;

    if (Detector !== "") {
        subtitle = Detector;
        link_1 = `<a href="${document.URL.split("&Detector")[0]}">Return to overview page</a>`;
        link_2 = "";
    }

    document.getElementById("Detector").innerHTML = subtitle;
    document.getElementById("graphs_or_return").innerHTML = link_1;
    document.getElementById("csv").innerHTML = link_2;
    document.getElementById("loading").innerHTML = "Loading...";

    await getgraphnames();   // reads graph names from pagenames file

    drawGraphs().then(
       function(text) { 
           console.log(Graph);
           if (Graph != "") {
                document.getElementById(Graph).scrollIntoView();
           }
    });


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
    //console.log(text);

    if (text.includes('404 Not Found')) {
        console.log('ERROR: ' + filename + ' not found!');
        text = false;
    }

    return text;

}


async function getdetectornames() {

    // fills global arrays det_list and graph_collection

    graphs_this_page = [];  // tells jsROOT which graphs to show

    let text = await fetchfiledata(pagenames);

    let lineArr = text.split('\r\n'); 
             // eg CDC - CPP,4,cdc_status,cdc_occ,cdc_missing,cdc_eff

    let npages = lineArr.length - 1;  // ignore the empty last line

    det_list = [""];

    for (let i=0; i<npages; i++) {
        graph_collection.push(lineArr[i].split(','));
        let name_without_spaces = graph_collection[i][0].replaceAll(" ","_");         
        det_list.push(name_without_spaces);
            
//        statusgraphs.push((graph_collection[i][2]));   // overall readiness is first
    }

}



async function getgraphnames() {

    // uses global graph_collection
    // fills global graphs_this_page

    let statusgraphs = ['readiness'];
    let styletext = ' class="graphpanel"';
    let divtext = '';
    let linkfile = '';
    let listoflinks = '';

    graphs_this_page = [];  // tells jsROOT which graphs to show

    if (Detector != "") {  // detector page

        let j = det_list.indexOf(Detector) - 1;   // because det_list starts w overview

        const ngraphs = Number(graph_collection[j][1]); 

        for (let i = 2; i < ngraphs+2 ; i++) {

            let thisgraph =  graph_collection[j][i];

            graphs_this_page.push(thisgraph);  // copy graph name into array for this page

            divtext += `<div id="${thisgraph}" class="graph_top"></div>`;

            divtext += '<div id=g_' + thisgraph + styletext + '>';
            divtext += '</div>';
            divtext += `<div class="graph_names"><a href="#${thisgraph}">${thisgraph}</a></div>`;
            listoflinks += `<a href = "#${thisgraph}">${thisgraph}</a> `;

        }

    } else  {    // overview page

        let npages = det_list.length;  // NB it starts with "" for overview

        // start at -1 for readiness
        for (let i = 0; i < npages; i++) {

            let thisgraph = 'readiness';
            if (i>0 ) {
                thisgraph = graph_collection[i-1][2];
            }

            graphs_this_page.push(thisgraph);  // copy graph name into array for this page

            //divtext += `<div id="${statusgraphs[i]}" class="graph_names">${statusgraphs[i]}</div>`;
            divtext += `<div id="${thisgraph}" class="graph_top"></div>`;
            divtext += `<div id=g_${thisgraph} ${styletext}></div>`;  // the graph gets inserted inside this later
            divtext += `<div class="graph_names"><a href="#${thisgraph}">${thisgraph}</a></div>`;

            listoflinks += `<a href = "#${thisgraph}">${thisgraph}</a> `;

            if (i>0) { // no detector link for overall readiness

                let thisdetector = det_list[i]; 

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
    //    document.getElementById("RunPeriod").innerHTML = "";
    //  document.getElementById("Version").innerHTML = "";
    //document.getElementById("titles2").innerHTML = "";
    document.getElementById("problems").innerHTML = message;
}

    
async function drawGraphs() {

    let file = await openFile(graphs_filename);//'./RunPeriod-2023-01/v6/monitoring_graphs.root');

    if (file) {
        console.log('file opened');

        //console.log(graphs_this_page);
            
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
    Detector = '';

    let ver_list = await readlist(listfile);
    let most_recent = ver_list[ver_list.length-1];  // suggest as default

    Version = most_recent;

    await fillmenu("select_ver",ver_list,most_recent);

});


// when the RP or ver changes:
//      show the go/reload button 
//      hide the detector dropdown
//
// after reloading the page, 
//      hide the go/reload
//      show the detector dropdown
//
// after the detector changes
//      reload the page
//



select_rp.addEventListener('change',function() {

  console.log('rp menu changed');

  const sel = document.getElementById("select_det");
  sel.style.display = "none";

  const btn = document.getElementById("reload");
  btn.style.display = "inline";

});


select_ver.addEventListener('change',function() {

  console.log('ver menu changed');

  const sel = document.getElementById("select_det");
  sel.style.display = "none";

  const btn = document.getElementById("reload");
  btn.style.display = "inline";

});


select_det.addEventListener('change',function() {

  console.log('det menu changed');

  const btn = document.getElementById("reload");
  btn.style.display = "none";

  const RP = select_rp.value;
  const ver = select_ver.value;
  const det = select_det.value;

  let new_url = document.URL.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}`;
  if ( det != "" ) {
    new_url = new_url + `&Detector=${det}`;
  }

  console.log(new_url);
  window.location.assign(new_url);

});



reload.addEventListener('click', function () {  
console.log('reload');
    const RP = select_rp.value;
    const ver = select_ver.value;
    const det = '';

    let new_url = document.URL.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}`;

    console.log(new_url);
    window.location.assign(new_url);

});



