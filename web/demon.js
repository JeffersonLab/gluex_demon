// functions for gluex detector calibration monitoring page


var RunPeriod = "";
var Version = "";
var Detector = "";

var graphs_filename = "";  // root file
var pagenames = "";

var graphs_this_page = [];

import { openFile, draw } from 'https://root.cern/js/latest/modules/main.mjs';

$(document).ready(function () {

    get_url_args();

    if ( RunPeriod === "" || Version === "") {

        let example_url1 = document.URL.split("?")[0] + '?RunPeriod=RunPeriod-2022-05&Version=24';
        let example_url2 = document.URL.split("?")[0] + '?RunPeriod=RunPeriod-2023-01&Version=06';
        let errortext = '<span style="text-size:0.8em;">';
        errortext = errortext + `Incomplete url? <br/><br/> Try <a href="${example_url1}">${example_url1}</a><br/><br/>`;
        errortext = errortext + `or <a href="${example_url2}">${example_url2}</a>`;
        errortext = errortext + '</span>';

        document.getElementById("RunPeriod").innerHTML = errortext;
        document.getElementById("loading").innerHTML = "";
        document.getElementById("titles2").innerHTML = "";


    } else {

        document.getElementById("RunPeriod").innerHTML = RunPeriod;
        document.getElementById("Version").innerHTML = 'Version ' + Version;

        let year_month = RunPeriod.substring(10,17);
        let subtitle = Detector;
        let link_1 = "";
        let link_2 = "";

        graphs_filename = `./${RunPeriod}/${Version}/monitoring_graphs_${year_month}_ver${Version}.root`
        pagenames = `./${RunPeriod}/${Version}/monitoring_pagenames_${year_month}_ver${Version}.txt`
        let csv_filename = `./${RunPeriod}/${Version}/monitoring_data_${year_month}_ver${Version}.csv`

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

        getgraphnames();

        drawGraphs();
    }

});


async function fetchfiledata(filename) {
        const response = await fetch(filename);
      // waits until the request completes...

        const text = await response.text();

        return text;
}


function get_url_args() {

    /* read in the url, split it into arguments */

    let par_from_url = { RunPeriod: "", Version: "", Detector: ""};

    let currentURL_split = document.URL.split("?");
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


async function getgraphnames() {


    const homedir = 'https://halldweb.jlab.org/gluex_demon/';

    let group = [];
    let statusgraphs = ['readiness'];
    let detectors = [];
    let styletext = ' class="graphpanel"';
    let divtext = '';
    let linkfile = '';

    graphs_this_page = [];


    fetchfiledata(pagenames).then(
        function(text) {

        let lineArr = text.split('\n'); 
             // eg CDC - CPP,4,cdc_status,cdc_occ,cdc_missing,cdc_eff

        let npages = lineArr.length - 1;  // NO IDEA 

        for (let i=0; i<npages; i++) {
            group.push(lineArr[i].split(','));
            let name_without_spaces = group[i][0].replaceAll(" ","_");         
            detectors.push(name_without_spaces);
            statusgraphs.push(group[i][2]);   // overall readiness is first
        }

        if (Detector === "") {  // overview page

            for (let i = 0; i < statusgraphs.length; i++) {
                divtext += '<div id=' + statusgraphs[i] + styletext + '>';
                graphs_this_page.push(statusgraphs[i]);  // copy graph name into array for this page
                
                divtext += '</div>';

                if (i>0) { // no detector link for overall readiness

                    let thisdetector = detectors[i-1];

                    linkfile = document.URL + '&Detector=' + thisdetector;
                    divtext += '<span><a href=' + linkfile + '> ' + thisdetector + ' details </a>';
                    divtext += '</span>';

                }
            }          

        } else { // detector page

            for (let j = 0; j < detectors.length; j++) {
                if (Detector === detectors[j]) {
                    let ngraphs = group[j][1];
                    console.log('ngraphs:'+ngraphs);
                    for (let i = 2; i < ngraphs; i++) {
                        graphs_this_page.push(group[j][i]);  // copy graph name into array for this page
                        divtext += '<div id=' + group[j][i] + styletext + '>';
                        divtext += '</div>';
                    }
                }
            }          

        }

        document.getElementById("graphs").innerHTML = divtext;    

    },
        function(error){console.log('Error - could not read the file '+pagenames)}
    );

}

    
///import { openFile, draw } from 'https://root.cern/js/latest/modules/main.mjs';
    
//    $(document).ready(function () {
//        drawGraphs();
//    });
    
async function drawGraphs() {

    let file = await openFile(graphs_filename);//'./RunPeriod-2023-01/v6/monitoring_graphs.root');

    if (file) {
        console.log('file opened');
            
        const obj = [];

            // this makes an object named after the graph, which populates the div with the same name

        for (let i = 0; i < graphs_this_page.length; i++) {
            let gname = graphs_this_page[i];  //graphnames[i]
            obj[i] = await file.readObject(gname);
            obj[i].fMarkerSize=0.7;
            obj[i].fMarkerStyle=8;
            obj[i].fMarkerColor=890;
            obj[i].fEditable=0;

            await draw(gname, obj[i], 'ap;gridx;gridy;');
        }

        console.log('drawing completed');

    } else {
        console.log('cannot find file :-( ');  // I dont think this works
    }

}





/*<!--
<script>
    var PossiblePlots;
    PossiblePlots = ["CDC", "FCAL", "SC", "TOF", "DIRC", "BCAL", "FDC", "fa125_itrig"]
    possiblePlots = [];

    $(document).ready(function () {
        populatePlotDropdown();
    });

    function populatePlotDropdown() {
        const plotSelect = document.getElementById('detectorSelect');

        // Add 'All' option
        const allOption = document.createElement('option');
        allOption.value = 'All';
        allOption.textContent = 'All';
        plotSelect.appendChild(allOption);

        // Add options from keys array
        for (const plotName of PossiblePlots) {
            const option = document.createElement('option');
            option.value = plotName;
            option.textContent = plotName;
            plotSelect.appendChild(option);
            // Update possiblePlots array
            if (!possiblePlots.includes(plotName)) {
                possiblePlots.push(plotName);
            }
        }
    }

    detectorSelect.addEventListener('change', function () {
        const selectedDetector = detectorSelect.value;
        loadAndDisplayImage(selectedDetector);
    });

    function clearPlotContainer() {
        // Clear the plot container
        document.getElementById('plotContainer').innerHTML = '';
    }

    async function loadAndDisplayImage(detector) {
        const file = await JSROOT.openFile('./cdc_summary_histos.root');
        if (file) {
            console.log('File opened');

            // Construct the object name based on the selected detector
            const objectName = `gdedx`; //`${detector}_dedx/dedx_p`;

            try {
                const obj = await file.readObject(objectName);

                // Clear the plot container and draw the object
                clearPlotContainer();
                await JSROOT.draw('plotContainer', obj, 'ap');

                console.log('Drawing completed');
            } catch (error) {
                console.error('Error loading object:', error);
            }
        } else {
            console.error('Error opening file');
        }
    }

*/

