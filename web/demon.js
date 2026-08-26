// functions for gluex detector calibration monitoring page

const RP_file = './runperiods.txt';

var RP_list = [];  // list of available run periods  in runperiods.txt
var ver_list = []; // list of available versions     in versions.txt inside RP's subdir
var page_list = []; // list of available detectors/modules, in pagenames 
var gr_list = [];  // list of graph names, used for the menu

var graph_collection = [];  // vast 2D list of graphs             in pagenames
var graphs_this_page = [];   // list of graphs on the current page loaded from the file (may include nonexistent graphs)

var plot_collection = '';  // list of plot names, from json file of plotnames

var RunPeriod = "";  // selected RP
var Version = "";
var Page = "";
var Graph = "";

//import { openFile, draw, create, settings } from 'https://jsroot.gsi.de/latest/modules/main.mjs';
import { openFile, draw, create, settings } from 'https://root.cern/js/latest/modules/main.mjs';

await get_url_args();

const RP_supplied = RunPeriod;
const ver_supplied = Version;
const page_supplied = Page;


RP_list = await readlist(RP_file, true);

if ( RunPeriod == "" ) {
    RunPeriod = RP_list[0];
    Version = "";
} else {
    const RP_valid = RP_list.includes(RunPeriod);

    if (!RP_valid) {
        console.log('Invalid run period');
        const url = document.URL.split("?")[0];
        show_problem(`${RunPeriod} not found! <a href="${url}">Start again</a>`);
	throw new Error('Invalid run period supplied');
    }
}    

await fillmenu("select_rp",RP_list,RunPeriod);

ver_list = await readlist(`${RunPeriod}/versions.txt`, true);

if (Version == "") {
    Version = ver_list[0];
} else {
    const Ver_valid = ver_list.includes(Version);

    if (!Ver_valid) {
        console.log('Invalid version');
        const url = document.URL.split("?")[0];
        show_problem(`Version ${Version} not found! <a href="${url}">Start again</a>`);
	throw new Error('Invalid version supplied');
    }
}

// if the page was called without arguments, force a reload

if (RP_supplied == "" || ver_supplied == "") {
    let new_url = document.URL.split("#")[0];
    new_url = new_url.split("?")[0] + `?RunPeriod=${RunPeriod}&Version=${Version}&Page=Overview`;
    window.location.assign(new_url);
}

await fillmenu("select_ver",ver_list,Version);

const year_month = RunPeriod.substring(10,17);

const pagenames = `./${RunPeriod}/${Version}/monitoring_pagenames_${year_month}_ver${Version}.txt`;
const plotnames = `./${RunPeriod}/${Version}/monitoring_plotnames_${year_month}_ver${Version}.txt`;

await getpagenames();	// this fills page_list and graph_collection and plot_collection
console.log("collected page names and graphs");

if (page_supplied == "" || !page_list.includes(Page)) {
    let new_url = document.URL.split("#")[0];
    new_url = new_url.split("?")[0] + `?RunPeriod=${RunPeriod}&Version=${Version}&Page=Overview`;
    window.location.assign(new_url);
}

// at this point, RP, version and page are all good, and in the url.

document.getElementById("RunPeriod").innerHTML = RunPeriod;
document.getElementById("Version").innerHTML = 'Version ' + Version;

await fillmenu("select_page",page_list,Page);

const graphs_filename = `./${RunPeriod}/${Version}/monitoring_graphs_${year_month}_ver${Version}.root`;
document.getElementById("link_root").href = `${graphs_filename}`;
document.getElementById("link_csv").href = csv_filename();
document.getElementById("link_compare").href = `./compare.html?RunPeriod=${RunPeriod}&Version=${Version}`;

console.log("getting the list of graphs");

await get_list_of_graphs();

if (Graph == "" || !gr_list.includes(Graph)) {
    Graph = gr_list[0];
}

await fillmenu("select_graph",gr_list,Graph);

console.log('awaiting build_page');

await build_page(); 

if (Graph) document.getElementById(Graph).scrollIntoView();

// fill the menu again as nonexistent graphs are removed in build_page
fillmenu("select_graph",gr_list,Graph);

console.log('page ready');


//------------------------------------


function get_url_args() {

    /* read in the url, split it into arguments */

    let par_from_url = { RunPeriod: "", Version: "", Page: ""};
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
    Page = par_from_url['Page'];  // actually the python module title
    
}


async function fetchfiledata(filename, quiet=true) {

    const response = await fetch(filename+'?'+Math.random());   // requesting filename?random avoids the data being cached

    let text = await response.text();
    // this will be 404 if the file doesn't exist
    //console.log(text);

    if (text.includes('404 Not Found')) {
        text = false;
	if (!quiet) {
            console.log('ERROR: ' + filename + ' not found!');
            show_problem(filename + ' is missing!');
	}
    }

    return text;
}


async function fetchjson(filename, quiet=true) {

    const response = await fetch(filename+'?'+Math.random());   // requesting filename?random avoids the data being cached

    if (!response.ok) {
        console.log('ERROR: ' + filename + ' not found!');
        show_problem(filename + ' is missing!');
	return false;
    }
    
    let data = await response.json();
    return data;
}


async function getpagenames() {

    // fills global arrays page_list and graph_collection and plot_collection

    let text = await fetchfiledata(pagenames);

    let lineArr = text.split('\r\n');  // eg CDC - CPP,4,cdc_status,cdc_occ,cdc_missing,cdc_eff

    let npages = lineArr.length - 1;  // ignore the empty last line

    page_list = ["Overview"];

    for (let i=0; i<npages; i++) {
        graph_collection.push(lineArr[i].split(','));
        let name_without_spaces = graph_collection[i][0].replaceAll(" ","_");         
        page_list.push(name_without_spaces);
    }

    plot_collection = await fetchjson(plotnames);

}


async function get_list_of_graphs() {

    if (Page == "Overview") { 
        
        graphs_this_page.push('/readiness');  // copy graph name into array for this page
	gr_list.push('readiness');

	const npages = page_list.length;  // NB it starts with "" for overview
	
	for (let i = 0; i < npages-1; i++) {
    
            const gdir = graph_collection[i][0]; 
            const thisgraph = graph_collection[i][2];

            graphs_this_page.push(gdir + '/' + thisgraph); 
            gr_list.push(thisgraph.replace("_status_all",""));
	    
	}

    } else  {
	
        const j = page_list.indexOf(Page) - 1;   // because page_list starts w overview

	const graphs = graph_collection[j];
        const gdir = graphs[0]; 
        const ngraphs = Number(graphs[1]); 
        const status_composite = graphs[2];
	
	graphs_this_page.push(gdir + '/' + status_composite);

	gr_list.push(Page);

	// mg names appear before constituents
	for (let i=1; i < ngraphs ; i++) {

	    let thisgraph = graphs[i+2];
	    
	    if (thisgraph.endsWith("_status")) continue;

	    graphs_this_page.push(gdir + '/' + thisgraph);	    
	    gr_list.push(thisgraph.replace("_status_all",""));
	}
    }
}


function csv_filename()  {

    let csv_filename = '';

    if (Page == "Overview") { 
        csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${year_month}_ver${Version}.csv`;
    } else {	
        csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${Page}_${year_month}_ver${Version}.csv`;        
    }
    
    return csv_filename;    	
}    


async function build_page() {

    // graphs_this_page array is global

    let file = await openFile(graphs_filename);//'./RunPeriod-2023-01/v6/monitoring_graphs.root');

    if (!file) console.log("file not found",graphs_filename);
    if (!file) return;

    console.log("opened root file");

    // make html containing empty divs before reading the root file

    document.getElementById("graphs").innerHTML = '';    

    for (const fullgname of graphs_this_page) {	
        let gname = fullgname.split("/")[1];
	let html = make_graph_div(gname);
        document.getElementById("graphs").innerHTML += html;
    }

    const promises = [];
    const mg_cpts = [];
    const missing = [];
    
    for (const fullgname of graphs_this_page) {

	//let gname = fullgname.split("/")[1]; same as rootgraph.fName
	
        const promise = file.readObject(fullgname).then(rootgraph => {
	    
	    const mg_cpt = draw_graph_and_legend(rootgraph);
	    if (mg_cpt) mg_cpts.push(mg_cpt);
	    
        }).catch(err => {
            console.log(`Graph ${fullgname} was not found in the root file`);
            console.error(err);

	    const gname = fullgname.split("/")[1];
	    const anchorname = get_anchor_name(gname);
	    
	    document.getElementById(gname + "_wrapper").innerHTML = '';
	    missing.push(anchorname);
        });
	
        promises.push(promise);
    }

    await Promise.all(promises);

    if (missing.length > 0) {
        console.log('Missing graphs:');
	console.log(missing);
 
        for (const x of missing) {
            const index = gr_list.indexOf(x);

            if (index > -1) { // only splice array when item is found
                gr_list.splice(index, 1); // 2nd parameter means remove one item only
                console.log('removing',x,'from gr_list');
            }
        }
    }	

    if (mg_cpts.length == 0) return;

    //mg_cpts might not be ordered.
    let found_first = false;
    
    for (const x of gr_list) {
	if (mg_cpts.includes(x)) {
	    document.getElementById(x).innerHTML = '<div class="before_mg_constituents">MultiGraph components are shown below.</div>';
	    found_first = true;
	}
	if (found_first) break;
    }

}


function get_anchor_name(gname) {

    let anchorname = gname;

    if (gname.endsWith("_status_all")) anchorname = gname.substring(0,gname.length-11);

    return anchorname;

}


function make_graph_div(gname) {


    let gstyle = "graphpanel";
    if (gname.endsWith("_status_all")) gstyle = "statusgraphpanel";    

    const anchorname = get_anchor_name(gname);

    let divtext = `<div id="${anchorname}_wrapper" class="graph_wrapper">\n`; 

    divtext += `  <div id="${anchorname}" class="graph_top"></div>\n`; 
    divtext += `  <div id="gdiv_${anchorname}" class="${gstyle}"></div>\n`; 
        
    divtext += '  <div id="glinks_' + anchorname + '" class="graph_bottom"></div>\n'; 
    divtext += '</div>\n';

    return divtext;
        
}


function make_graph_links_html(anchorname) {

    const clickelement = 'click_info_' + anchorname;

    let details = '';

    if ((Page == '' || Page == "Overview") && anchorname != 'readiness') {
        let link = document.URL.split("?")[0] + `?RunPeriod=${RunPeriod}&Version=${Version}&Page=${anchorname}`;
        details = '    &nbsp;&nbsp;<a href=' + link + '>Details</a>';
    }
        
    let divtext = `    ${anchorname}`;    
    divtext += `    &nbsp;&nbsp;<button title="Copy the url for this plot" class="graph_url" id="btn_${anchorname}"><img src="link.png" alt="Copy url"></button>` + '\n';

    divtext += details;
    divtext += '    &nbsp;&nbsp;<span id="' + clickelement + '" class="click_info"></span>\n';

    return divtext;
        
}


function draw_graph_and_legend(rootgraph) {

    const aname = get_anchor_name(rootgraph.fName);

    const div_links = 'glinks_' + aname;    
    const divhtml = make_graph_links_html(aname);
	    
    document.getElementById(div_links).innerHTML = divhtml;
	    
    Object.assign(rootgraph, {fMarkerSize: 0.5, fMarkerStyle: 8, fMarkerColor: 890, fEditable: 0});

    // set range of status graphs uniformly
    if (rootgraph.fName.includes('status')) {
        rootgraph.fHistogram.fMinimum = -1.5;
        rootgraph.fHistogram.fMaximum = 1.5;
        rootgraph.fHistogram.fYaxis.fNdivisions = 103;
        rootgraph.fHistogram.fXaxis.fLabelSize = 0.047;
        rootgraph.fHistogram.fYaxis.fLabelSize = 0.047;
    }
    
    let drawlegend = false;	

    // don't draw legend on the status composite multigraph made in JS bc it kills the graph	
    if (rootgraph._typename == 'TMultiGraph') { // && !gname.includes('composite')) {
        if (rootgraph.fGraphs) {
            if (rootgraph.fGraphs.arr) {
                if (rootgraph.fGraphs.arr.length > 1 ) drawlegend = true;
	    }
	}
    }
	    
    const div_graph = 'gdiv_' + aname;

    draw(div_graph, rootgraph, 'ap;gridx;gridy;').then(painter => {     // draw the graph first, otherwise xmin gets reset to 0  !
        const clickelement = 'click_info_' + aname;
        painter.configureUserClickHandler(info => UserHandler(info, div_graph, clickelement));
    });

    if (drawlegend) {
        const legend = create('TLegend');
        const garr = rootgraph.fGraphs.arr;
        let y1 = 0.9 - 0.1*garr.length;
        if (y1<0.18) y1=0.18;

        Object.assign(legend, { fX1NDC: 0.91, fY1NDC: y1, fX2NDC: 1.0, fY2NDC: 0.9, fColumnSeparation:0, fMargin:0.15 });

        for (const g of garr) {
            let entry = create('TLegendEntry');
            Object.assign(entry, {fObject: g, fLabel: g.fName, fOption: 'p'});            
            legend.fPrimitives.Add(entry);
        }
        draw(div_graph,legend);
    }

    let first_mg_cpt = null;
    if (Page != "" && !rootgraph.fName.endsWith('status_all') && rootgraph._typename == 'TMultiGraph') {
	first_mg_cpt = rootgraph.fGraphs.arr[0].fName + '_' + rootgraph.fName;
    }
    return first_mg_cpt;    
}


async function readlist(listfile, reverse=false) {

    const text = await fetchfiledata(listfile);
    
    let returntext = '';

    if (!text) {  // file not found

        console.log('Error (readlist) - could not read the file '+listfile);
        returntext = false;

    } else {

        returntext = text.split('\n');    // array of lines,  with '' in last place

        if (returntext[returntext.length-1] === '') returntext.pop();

        if (reverse) returntext.reverse();
    
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
         if (list[i] == preselect) {
             c.selected = true;
         } 
    }
}


function show_problem(message) {
    document.getElementById("problems").innerHTML = message;
}


function UserHandler(info, divname, clickelement) {

    if (!info) {
        return true;
    }

    // for overall status, show rcdb link only

    const run = Math.trunc(info.obj.fX[info.bin]);  // fX contains floats
    const rcdburl = `https://halldweb.jlab.org/rcdb/runs/info/${run}`;
    
    let linktext = `<a href=${rcdburl}><img src="rcdb.png" alt="RCDB" height="16" width="16"/></a>`;
        
    if (info.name != 'readiness') {

        // single graphs:       divname gdiv_n_missing,          info.name n_missing  => graph n_missing
        // single mg component: divname gdiv_eff0_hitefficiency, info.name eff0_hitefficiency => eff0_hitefficiency
    
        // mg :                 divname gdiv_hitefficiency,      info.name eff0 -> eff0_hitefficiency
        // status mg :          divname gdiv_CDC,                info.name occ -> occ_status

        let gname = divname.slice(5); // remove gdiv_ from the front

        let thispage = Page; // use as the plot_collection array index
	
        if (Page == "Overview") {

	    thispage = gname;	    
	    gname = info.name + "_status";
	    
        } else {

	    if (gname == thispage) { // status graph
		gname = info.name + "_status";
		
	    } else if (gname != info.name) { // mg
                gname = info.name + '_' + gname;                
            }
	}
	
        const run_6digits = `${run}`.padStart(6,"0");   // add leading 0 for early run numbers
        let plotname = '';
    
        if (plot_collection[thispage][gname]) {
            plotname = plot_collection[thispage][gname];
        } else {
            console.log(`click: plot_collection[${thispage}][${gname}] not found`);
        }

        if (plotname) {

	    let ver = `mon_ver${Version}`;

            if (Version[0] == "R") {
                const rest = Version[4];
		ver = `recon_ver0${rest}`;
            }

	    const ploturl = `https://halldweb.jlab.org/work/halld2/data_monitoring/${RunPeriod}/${ver}/Run${run_6digits}/${plotname}.png`;
		
            linktext += `&nbsp;&nbsp;<a href=${ploturl}>Monitoring histogram (${run})</a>`;
        }    
    }
    
    document.getElementById(clickelement).innerHTML = linktext;
    
    return true; // means event is handled and can be ignored
}

// when the RP or ver changes:
//      show the go/reload button 
//      hide the Page dropdown
//
// after reloading the page, 
//      hide the go/reload
//      show the Page dropdown
//
// after the Page changes
//      reload the page
//


select_rp.addEventListener('change', async function () {

    RunPeriod = select_rp.value;
    Version = '';
    Page = '';
    Graph = '';

    const listfile = `${RunPeriod}/versions.txt`;    
    const ver_list = await readlist(listfile);
    Version = ver_list[ver_list.length-1];  // suggest as default

    await fillmenu("select_ver",ver_list,Version);

});


select_rp.addEventListener('change',function() {

  console.log('rp menu changed');

  const sel = document.getElementById("select_page");
  sel.style.display = "none";

  const sel2 = document.getElementById("select_graph");
  sel2.style.display = "none";
    
  const btn = document.getElementById("reload");
  btn.style.display = "inline";

});


select_ver.addEventListener('change',function() {

  console.log('ver menu changed');

  const sel = document.getElementById("select_page");
  sel.style.display = "none";

  const sel2 = document.getElementById("select_graph");
  sel2.style.display = "none";
    
  const btn = document.getElementById("reload");
  btn.style.display = "inline";

});


select_page.addEventListener('change',function() {

  console.log('page menu changed');

  const btn = document.getElementById("reload");
  btn.style.display = "none";

  Page = select_page.value;

  const new_url = make_url_without_graph();
  window.location.assign(new_url);

});


select_graph.addEventListener('change',function() {

    const Graph = select_graph.value;
    if (Graph == '') return;

    const plain_url = make_url_without_graph();
    
    let new_url = plain_url + `#${Graph}`;

    window.location.assign(new_url);
    
});


//Go button loads new version
reload.addEventListener('click', function () {  
    console.log('reload');

    RunPeriod = select_rp.value;
    Version = select_ver.value;
    Page = "Overview";
    
    const new_url = make_url_without_graph();    
    
    window.location.assign(new_url);

});


function make_url_without_graph(){

    let new_url = document.URL.split("#")[0];

    new_url = new_url.split("?")[0] + `?RunPeriod=${RunPeriod}&Version=${Version}&Page=${Page}`;

    return new_url;
}


// copy-graph-url-to-clipboard code
document.addEventListener('click', (event) => {

    const btn = event.target.closest('div.graph_bottom button.graph_url');

    if (btn) {
        if (btn.id) {
            const clicked_graph = btn.id.split("btn_")[1]

            if (clicked_graph) {
      
                const plain_url = make_url_without_graph();
                let this_url = plain_url + `#${clicked_graph}`;

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
            }
        }
    }

    
}, {passive: true} );





//function copyURLtoClipboard() {
//            window.clipboardData.setData("Text",location.href);
//            }
