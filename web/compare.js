// functions for gluex detector calibration monitoring page
import { openFile, draw, create, createTMultiGraph } from 'https://root.cern/js/latest/modules/main.mjs';

const RP_file = './runperiods.txt';

var RP_list = [];  // list of available run periods  in runperiods.txt
var ver_list = []; // list of available versions     in versions.txt inside RP's subdir
var ver2_list = []; // list of available versions     in versions.txt inside RP's subdir
var page_list = []; // list of available pages, in pagenames 
var graph_list = [];

var graphs_filename = "";
var graphs_filename2 = "";

var RunPeriod = "";
var Version = "";
var Version2 = "";
var PageGraph = "";
var Page = "";
var Graph = "";

// put Graph = CDC/dedx into the url. split it into page and graphname for the menus.

await get_url_args();

if (!PageGraph) hide_pagegraph_menus();

RP_list = await readlist(RP_file, true);

if (RunPeriod == "") {
    RunPeriod = RP_list[0];
    Version = "";
    Version2 = "";
    PageGraph = "";
} else if (!RP_list.includes(RunPeriod)) {
    const url = document.URL.split("?")[0];
    show_problem(`${RunPeriod} not found! <a href="${url}">Start again</a>`);
    throw new Error('Invalid run period supplied');
}    

await fillmenu("select_rp",RP_list,RunPeriod);


ver_list = await readlist(`${RunPeriod}/versions.txt`, true);

if (Version && !ver_list.includes(Version) || Version2 && !ver_list.includes(Version2)){
    const url = document.URL.split("?")[0] + `?RunPeriod=${RunPeriod}`;
    show_problem(`Version not found! <a href="${url}">Start again</a>`);
    throw new Error('Invalid version supplied');
}

let v1 = Version;
let v2 = Version2;

if (Version == "") v1 = (ver_list.length>1) ? ver_list[ver_list.length-2] : ver_list[0];
if (Version2 == "") v2 = ver_list[ver_list.length-1];

await fillmenu("select_ver",ver_list,v1);
await fillmenu("select_ver2",ver_list,v2);

if (Version1 && Version2) {
    document.getElementById("RunPeriod").innerHTML = RunPeriod;
    document.getElementById("Version1").innerHTML = 'Versions ' + Version;
    document.getElementById("Version2").innerHTML = '& ' + Version2;

    const year_month = RunPeriod.substring(10,17);
    const filename = `./${RunPeriod}/${Version}/monitoring_pagenames_${year_month}_ver${Version}.txt`;
    graphs_filename = `./${RunPeriod}/${Version}/monitoring_graphs_${year_month}_ver${Version}.root`;
    graphs_filename2 = `./${RunPeriod}/${Version2}/monitoring_graphs_${year_month}_ver${Version2}.root`;    
    const csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${year_month}_ver${Version}.csv`;
    const csv_filename2 = `./${RunPeriod}/${Version}/monitoring_data_${year_month}_ver${Version2}.csv`;
    const pagenames2 = `./${RunPeriod}/${Version}/monitoring_pagenames_${year_month}_ver${Version2}.txt`;

    document.getElementById("rootfile1").innerHTML = `<a href="${graphs_filename}">ROOT file ${Version}</a>`;
    document.getElementById("rootfile2").innerHTML = `<a href="${graphs_filename2}">ROOT file ${Version2}</a>`;    
    document.getElementById("csv1").innerHTML = `<a href="${csv_filename}">CSV file ${Version}</a>`;
    document.getElementById("csv2").innerHTML = `<a href="${csv_filename2}">CSV file ${Version2}</a>`;    
    
    show_pagegraph_menus();
    
    console.log('awaiting get list of graphs');
    if (PageGraph) await drawGraphs();

    Page = (PageGraph) ? PageGraph.split('/')[0] : "";
    Graph = (PageGraph) ? PageGraph.split('/')[1] : "";

    await getlistofpages(graphs_filename);    
    if (!page_list.includes(Page)) Page = page_list[0];
    await fillmenu("select_page", page_list, Page);    

    await getlistofgraphs(graphs_filename);  
    if (!graph_list.includes(Graph)) Graph = graph_list[0];
    await fillmenu("select_gr", graph_list, Graph);

    PageGraph = `${Page}/${Graph}`;
    await drawGraphs();

}


function get_url_args() {

    /* read in the url, split it into arguments */
    let par_from_url = { RunPeriod: "", Version: "", Version2:"", Graph: ""};

    const currentURL_split = document.URL.split("?");

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
    PageGraph = par_from_url['Graph'];        
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


async function getlistofpages(graphs_filename) {

    let file = await openFile(graphs_filename);//'./RunPeriod-2023-01/v6/monitoring_graphs.root');
    if (!file) {
        show_problem(`Could not open `, graphs_filename);
	return;
    }

    page_list = [];
    for (const x of file.fKeys) {
        if (x.fClassName == 'TDirectory') page_list.push(x.fName);
    }

}


async function getlistofgraphs(graphs_filename) {

    let file = await openFile(graphs_filename);//'./RunPeriod-2023-01/v6/monitoring_graphs.root');
    if (!file) {
        show_problem('Could not open ', graphs_filename);
	return;
    }

    const dir = await file.readObject(Page);
    if (!dir) {
        show_problem('Could not open directory', Page);
	return;
    }

    graph_list = [];
    for (const x of dir.fKeys) {
        if (x.fClassName == 'TGraph' || x.fClassName == 'TGraphErrors') graph_list.push(x.fName);
    }

}


async function readlist(listfile) {

    const text = await fetchfiledata(listfile);
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

    const x = document.getElementById(select_id);
    x.length = 0;

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
    document.getElementById("problems").innerHTML = message;
}

    
async function drawGraphs() {

    document.getElementById("graphs").innerHTML = "";
    document.getElementById("problems").innerHTML = "";
    
    let file = await openFile(graphs_filename);//'./RunPeriod-2023-01/v6/monitoring_graphs.root');
    let file2 = await openFile(graphs_filename2);//'./RunPeriod-2023-01/v6/monitoring_graphs.root');

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

    let gname = PageGraph;  
    let mkr = mg_symbols[0];
            
    console.log('looking for graph called ',gname);
    let g1 = await file.readObject(gname);

    g1.fMarkerSize = 0.6;
    g1.fMarkerColor = mg_colours[0];
    g1.fMarkerStyle = mkr; //mg_symbols[(i/5) % 4];
    g1.fLineColor = mg_colours[0];
    g1.fLineStyle = 3;

    let temp = CreateLegendEntry(g1, Version, mkr);
    leg.fPrimitives.Add(temp);          
    mkr = mg_symbols[0];

    console.log('looking for graph in next file');

    let g2 = "";
    
    try {
        g2 = await file2.readObject(gname);
    } catch (error) {
        console.error(error.message);
	show_problem(`Graph ${gname} is not in version ${Version2}`);
    }	    

    if (g2) {

        console.log(g2);
        g2.fMarkerSize = 0.6;
        g2.fMarkerColor = mg_colours[1];
        g2.fMarkerStyle = mkr; //mg_symbols[(i/5) % 4];
        g2.fLineColor = mg_colours[1];
        g2.fLineStyle = 3;

        temp = CreateLegendEntry(g2, Version2, mkr);
        leg.fPrimitives.Add(temp);          

        Object.assign(leg, { fTextFont:43, fTextSize:13, fTextAlign:12 });
        Object.assign(leg, { fX1NDC: 0.91, fY1NDC: 0.7, fX2NDC: 1.0, fY2NDC: 0.9, fColumnSeparation:0, fMargin:0.15 });
    
        let mg = createTMultiGraph(g1, g2);
	mg.fTitle = PageGraph;

        await draw(divname,mg,'ap:gridx:gridy');
        await draw(divname,leg);
    } else {
	await draw(divname, g1);
    }
      
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

    hide_pagegraph_menus();
    
    const selectedRP = select_rp.value;
    const listfile = `${selectedRP}/versions.txt`;

    Version = '';
    Version2 = "";
    PageGraph = "";

    let ver_list = await readlist(listfile);

    const ver1 = (ver_list.length>1) ? ver_list[ver_list.length-2] : ver_list[0];
    const ver2 = ver_list[ver_list.length-1];

    await fillmenu("select_ver",ver_list,ver1);
    await fillmenu("select_ver2",ver_list,ver2);

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


function hide_pagegraph_menus() {
    const selp = document.getElementById("select_page");
    selp.style.display = "none";
    const selg = document.getElementById("select_gr");
    selg.style.display = "none";
    
    const btn = document.getElementById("reload");
    btn.style.display = "inline";

    const cp = document.getElementById("copy_url");
    cp.style.display = "none";
}


function show_pagegraph_menus() {
    const selp = document.getElementById("select_page");
    selp.style.display = "inline";
    const selg = document.getElementById("select_gr");
    selg.style.display = "inline";
    
    const btn = document.getElementById("reload");
    btn.style.display = "none";

    const cp = document.getElementById("copy_url");
    cp.style.display = "inline";
}


select_ver.addEventListener('change',function() {
  console.log('ver menu changed');
  hide_pagegraph_menus();
});

select_ver2.addEventListener('change',function() {
  console.log('ver2 menu changed');
  hide_pagegraph_menus();
});



select_page.addEventListener('change',async function() {

  Page = select_page.value;
  
  await getlistofgraphs(graphs_filename);  
  if (!graph_list.includes(Graph)) Graph = graph_list[0];
  await fillmenu("select_gr", graph_list, Graph);

  PageGraph = `${Page}/${Graph}`;  
  await drawGraphs();
});


select_gr.addEventListener('change',async function() {
    
  Graph = select_gr.value;
  PageGraph = `${Page}/${Graph}`;

  await drawGraphs();
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


copy_url.addEventListener('click', function () {  

    let this_url = document.URL.split("?")[0] + `?RunPeriod=${RunPeriod}&Version=${Version}&Version2=${Version2}&Graph=${Page}/${Graph}`;    
    
    console.log(this_url);

    const tempInput = document.createElement('textarea');
    tempInput.value = this_url;
    document.body.appendChild(tempInput);
    tempInput.select();
    tempInput.setSelectionRange(0, 99999);

    try {
       document.execCommand('copy');
       //alert('URL copied to clipboard!');
    } catch (err) {
        alert('Could not copy URL, sorry.');
    }

    document.body.removeChild(tempInput);

});
