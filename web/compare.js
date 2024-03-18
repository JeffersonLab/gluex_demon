// functions for gluex detector calibration monitoring page

const RP_file = './runperiods.txt';

var RP_list = [];  // list of available run periods  in runperiods.txt
var ver_list = []; // list of available versions     in versions.txt inside RP's subdir
var graph_list = [];  // list of graphs in the root file             in pagenames

var graphs = [];   // list of graphs to compare

var RunPeriod = "";
var Version = "";

var graphs_filename = "";  // root file
var csv_filename = "";
var pagenames = "";  // file containing lists of graphs


import { openFile, draw, redraw, create, createTGraph, createTMultiGraph, createHistogram } from 'https://root.cern/js/latest/modules/main.mjs';
        JSROOT.gStyle.fPadTopMargin = 0.5;


$(document).ready(async function () {

    await get_url_args();

    RP_list = await readlist(RP_file);

    if ( RunPeriod === "" ) {

        RunPeriod = RP_list[0];
        Version = "";
        graphs=[];
      
    } else if (! RP_list.includes(RunPeriod) ) {

        show_problem(`${RunPeriod} is not known!`);

        RunPeriod = RP_list[0];
        Version = "";
        graphs=[];
    } 
    
    await fillmenu("select_rp",RP_list,[RunPeriod]);

    ver_list = [];

    ver_list = await readlist(`${RunPeriod}/versions.txt`);

    if (Version === "") { 

        Version = ver_list[0];                
        graphs=[];

    } else if (! ver_list.includes(Version) ) {

        show_problem(`${RunPeriod} version ${Version} is not known!`);
        Version = ver_list[0];                
        graphs=[];
    }

    await fillmenu("select_ver",ver_list,[Version]);


    document.getElementById("RunPeriod").innerHTML = RunPeriod;
    document.getElementById("Version").innerHTML = 'Version ' + Version;


    let year_month = RunPeriod.substring(10,17);

    graphs_filename = `./${RunPeriod}/${Version}/monitoring_graphs_${year_month}_ver${Version}.root`;
    csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${year_month}_ver${Version}.csv`;
    pagenames = `./${RunPeriod}/${Version}/monitoring_pagenames_${year_month}_ver${Version}.txt`;


    await getlistofgraphs();	// this fills det_list and graph_collection

    //remove graphs from url if not in the list

    var temp = [];
    for (const x of graphs) {
        if (graph_list.includes(x)) temp.push(x);
    }

    graphs = temp; // keep first 4


    show_graph_menu();
    await fillmenu("select_gr",graph_list,graphs);




    let subtitle = "";
    let link_1 = `<a href="${graphs_filename}">ROOT file</a>`;
    let link_2 = `<a href="${csv_filename}">CSV file</a>`;


    document.getElementById("rootfile").innerHTML = link_1;
    document.getElementById("csv").innerHTML = link_2;
//    document.getElementById("loading").innerHTML = "Loading...";


    if (graphs.length > 0) await drawGraphs();


});


function get_url_args() {

    /* read in the url, split it into arguments */

    let par_from_url = { RunPeriod: "", Version: "", Compare: ""};
    let currentURL_split = "";

    currentURL_split = document.URL.split("?");


    if (currentURL_split.length === 2) {
        let URL_AND_split = currentURL_split[1].split("&");
        for (let i = 0; i < URL_AND_split.length; i++) {
          let opt = URL_AND_split[i].split("=");
          par_from_url[opt[0]] = opt[1];
        }
    }


    RunPeriod = par_from_url['RunPeriod'];
    Version = par_from_url['Version'];

    graphs = [];

    graphs = par_from_url['Compare'].split("+"); 
    
}




async function fetchfiledata(filename) {


    const response = await fetch(filename);
    // waits until the request completes...

    let text = await response.text();
    // this will be 404 if the file doesn't exist
    //console.log(text);

    if (text.includes('404 Not Found')) {
        console.log('ERROR: ' + filename + ' not found!');
        show_problem(filename + ' is missing!');
        text = false;
    }

    return text;

}


async function getlistofgraphs() {

    // fills global array graph_list

    let text = await fetchfiledata(pagenames);

    let lineArr = text.split('\r\n'); 
             // eg CDC - CPP,4,cdc_status,cdc_occ,cdc_missing,cdc_eff

    let npages = lineArr.length - 1;  // ignore the empty last line

    for (let i=0; i<npages; i++) {

        let thisline = lineArr[i].split(',');
        let dir = thisline[0];
        
        for (let j = 2; j< thisline[1]; j++) {   
            if (!thisline[j].endsWith("composite")) graph_list.push(dir.concat("/",thisline[j]));  // exclude the multigraphs
        }
    }

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
         if (preselect.includes(list[i])) {
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

        const obj = [];

        var mg_colours = [887, 907, 801, 63];
        var mg_symbols = [8, 22, 29, 33, 23];

        let divname = 'graphs';

        let leg = create('TLegend');


        for (let i = 0; i < graphs.length; i++) {

            let gname = graphs[i];  //graphnames[i]
          
            let mkr = mg_symbols[i];
            
            console.log('looking for graph called ',gname);
            obj[i] = await file.readObject(gname);
            obj[i].fMarkerSize = 0.6;
            obj[i].fMarkerColor = mg_colours[i];
            obj[i].fMarkerStyle = mkr; //mg_symbols[(i/5) % 4];
            obj[i].fLineColor = mg_colours[i];
            obj[i].fLineStyle = 3;

            let legendtxt = gname.concat(' ',obj[i].fTitle);
            let temp = CreateLegendEntry(obj[i], legendtxt, mkr);
            leg.fPrimitives.Add(temp);          

       }

        // allow 0.1 per line until reaching 1

        let y1 = 1.0 - 0.05*graphs.length;
        if (y1 < 0) y1 = 0;

        Object.assign(leg, { fX1NDC: 0.3, fY1NDC: y1, fX2NDC: 0.7, fY2NDC: 1.0 });
        Object.assign(leg, { fTextFont:43, fTextSize:13, fTextAlign:12 });


        let n = graphs.length;

        let mg = obj[0];
    
        if (n==1) {
          mg = createTMultiGraph(obj[0]);

        } else if (n==2) {

          mg = createTMultiGraph(obj[0],obj[1]);

        } else if (n==3) {

          mg = createTMultiGraph(obj[0],obj[1],obj[2]);

        } else if (n==4) {

          mg = createTMultiGraph(obj[0],obj[1],obj[2],obj[3]);
        
        } else if (n==5) {

           mg = createTMultiGraph(obj[0],obj[1],obj[2],obj[3],obj[4]);

        } else {

           mg = createTMultiGraph(obj[0],obj[1],obj[2],obj[3],obj[4],obj[5]);
        }


        await draw(divname,mg,'apl:gridx:gridy');

        await draw('legend',leg);
      
        console.log('drawing completed');

    } else {
        console.log('cannot find file :-( ');  // I dont think this works
    }

}

function CreateLegendEntry(obj, lbl, mkr) {
         let entry = create('TLegendEntry');
         entry.fObject = obj;
         entry.fLabel = lbl;
         entry.fOption = 'p';
         entry.fMarkerStyle = mkr;
         return entry;
}


function show_graph_menu() {
    document.getElementById("sel_gr_text").innerHTML = 'Select up to 4 graphs to compare (click and ctrl-click or cmd-click)<br/>';

    const sel = document.getElementById("select_gr");
    sel.style.display = "inline";
}

function hide_graph_menu() {
    document.getElementById("sel_gr_text").innerHTML = '';

    const sel = document.getElementById("select_gr");
    sel.style.display = "none";

    document.getElementById("graphs").innerHTML = '';
    document.getElementById("legend").innerHTML = '';
    document.getElementById("RunPeriod").innerHTML = '';
    document.getElementById("Version").innerHTML = '';
}



select_rp.addEventListener('change', async function () {
    const selectedRP = select_rp.value;
    let listfile = `${selectedRP}/versions.txt`;

    Version = '';
    graphs = [];
    hide_graph_menu();

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

  //const sel = document.getElementById("select_gr");
  //sel.style.display = "none";
  hide_graph_menu();

  const btn = document.getElementById("reload");
  btn.style.display = "inline";

});


select_ver.addEventListener('change',function() {

  console.log('ver menu changed');

  //const sel = document.getElementById("select_gr");
  //sel.style.display = "none";
  hide_graph_menu();

  const btn = document.getElementById("reload");
  btn.style.display = "inline";

});


select_gr.addEventListener('change',function() {

  console.log('graph menu changed');

  const btn = document.getElementById("reload");
  btn.style.display = "none";

  const RP = select_rp.value;
  const ver = select_ver.value;

  var options = document.getElementById('select_gr').selectedOptions;
  graphs = Array.from(options).map(({ value }) => value);

  while (graphs.length > 4) {
      graphs.pop();
  }
    

  console.log(graphs);


  let new_url = document.URL.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}`;
  if ( graphs.length > 0 ) {
    new_url = new_url + `&Compare=${graphs[0]}`;
  }
  for (let i=1; i< graphs.length; i++) {
    new_url = new_url + `+${graphs[i]}`;
  }

  console.log(new_url);
  window.location.assign(new_url);

});



reload.addEventListener('click', function () {  
console.log('reload');
    const RP = select_rp.value;
    const ver = select_ver.value;

    let new_url = document.URL.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}`;

    console.log(new_url);
    window.location.assign(new_url);

});



