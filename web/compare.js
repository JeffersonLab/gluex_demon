// functions for gluex detector calibration monitoring page

const RP_file = './runperiods.txt';

var RP_list = [];  // list of available run periods  in runperiods.txt
var ver_list = []; // list of available versions     in versions.txt inside RP's subdir
var ver2_list = []; // list of available versions     in versions.txt inside RP's subdir
var graph_list = [];  // list of graphs in the root file             in pagenames

var graphs = [];   // list of graphs to compare

var RunPeriod = "";
var Version = "";
var Version2 = "";
var Graph = "";

var graphs_filename = "";  // root file
var graphs_filename2 = "";  // root file
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
        Version2 = "";		
        graph_list=[];
      
    } else if (! RP_list.includes(RunPeriod) ) {

        show_problem(`${RunPeriod} is not known!`);

        RunPeriod = RP_list[0];
        Version = "";
        Version2 = "";	
        graph_list=[];
    } 
    
    await fillmenu("select_rp",RP_list,[RunPeriod]);

    ver_list = [];
    ver_list = await readlist(`${RunPeriod}/versions.txt`);

    ver2_list = [];
    ver2_list = await readlist(`${RunPeriod}/versions.txt`);

    if (Version === "") { 

        Version = ver_list[0];                
        graph_list=[];

    } else if (! ver_list.includes(Version) ) {

        show_problem(`${RunPeriod} version ${Version} is not known!`);
        Version = ver_list[0];                
        graph_list=[];
    }

    if (Version2 === "") { 

        Version2 = ver2_list[0];                

    } else if (! ver2_list.includes(Version) ) {

        show_problem(`${RunPeriod} version ${Version} is not known!`);
        Version2 = ver_list2[0];                

    }
    
    await fillmenu("select_ver",ver_list,[Version]);
    await fillmenu("select_ver2",ver2_list,[Version2]);    


    document.getElementById("RunPeriod").innerHTML = RunPeriod;
    document.getElementById("Version1").innerHTML = 'Version ' + Version;
    document.getElementById("Version2").innerHTML = 'Version ' + Version2;    
    document.getElementById("Graph").innerHTML = Graph;
    



    
    let year_month = RunPeriod.substring(10,17);

    graphs_filename = `./${RunPeriod}/${Version}/monitoring_graphs_${year_month}_ver${Version}.root`;
    graphs_filename2 = `./${RunPeriod}/${Version2}/monitoring_graphs_${year_month}_ver${Version2}.root`;    
    csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${year_month}_ver${Version}.csv`;
    pagenames = `./${RunPeriod}/${Version}/monitoring_pagenames_${year_month}_ver${Version}.txt`;

    console.log('awaiting get list of graphs');
    await getlistofgraphs();	// this fills det_list and graph_collection

    await fillmenu("select_gr",graph_list,Graph);

    
    //remove graphs from url if not in the list




    let subtitle = "";
    let link_1 = `<a href="${graphs_filename}">ROOT file</a>`;
    let link_2 = `<a href="${csv_filename}">CSV file</a>`;


    document.getElementById("rootfile").innerHTML = link_1;
    document.getElementById("csv").innerHTML = link_2;
//    document.getElementById("loading").innerHTML = "Loading...";


    if (Graph != "") await drawGraphs();


});


function get_url_args() {

    /* read in the url, split it into arguments */

    let par_from_url = { RunPeriod: "", Version: "", Version2:"", Graph: ""};
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
    Version2 = par_from_url['Version2'];
    Graph = par_from_url['Graph'];    


    
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

    console.log(pagenames);
    
    let lineArr = text.split('\r\n'); 
             // eg CDC - CPP,4,cdc_status,cdc_occ,cdc_missing,cdc_eff

    let npages = lineArr.length-1;  // do not ignore the empty last line

    for (let i=0; i<npages; i++) {

        let thisline = lineArr[i].split(',');
        let dir = thisline[0];
	let lastitem = Number(thisline[1]) + 1;
	console.log("lastitem:",lastitem);
        for (let j = 2; j<=lastitem; j++) {
	    console.log(thisline[j]);
            if (!thisline[j].endsWith("composite")) graph_list.push(dir.concat("/",thisline[j]));  // exclude the multigraphs
        }
    }

    console.log(graph_list);
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
    let file2 = await openFile(graphs_filename2);//'./RunPeriod-2023-01/v6/monitoring_graphs.root');    

    if (file) {
	console.log('file opened');
    }

    if (file2) {
	console.log('file 2 opened');
    }

    if (!file || !file2) {
	console.log('file missing');
	return;
    }
	
        

    var mg_colours = [887, 907, 801, 63];
    var mg_symbols = [8, 22, 29, 33, 23];

    let divname = 'graphs';
    let leg = create('TLegend');
    leg.fColumnSeparation = 0;
    leg.fMargin = 0.05; 

/////        for (let i = 0; i < graphs.length; i++) {

    let gname = Graph; //graphs[i];  //graphnames[i]
    let mkr = mg_symbols[0];
            
            console.log('looking for graph called ',gname);
    let g1 = await file.readObject(gname);

    console.log(g1);    
    
            g1.fMarkerSize = 0.6;
            g1.fMarkerColor = mg_colours[0];
            g1.fMarkerStyle = mkr; //mg_symbols[(i/5) % 4];
            g1.fLineColor = mg_colours[0];
            g1.fLineStyle = 3;

//            let legendtxt = gname.concat(' ',obj[i].fTitle);
            let temp = CreateLegendEntry(g1, Version, mkr);

    
	
            leg.fPrimitives.Add(temp);          
            mkr = mg_symbols[0];
            
            console.log('looking for graph in next file');
            let g2 = await file2.readObject(gname);
            g2.fMarkerSize = 0.6;
            g2.fMarkerColor = mg_colours[1];
            g2.fMarkerStyle = mkr; //mg_symbols[(i/5) % 4];
            g2.fLineColor = mg_colours[1];
            g2.fLineStyle = 3;

//            let legendtxt = gname.concat(' ',obj[i].fTitle);
            temp = CreateLegendEntry(g2, Version2, mkr);
            leg.fPrimitives.Add(temp);          


	
/////       }

        // allow 0.1 per line until reaching 1
        let n = graphs.length;
	
        let y1 = 1.0 - 0.05*2;
        if (y1 < 0) y1 = 0;

//        Object.assign(leg, { fX1NDC: 0.3, fY1NDC: y1, fX2NDC: 0.7, fY2NDC: 1.0 });
        Object.assign(leg, { fTextFont:43, fTextSize:13, fTextAlign:12 });
        Object.assign(leg, { fX1NDC: 0.91, fY1NDC: 0.7, fX2NDC: 1.0, fY2NDC: 0.9, fColumnSeparation:0, fMargin:0.15 });
    
        let mg = createTMultiGraph(g1, g2);

    console.log('c');
    console.log(divname);
    console.log(mg);
        await draw(divname,mg,'ap:gridx:gridy');
       await draw(divname,leg);

      
        console.log('drawing completed');


}

function CreateLegendEntry(obj, lbl, mkr) {
         let entry = create('TLegendEntry');
         entry.fObject = obj;
         entry.fLabel = lbl;
         entry.fOption = 'p';
         entry.fMarkerStyle = mkr;
         return entry;
}





select_rp.addEventListener('change', async function () {
    const selectedRP = select_rp.value;
    let listfile = `${selectedRP}/versions.txt`;

    Version = '';
    Version2 = "";
    graphs = [];

    let ver_list = await readlist(listfile);
    let most_recent = ver_list[ver_list.length-1];  // suggest as default

    Version = most_recent;

    await fillmenu("select_ver",ver_list,most_recent);
    await fillmenu("select_ver2",ver_list,most_recent);    

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

/*

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

*/

select_gr.addEventListener('change',function() {

  console.log('graph menu changed');

  const btn = document.getElementById("reload");
  btn.style.display = "none";

  const RP = select_rp.value;
  const ver = select_ver.value;
  const ver2 = select_ver2.value;
  const Graph = select_gr.value;
        

  console.log(Graph);


  let new_url = document.URL.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}&Version2=${ver2}&Graph=${Graph}`;

  console.log(new_url);
  window.location.assign(new_url);

});



reload.addEventListener('click', function () {  
console.log('reload');
    const RP = select_rp.value;
    const ver = select_ver.value;
    const ver2 = select_ver2.value;    

    let new_url = document.URL.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}&Version2=${ver2}`;

    console.log(new_url);
    window.location.assign(new_url);

});



