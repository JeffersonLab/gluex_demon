// functions for gluex detector calibration monitoring page

const RP_file = './runperiods.txt';

var RP_list = [];  // list of available run periods  in runperiods.txt
var ver_list = []; // list of available versions     in versions.txt inside RP's subdir
var det_list = []; // list of available detectors/modules   in pagenames 
var gr_list = [];

var graph_collection = [];  // vast 2D list of graphs             in pagenames
var graphs_this_page = [];   // list of graphs on the current page loaded from the file (may include nonexistent graphs)

var plot_collection = '';

var RunPeriod = "";
var Version = "";
var Detector = "";
var Graph = "";

var graphs_filename = "";  // root file
var csv_filename = "";
var pagenames = "";  // file containing lists of graphs
var plotnames = "";  // file containing lists of plots

var year_month = "";


//import { openFile, draw, create, settings } from 'https://jsroot.gsi.de/latest/modules/main.mjs';
import { openFile, draw, create, settings } from 'https://root.cern/js/latest/modules/main.mjs';


await get_url_args();

RP_list = await readlist(RP_file, true);

if ( RunPeriod === "" ) {

    RunPeriod = RP_list[0];
    Version = "";
    Detector = "";
    Graph = "";
    
} else if (! RP_list.includes(RunPeriod) ) {

    show_problem(`${RunPeriod} is not known!`);

    RunPeriod = RP_list[0];
    Version = "";
    Detector = "";
    Graph = "";
    
} 
    
await fillmenu("select_rp",RP_list,RunPeriod);

ver_list = [];
gr_list = [];

ver_list = await readlist(`${RunPeriod}/versions.txt`, true);

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


year_month = RunPeriod.substring(10,17);

graphs_filename = `./${RunPeriod}/${Version}/monitoring_graphs_${year_month}_ver${Version}.root`;
csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${year_month}_ver${Version}.csv`;
pagenames = `./${RunPeriod}/${Version}/monitoring_pagenames_${year_month}_ver${Version}.txt`;
plotnames = `./${RunPeriod}/${Version}/monitoring_plotnames_${year_month}_ver${Version}.txt`;

let compare_link = `https://halldweb.jlab.org/gluex_demon/compare.html?RunPeriod=${RunPeriod}&Version=${Version}`;
    
await getdetectornames();	// this fills det_list and graph_collection
console.log("collected detector names and graphs");

if (Detector != "" && ! det_list.includes(Detector) ) {   //det_list[0] is "Overview"
    show_problem(`${RunPeriod} version ${Version} does not include ${Detector}!`);
    Detector = "";
}

await fillmenu("select_det",det_list,Detector);


console.log('filled detector menu');

let subtitle = "Overview";
let link_1 = `<a href="${graphs_filename}">ROOT file</a>`;
let link_2 = `<a href="${csv_filename}">CSV file</a>`;
let link_3 = `<a href="${compare_link}">Compare graphs</a>`;    

if (Detector !== "") {
    subtitle = Detector;
}

document.getElementById("Detector").innerHTML = subtitle;

document.getElementById("rootfile").innerHTML = link_1;
document.getElementById("csv").innerHTML = link_2;
document.getElementById("compare").innerHTML = link_3;

console.log("getting the list of graphs");

await get_list_of_graphs();

let selected = Graph;
if (selected == "") selected = "Overview";

console.log('awaiting build_page');

await build_page();

await fillmenu("select_graph",gr_list,selected);

console.log('page ready');


//------------------------------------


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


async function getdetectornames() {

    // fills global arrays det_list and graph_collection

    graphs_this_page = [];  // tells jsROOT which graphs to show

    let text = await fetchfiledata(pagenames);

    let lineArr = text.split('\r\n'); 
             // eg CDC - CPP,4,cdc_status,cdc_occ,cdc_missing,cdc_eff

    let npages = lineArr.length - 1;  // ignore the empty last line

    det_list = ["Overview"];

    for (let i=0; i<npages; i++) {
        graph_collection.push(lineArr[i].split(','));
        let name_without_spaces = graph_collection[i][0].replaceAll(" ","_");         
        det_list.push(name_without_spaces);
    }

    plot_collection = await fetchjson(plotnames);

}



async function get_list_of_graphs() {

    graphs_this_page = [];  // tells jsROOT which graphs to show

    let thisdet = "";

    if (Detector) {
	if (Detector != "Overview") thisdet = Detector;
    }
    

    if (thisdet == "") { 
	let npages = det_list.length;  // NB it starts with "" for overview
        
        for (let i = 0; i < npages; i++) {
    
            let thisgraph = 'readiness';
            let gdir = '';

            if (i>0 ) {
                gdir = graph_collection[i-1][0]; 
                thisgraph = graph_collection[i-1][2];
            }

            graphs_this_page.push(gdir + '/' + thisgraph);  // copy graph name into array for this page

	}

    } else  {    // detector page
	
        let j = det_list.indexOf(Detector) - 1;   // because det_list starts w overview

	const graphs = graph_collection[j];
        const gdir = graphs[0]; 
        const ngraphs = Number(graphs[1]); 
        const status_composite = graphs[2];
	
	graphs_this_page.push(gdir + '/' + status_composite);

	// mg names appear before constituents
	for (let i=1; i < ngraphs ; i++) {

	    let thisgraph = graphs[i+2];
	    
	    if (thisgraph.endsWith("_status")) continue;

	    graphs_this_page.push(gdir + '/' + thisgraph);	    
	}

    }
}

async function make_csv_link()  {

    let page_csv_filename = csv_filename; //global, link for big csv file from overview page
    let link_text = 'CSV file';

    if (Detector != "") {  // detector page
        page_csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${Detector}_${year_month}_ver${Version}.csv`;
        link_text = 'CSV file for this page';
    }
    
    const file_exists = await fetchfiledata(page_csv_filename,true);
    let csv_link = '';
    
    if (file_exists) {
	csv_link = `<a href="${page_csv_filename}">${link_text}</a>`;
    } else {
	csv_link = `CSV file not found: ${page_csv_filename}`;
    }

    document.getElementById("csv").innerHTML = csv_link;
	
}    


async function build_page() {

    // graphs_this_page array is global

    let file = await openFile(graphs_filename);//'./RunPeriod-2023-01/v6/monitoring_graphs.root');

    if (!file) console.log("file not found",graphs_filename);
    if (!file) return;

    console.log("opened root file");

    // make html containing empty divs before reading the root file

    document.getElementById("graphs").innerHTML = '';    
    console.log();
    for (const fullgname of graphs_this_page) {	
        let gname = fullgname.split("/")[1];
	let html = make_graph_div(gname);
        document.getElementById("graphs").innerHTML += html;
	gr_list.push(gname.replace("_status_all",""));
    }

    const promises = [];
    const mg_cpts = [];
    const missing = [];
    
    for (const fullgname of graphs_this_page) {

	console.log(fullgname);
	//let gname = fullgname.split("/")[1]; same as rootgraph.fName
	
        const promise = file.readObject(fullgname).then(rootgraph => {
	    
	    const mg_cpt = draw_graph_and_legend(rootgraph);
	    if (mg_cpt) mg_cpts.push(mg_cpt);
	    
        }).catch(err => {
            console.log(`Graph ${fullgname} was not found in the root file`);
            console.error(err);

	    let gname = fullgname.split("/")[1];
	    let anchorname = get_anchor_name(gname);
	    
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
	    document.getElementById(x).innerHTML = '<div class="before_mg_constituents">MultiGraph components are shown below.</div>';           found_first = true;
	    console.log('First mg component graph is ',x);
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


    const styletext = ' class="graphpanel"';
    const styletext2 = ' class="statusgraphpanel"';

    let style = styletext;
    if (gname.endsWith("_status_all")) style = styletext2;

    let anchorname = get_anchor_name(gname);

    //console.log('   ',anchorname);

    let divtext = `<div id="${anchorname}_wrapper" class="graph_wrapper">\n`; 
    
    divtext += `  <div id="${anchorname}" class="graph_top"></div>\n`; 
    divtext += '  <div id="gdiv_' + anchorname + '" ' + style + '></div>\n'; 
    divtext += '  <div id="glinks_' + anchorname + '" class="graph_bottom"></div>\n'; 
    divtext += '</div>\n';
    
    return divtext;
        
}


function make_graph_links_html(anchorname) {

    const clickelement = 'click_info_' + anchorname;

    let details = '';

    if (Detector == '' && anchorname != 'readiness') {
        let link = document.URL.split("?")[0] + `?RunPeriod=${RunPeriod}&Version=${Version}&Detector=${anchorname}`;
        details = '    &nbsp;&nbsp;<a href=' + link + '>Details</a>';
    }
        
    let divtext = '\n';

    divtext += `    <button title="Copy the url for this plot" class="graph_url" id="btn_${anchorname}"><img src="link.png" alt="Copy url"></button>` + '\n';
    divtext += `    &nbsp;&nbsp;<a href="#${anchorname}">${anchorname}</a>`;
    divtext += '    &nbsp;&nbsp;<a href="#top">Top of page</a>';
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
        let legend = create('TLegend');
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
    if (Detector != "" && !rootgraph.fName.endsWith('status_all') && rootgraph._typename == 'TMultiGraph') {
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

    if (reverse) {
        returntext.reverse();
    }
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

    console.log('click: divname: '+divname);

    if (!info) {
        return true;
    }

    console.log('click: info:', info);

    // for overall status, show rcdb link only

    let run = Math.trunc(info.obj.fX[info.bin]);  // fX contains floats
    let rcdburl = `https://halldweb.jlab.org/rcdb/runs/info/${run}`;    
    let linktext = `<a href=${rcdburl}><img src="rcdb.png" alt="RCDB" height="16" width="16"/></a>`;

    let ploturl = '';
    let showplot = true;
    
    if (info.name == 'readiness') showplot = false;
    
    if (showplot) {

    // single graphs:       divname gdiv_n_missing,          info.name n_missing  => graph n_missing
    // single mg component: divname gdiv_eff0_hitefficiency, info.name eff0_hitefficiency => eff0_hitefficiency
    
    // mg :                 divname gdiv_hitefficiency,      info.name eff0 -> eff0_hitefficiency
    // status mg :          divname gdiv_CDC_status_all,     info.name occ -> occ_status
    
    let gname = divname.slice(5); // remove gdiv_ from the front

    if (gname != info.name) { // mg
        if (divname.endsWith('status_all')) {
        gname = info.name + '_status';
        } else {
        gname = info.name + '_' + gname;
        }
    }
    
    console.log('graph name:',gname);
    
    let thisdetector = Detector;

    if (Detector == '') {
        thisdetector = divname.slice(5).replace('_status_all','');
    }

    let run_6digits = `${run}`.padStart(6,"0");   // add leading 0 for early run numbers
    let plotname = '';
    
    if (plot_collection[thisdetector][gname]) {
        plotname = plot_collection[thisdetector][gname];
        console.log('click: plotname: ' +plotname);
    } else {
            console.log(`click: plot_collection[${thisdetector}][${gname}] not found`);
    }

    if (plotname) {

            let ploturl = `https://halldweb.jlab.org/work/halld2/data_monitoring/${RunPeriod}/mon_ver${Version}/Run${run_6digits}/${plotname}.png`;
            if (Version[0] == "R") {
        let rest = Version[4];
        ploturl = `https://halldweb.jlab.org/work/halld2/data_monitoring/${RunPeriod}/recon_ver0${rest}/Run${run_6digits}/${plotname}.png`;
        }

            linktext += `&nbsp;&nbsp;<a href=${ploturl}>Monitoring histogram (${run})</a>`;
    }    
    }
    

    document.getElementById(clickelement).innerHTML = linktext;
    
    return true; // means event is handled and can be ignored
}


select_rp.addEventListener('change', async function () {
    const selectedRP = select_rp.value;
    let listfile = `${selectedRP}/versions.txt`;

    Version = '';
    Detector = '';
    Graph = '';

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

  const sel2 = document.getElementById("select_graph");
  sel2.style.display = "none";
    
  const btn = document.getElementById("reload");
  btn.style.display = "inline";

});


select_ver.addEventListener('change',function() {

  console.log('ver menu changed');

  const sel = document.getElementById("select_det");
  sel.style.display = "none";

  const sel2 = document.getElementById("select_graph");
  sel2.style.display = "none";
    
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

  // trim local bookmark #graphname
    
  let new_url = document.URL.split("#")[0];
  new_url = new_url.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}`;

  if ( det != "" && det != "Overview" ) {
    new_url = new_url + `&Detector=${det}`;
  }

  console.log(new_url);
  window.location.assign(new_url);

});


select_graph.addEventListener('change',function() {

  const Graph = select_graph.value;
  if (Graph == '') return;

  const btn = document.getElementById("reload");
  btn.style.display = "none";

  const RP = select_rp.value;
  const ver = select_ver.value;
  const det = select_det.value;

  // trim local bookmark #graphname
    
  let new_url = document.URL.split("#")[0];
  new_url = new_url.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}&Detector=${det}#${Graph}`;

  console.log(new_url);
  window.location.assign(new_url);

    /*
    console.log('graph menu changed');

    if (Graph != "") {
    document.getElementById(Graph).scrollIntoView();
    } */
    
});


reload.addEventListener('click', function () {  
  console.log('reload');
  const RP = select_rp.value;
  const ver = select_ver.value;
    
  let new_url = document.URL.split("#")[0];
  new_url = new_url.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}`;

  console.log(new_url);
  window.location.assign(new_url);

});


// copy-graph-url-to-clipboard code
document.addEventListener('click', (event) => {
    // Use .closest() to find the target element or its parent with a specific selector

    console.log('clicked');
    
  const btn = event.target.closest('div.graph_bottom button.graph_url');

  if (btn) {
      console.log('Button clicked:', btn.id);

      if (btn.id) {
          let clicked_graph = btn.id.split("btn_")[1]

      if (clicked_graph) {
      
            const RP = select_rp.value;
            const ver = select_ver.value;
            const det = select_det.value;

          let thisdet = "";
        if (det != "" && det != "Overview") {
            thisdet = `&Detector=${det}`;
        }

        let this_url = document.URL.split("#")[0];
            this_url = this_url.split("?")[0] + `?RunPeriod=${RP}&Version=${ver}${thisdet}#${clicked_graph}`;
          
            console.log(clicked_graph);
            console.log(this_url);

            const tempInput = document.createElement('textarea');
            tempInput.value = this_url;
            document.body.appendChild(tempInput);
            tempInput.select();
            tempInput.setSelectionRange(0, 99999);

            try {
               document.execCommand('copy');
//              alert('URL copied to clipboard!');
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
