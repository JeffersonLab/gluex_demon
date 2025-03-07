// functions for gluex detector calibration monitoring page

var root_file = '/work/halld/data_monitoring/RunPeriod-2023-01/mon_ver12/rootfiles/hd_root_121168.root';

const coords_file = 'pin_coords_Al.txt';

const boards_file = 'boardlist.txt';


var radius = [];  // hole radius in inches
var theta = [] ; // hole phi in radians, with 0 at 9 o'clock and increasing clockwise

var xinfo = []; // list of info for each straw


import { openFile, draw, redraw, create, createTGraph, createTMultiGraph, createHistogram } from 'https://root.cern/js/latest/modules/main.mjs';
import { getColorPalette, addColor, adoptRootColors } from 'https://root.cern/js/latest/modules/base/colors.mjs';
        JSROOT.gStyle.fPadTopMargin = 0.5;


$(document).ready(async function () {

    await get_url_filename();

    
    //document.getElementById('filename').innerHTML = root_file;

    
    let text = await fetchfiledata(coords_file);

    radius = [];
    theta = [];
    
    let lineArr = text.split('\n');   // this needed \r\n for demon
    let nlines = lineArr.length - 1;  // ignore the empty last line

    //console.log(nlines);
    
    for (let i=0; i<nlines; i++) {
	
	let x = lineArr[i].split(' ');
	
        radius.push(parseFloat(x[1]));
        theta.push(3.1416 - parseFloat(x[2]));	
    }

    console.log('Read in coords for ',radius.length,' pins');


    text = await fetchfiledata(boards_file);

    xinfo = text.split('\n');

    console.log('Read in connector info for ',xinfo.length,' pins');
    
    await drawHisto();


});


function get_url_filename() {

    /* read in the url, split it into arguments */

    let par_from_url = { file: ""};

    let currentURL_split = document.URL.split("?");

    if (currentURL_split.length === 2) {
        let URL_AND_split = currentURL_split[1].split("&");
        for (let i = 0; i < URL_AND_split.length; i++) {
          let opt = URL_AND_split[i].split("=");
          par_from_url[opt[0]] = opt[1];
        }


    }

    if (par_from_url['file']) root_file = par_from_url['file'];
    
}




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





function show_problem(message) {
    document.getElementById("problems").innerHTML = message;
}

    
async function drawHisto() {

    let file = await openFile(root_file);


    if (file) {
        console.log('file opened');

	//document.getElementById("filename").innerHTML = root_file;
	
	const histoname = "/CDC/cdc_num_events";
        const nev = await file.readObject(histoname);

	let Nevents = 1e6;
        
        if (nev) Nevents = nev.getBinContent(1);

        const occ = [];


        let ax = createHistogram('TH2D',100,100);

        ax.fName = 'Hist1';
        ax.fTitle = root_file; //'';//CDC occupancy run xxx';

        ax.setBinContent(-66,-66,1);
	ax.setBinContent(66,66,1)

	ax.fXaxis.fXmin = -58;
        ax.fXaxis.fXmax = +58;
	ax.fYaxis.fXmin = -58;
        ax.fYaxis.fXmax = +58;

	ax.fXaxis.fLabelSize = 0;
	ax.fYaxis.fLabelSize = 0;

	ax.fXaxis.fTickLength = 0;
	ax.fYaxis.fTickLength = 0;
	
	ax.PadStats = false;
	
	console.log(ax);

	
	await draw('plot',ax,'NOSTAT');

        const counts = []
        const r = [];
	const phi = [];

	const description = [];
	
	let maxcounts = 0;

	let strawnum = 0;
	
	for ( let ring = 1 ; ring <= 28 ; ring++) {

	    const histoname = "/CDC/rings_occupancy/cdc_occ_ring[" + ring + "]";

            const h = await file.readObject(histoname);
	    
	    for (let straw = 1; straw <= h.fXaxis.fNbins; straw++ ) {
		const n = h.getBinContent(straw,1);

		counts.push(n);
		if (n>maxcounts) maxcounts = n;

		strawnum++;		
		description.push('Ring '+ring+' Straw '+straw + ' N ' + strawnum );
	    }

        }


	//const colours = [19, 859, 862, 869, 434, 839,  815, 397, 800, 91,  90 ];  //orig set using root's default palette
	
	const mypalette = getColorPalette(57,0);   //array of 255 kBird
	adoptRootColors(mypalette.palette);   // replace the first 255 root colours with mypalette array, starting with rgb (52,44, 138)
	adoptRootColors(['white', 'rgb(20,20,100)']);   // put almost black at the front; keep white as index 0 because root uses it for pad b/g

        //console.log(mypalette);
	
        const colours = [1 ];  // almost black for 0 counts

	const n=255;  // number of colours (254 is the max for the palette), first 2 were replaced
	
	for (let i=2; i<n ; i++) {
	    colours.push(i);   // store new array index for palette     
	    //colours.push(Math.floor(i*255/n));    // reinstate this if n < 255
	}

	
	const nbands = colours.length - 1;

	const cont = Math.ceil(maxcounts/(nbands));
	
	const contours = [0,  1];    // first colour band is for 0 counts (almost black)
	
	for (let i=0; i<nbands; i++) {    // highest one needs to stop above max counts
	    contours.push(contours[i+1] + cont);
	}

	const graphs=[];
	const info=[];
	
	for ( let c=0; c < contours.length - 1; c++ ) {

   	    const x1=[];
	    const y1=[];
	    
	    const tt = []; // tooltip eventually
	    const tt1 = [];
	    const tt2 = [];
	    
	    let np = 0; // point number for this graph
	    
  	    for (let i=0; i<3522; i++) {

	        if (counts[i] >= contours[c] && counts[i] < contours[c+1]) {
		    
		    x1.push(radius[i]*Math.cos(theta[i]));
		    y1.push(radius[i]*Math.sin(theta[i]));
		
		    tt.push(description[i]);

		    let text  = counts[i] + ' counts';
		    if (counts[i] == 1) text = counts[i] + ' count'; 
		    tt1.push(text);
		    
		    tt2.push(xinfo[i]);

		    np++;
		}
            }

        
            graphs[c] = createTGraph(x1.length,x1,y1); //define graph
	    Object.assign(graphs[c], {fTitle: 'Graph '+c, fMarkerSize: 1.05, fMarkerStyle: 8, fMarkerColor: colours[c], fEditable: 0});

	    const painter = await draw('plot', graphs[c], 'P same');
	    
	    //if (c==0) console.log(painter);

	    // replace tooltips only in this painter
	    painter.originalgetTooltips = painter.getTooltips;
	    painter.getTooltips = function(d) {
	    const res = this.originalgetTooltips(d);
            res.shift(); // remove first line
	    res.shift(); // remove line
	    res.shift(); // remove line
	    res.shift(); // remove line
	    res.push('');
	    res.push('  ' + tt[d.indx]);
	    res.push('');
	    res.push(tt1[d.indx]);  
	    let x = tt2[d.indx].indexOf('Conn');
	    res.push('');
            res.push('  ' + tt2[d.indx].slice(0,x-1) + '  ');
	    res.push('');
	    res.push(tt2[d.indx].slice(x));		   
	    res.push('');
	  
            return res;
      }

	
        }
      
        console.log('drawing completed');

    } else {
        console.log('cannot find file :-( ');  // I dont think this works
	show_problem('File not found');
    }

}


function UserHandler(info) {

    console.log(info);
    
         if (!info) {
            document.getElementById('tooltip').innerHTML = 'No info';
            //last_hbin = -1;
            return false;
         }
 
         //last_hbin = info.bin;
 
         // show info
         document.getElementById('tooltip').innerHTML = ` ${info.at} `;
 
         return true; // means event is handled and can be ignored
 }


function CreateLegendEntry(obj, lbl, mkr) {
         let entry = create('TLegendEntry');
         entry.fObject = obj;
         entry.fLabel = lbl;
         entry.fOption = 'p';
         entry.fMarkerStyle = mkr;
         return entry;
}



async function fetchfiledata(filename) {

    const response = await fetch(filename+'?'+Math.random());   // requesting filename?random avoids the data being cached

    let text = await response.text();
    // this will be 404 if the file doesn't exist
    // console.log(text);

    if (text.includes('404 Not Found')) {
        console.log('ERROR: ' + filename + ' not found!');
        show_problem(filename + ' is missing!');
        text = false;
    }

    return text;

}






