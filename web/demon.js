// functions for gluex detector calibration monitoring page

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

var year_month = "";

import { openFile, draw, create, settings } from 'https://root.cern/js/latest/modules/main.mjs';


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


    year_month = RunPeriod.substring(10,17);

    graphs_filename = `./${RunPeriod}/${Version}/monitoring_graphs_${year_month}_ver${Version}.root`;
    csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${year_month}_ver${Version}.csv`;
    pagenames = `./${RunPeriod}/${Version}/monitoring_pagenames_${year_month}_ver${Version}.txt`;

    let compare_link = `https://halldweb.jlab.org/gluex_demon/compare.html?RunPeriod=${RunPeriod}&Version=${Version}`;

    await getdetectornames();	// this fills det_list and graph_collection


    if (! det_list.includes(Detector) ) {   //det_list[0] is ""
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
        document.getElementById("return").innerHTML = `<a href="${document.URL.split("&Detector")[0]}">Return to overview page</a>`;
    }

    document.getElementById("Detector").innerHTML = subtitle;

    document.getElementById("rootfile").innerHTML = link_1;
    document.getElementById("csv").innerHTML = link_2;
    document.getElementById("compare").innerHTML = link_3;

    document.getElementById("loading").innerHTML = "Loading...";

    await getgraphnames();   // reads graph names from pagenames file

    drawGraphs().then(
       function(text) { 
           //console.log(Graph);
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
    let styletext2 = ' class="statusgraphpanel"';
    let divtext = '';
    let linkfile = '';
    let listoflinks = '<ul>';

    graphs_this_page = [];  // tells jsROOT which graphs to show

    console.log('Detector: '+Detector)
    
    if (Detector != "") {  // detector page
//        let year_month = `${RunPeriod}.substring(10,17)`;
        let page_csv_filename = `./${RunPeriod}/${Version}/monitoring_page_${Detector}_${year_month}_ver${Version}.csv`;
	const file_exists = await fetchfiledata(page_csv_filename,true);
        let csv_link = '';
	if (file_exists) {
	    csv_link = `<a href="${page_csv_filename}">CSV file for this page</a>`;
        }
	//let csv_link = `<a href="${page_csv_filename}">CSV file for this page</a>`;
        document.getElementById("csv").innerHTML = csv_link;
	
        let j = det_list.indexOf(Detector) - 1;   // because det_list starts w overview

        const gdir = graph_collection[j][0]; 
        const ngraphs = Number(graph_collection[j][1]); 

        for (let i = 2; i < ngraphs+2 ; i++) {

            let thisgraph =  graph_collection[j][i];
            let rootgraph =  gdir + '/' + thisgraph;
            let style = styletext

            // only show composite status_all graphs, hide the other status graphs
            if (thisgraph.endsWith('status')) continue; 

            graphs_this_page.push(rootgraph);  // copy graph name into array for this page

	    let anchorname = thisgraph;
	    if (thisgraph.endsWith("_status_all")) {
		anchorname = thisgraph.substring(0,thisgraph.length-4);  // trim _all
	    }
	    
            divtext += `<div id="${anchorname}" class="graph_top"></div>`;

            divtext += '<div id=gdiv_' + thisgraph + style + '>';
            divtext += '</div>';

            divtext += `<div class="graph_names"><a href="#${anchorname}">${anchorname}</a>&nbsp;&nbsp;<a href="#selectors">Top of page</a></div>`;
            listoflinks += `<li><a href = "#${anchorname}">${anchorname}</a></li> `;

        }

    } else  {    // overview page

        let csv_link = `<a href="${csv_filename}">CSV file</a>`;
        document.getElementById("csv").innerHTML = csv_link;    

	let npages = det_list.length;  // NB it starts with "" for overview

        // start at -1 for readiness
        for (let i = 0; i < npages; i++) {

            let thisgraph = 'readiness';
            let gdir = '';

            if (i>0 ) {
                gdir = graph_collection[i-1][0]; 
                thisgraph = graph_collection[i-1][2];
            }

            let rootgraph =  gdir + '/' + thisgraph;

            graphs_this_page.push(rootgraph);  // copy graph name into array for this page

	    let anchorname = thisgraph;
	    if (thisgraph.endsWith("_status_all")) {
		anchorname = thisgraph.substring(0,thisgraph.length-11);
	    }
	    
            divtext += `<div id="${anchorname}" class="graph_top"></div>`;

            divtext += `<div id=gdiv_${thisgraph} ${styletext}></div>`;  // the graph gets inserted inside this later

            divtext += `<div class="graph_names"><a href="#${anchorname}">${anchorname}</a>&nbsp;&nbsp;<a href="#selectors">Top of page</a>`; //</div>`;

            listoflinks += `<a href = "#${anchorname}">${anchorname}</a> `;

            if (i>0) { // no detector link for overall readiness

                let thisdetector = det_list[i]; 

                linkfile = document.URL.split("#")[0] + '&Detector=' + thisdetector;   // ignore #graphname
//                divtext += '<span><a href=' + linkfile + '> ' + thisdetector + ' details </a>';
//                divtext += '</span>';
                divtext += '&nbsp;&nbsp;<a href=' + linkfile + '>Details</a>';
            }

            divtext += '</div>';

        }          

    } 

    listoflinks += '</ul>';
    document.getElementById("graphs").innerHTML = divtext;    
    document.getElementById("links_graphs_this_page").innerHTML = 'Graphs on this page: ' + listoflinks;    

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
            
        const obj = [];
        const leg = [];
	
        // this makes an object named after the graph, which populates the div with the same name

        for (let i = 0; i < graphs_this_page.length; i++) {

            const gname = graphs_this_page[i];  //graphnames[i]

            const divname = 'gdiv_' + gname.split('/')[1];      // the divname doesnt include the directory
	    
            // only show composite status graphs, hide the others
            if (gname.endsWith('status')) continue;
	    
            obj[i] = await file.readObject(gname).catch((err) => {       
                console.error(err);
		return null;     // graph not found
            });
	    
	    if (obj[i] == null) {  
                const thisdiv = document.getElementById(divname);
	        thisdiv.innerHTML = 'Graph ' + gname + ' is not in the root file.';
		thisdiv.classList.remove("graphpanel"); 
		thisdiv.classList.add("graphmissing"); 
		continue;  
	    }
	    
	    Object.assign(obj[i], {fMarkerSize: 0.5, fMarkerStyle: 8, fMarkerColor: 890, fEditable: 0});
	    
            if (gname.includes('status')) {
                obj[i].fMinimum = -1.5;
                obj[i].fMaximum = 1.5;
		// obj[i].fYaxis.fNdivisions = 1;  // gives an error
            }

            let drawlegend = false;
   	    leg[i] = await create('TLegend');    
	    
	    if (obj[i]._typename == 'TMultiGraph') { // && !gname.includes('composite')) {                 

		if (obj[i].fGraphs) {
		    if (obj[i].fGraphs.arr) {
			if (obj[i].fGraphs.arr.length>1 ) drawlegend = true;      // don't draw legend on the status composite multigraph made in JS bc it kills the graph
			console.log('set drawlegend');
		    }
		}
	    }
		    
	    if (drawlegend) {
		
		const garr = obj[i].fGraphs.arr;
		let y1 = 0.9 - 0.1*garr.length;
		if (y1<0.18) y1=0.18;
		
                Object.assign(leg[i], { fX1NDC: 0.91, fY1NDC: y1, fX2NDC: 1.0, fY2NDC: 0.9, fColumnSeparation:0, fMargin:0.15 });

	        const entry = []

		for (let j=0; j < garr.length; j++) {
		
		    entry[j] = await create('TLegendEntry');
		    Object.assign(entry[j], {fObject: garr[j], fLabel: garr[j].fName, fOption: 'p'});
			
   		    await leg[i].fPrimitives.Add(entry[j]);

		}
            }

            let gpainter = await draw(divname, obj[i], 'ap;gridx;gridy;');     // draw the graph first, otherwise xmin gets reset to 0  !
            if (drawlegend) await draw(divname,leg[i]);	    

           // TMultiGraphPainter has array of Painters with xmin and xmax set to range   autorange set to true
	    // data are in arrays fX  fY
	    
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



