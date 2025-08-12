/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var showControllersOnly = false;
var seriesFilter = "";
var filtersOnlySampleSeries = true;

/*
 * Add header in statistics table to group metrics by category
 * format
 *
 */
function summaryTableHeader(header) {
    var newRow = header.insertRow(-1);
    newRow.className = "tablesorter-no-sort";
    var cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Requests";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 3;
    cell.innerHTML = "Executions";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 7;
    cell.innerHTML = "Response Times (ms)";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Throughput";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 2;
    cell.innerHTML = "Network (KB/sec)";
    newRow.appendChild(cell);
}

/*
 * Populates the table identified by id parameter with the specified data and
 * format
 *
 */
function createTable(table, info, formatter, defaultSorts, seriesIndex, headerCreator) {
    var tableRef = table[0];

    // Create header and populate it with data.titles array
    var header = tableRef.createTHead();

    // Call callback is available
    if(headerCreator) {
        headerCreator(header);
    }

    var newRow = header.insertRow(-1);
    for (var index = 0; index < info.titles.length; index++) {
        var cell = document.createElement('th');
        cell.innerHTML = info.titles[index];
        newRow.appendChild(cell);
    }

    var tBody;

    // Create overall body if defined
    if(info.overall){
        tBody = document.createElement('tbody');
        tBody.className = "tablesorter-no-sort";
        tableRef.appendChild(tBody);
        var newRow = tBody.insertRow(-1);
        var data = info.overall.data;
        for(var index=0;index < data.length; index++){
            var cell = newRow.insertCell(-1);
            cell.innerHTML = formatter ? formatter(index, data[index]): data[index];
        }
    }

    // Create regular body
    tBody = document.createElement('tbody');
    tableRef.appendChild(tBody);

    var regexp;
    if(seriesFilter) {
        regexp = new RegExp(seriesFilter, 'i');
    }
    // Populate body with data.items array
    for(var index=0; index < info.items.length; index++){
        var item = info.items[index];
        if((!regexp || filtersOnlySampleSeries && !info.supportsControllersDiscrimination || regexp.test(item.data[seriesIndex]))
                &&
                (!showControllersOnly || !info.supportsControllersDiscrimination || item.isController)){
            if(item.data.length > 0) {
                var newRow = tBody.insertRow(-1);
                for(var col=0; col < item.data.length; col++){
                    var cell = newRow.insertCell(-1);
                    cell.innerHTML = formatter ? formatter(col, item.data[col]) : item.data[col];
                }
            }
        }
    }

    // Add support of columns sort
    table.tablesorter({sortList : defaultSorts});
}

$(document).ready(function() {

    // Customize table sorter default options
    $.extend( $.tablesorter.defaults, {
        theme: 'blue',
        cssInfoBlock: "tablesorter-no-sort",
        widthFixed: true,
        widgets: ['zebra']
    });

    var data = {"OkPercent": 100.0, "KoPercent": 0.0};
    var dataset = [
        {
            "label" : "FAIL",
            "data" : data.KoPercent,
            "color" : "#FF6347"
        },
        {
            "label" : "PASS",
            "data" : data.OkPercent,
            "color" : "#9ACD32"
        }];
    $.plot($("#flot-requests-summary"), dataset, {
        series : {
            pie : {
                show : true,
                radius : 1,
                label : {
                    show : true,
                    radius : 3 / 4,
                    formatter : function(label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                            + label
                            + '<br/>'
                            + Math.round10(series.percent, -2)
                            + '%</div>';
                    },
                    background : {
                        opacity : 0.5,
                        color : '#000'
                    }
                }
            }
        },
        legend : {
            show : true
        }
    });

    // Creates APDEX table
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.896551724137931, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [1.0, 500, 1500, "comparison temperature (1d)"], "isController": false}, {"data": [1.0, 500, 1500, "GET http://altbau_vs_neubau_frontend/-1"], "isController": false}, {"data": [0.0, 500, 1500, "GET http://altbau_vs_neubau_frontend/-2"], "isController": false}, {"data": [1.0, 500, 1500, "GET http://altbau_vs_neubau_frontend/-0"], "isController": false}, {"data": [1.0, 500, 1500, "comparison temperature (1w)"], "isController": false}, {"data": [1.0, 500, 1500, "GET http://altbau_vs_neubau_frontend/-5"], "isController": false}, {"data": [1.0, 500, 1500, "GET http://altbau_vs_neubau_frontend/-3"], "isController": false}, {"data": [1.0, 500, 1500, "GET http://altbau_vs_neubau_frontend/-4"], "isController": false}, {"data": [1.0, 500, 1500, "comparison temperature (3h)"], "isController": false}, {"data": [1.0, 500, 1500, "comparison pollen (1m)"], "isController": false}, {"data": [1.0, 500, 1500, "SET metrics"], "isController": false}, {"data": [1.0, 500, 1500, "comparison pollen (1w)"], "isController": false}, {"data": [1.0, 500, 1500, "comparison humidity (1w)"], "isController": false}, {"data": [0.0, 500, 1500, "Initial Page TTLB"], "isController": true}, {"data": [1.0, 500, 1500, "comparison humidity (1m)"], "isController": false}, {"data": [1.0, 500, 1500, "comparison particulate_matter (3h)"], "isController": false}, {"data": [1.0, 500, 1500, "Click 1d"], "isController": true}, {"data": [1.0, 500, 1500, "Click 3h"], "isController": true}, {"data": [1.0, 500, 1500, "comparison particulate_matter (1d)"], "isController": false}, {"data": [1.0, 500, 1500, "comparison humidity (3h)"], "isController": false}, {"data": [1.0, 500, 1500, "comparison pollen (3h)"], "isController": false}, {"data": [1.0, 500, 1500, "comparison pollen (1d)"], "isController": false}, {"data": [1.0, 500, 1500, "Click 1m"], "isController": true}, {"data": [1.0, 500, 1500, "comparison particulate_matter (1m)"], "isController": false}, {"data": [1.0, 500, 1500, "comparison humidity (1d)"], "isController": false}, {"data": [0.0, 500, 1500, "GET http://altbau_vs_neubau_frontend/"], "isController": false}, {"data": [1.0, 500, 1500, "comparison particulate_matter (1w)"], "isController": false}, {"data": [1.0, 500, 1500, "comparison temperature (1m)"], "isController": false}, {"data": [1.0, 500, 1500, "Click 1w"], "isController": true}]}, function(index, item){
        switch(index){
            case 0:
                item = item.toFixed(3);
                break;
            case 1:
            case 2:
                item = formatDuration(item);
                break;
        }
        return item;
    }, [[0, 0]], 3);

    // Create statistics table
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 360, 0, 0.0, 160.81388888888887, 0, 2021, 29.0, 34.0, 1645.0, 1710.85, 22.400597349262647, 1131.4382272416153, 4.9529966632443525], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["comparison temperature (1d)", 15, 0, 0.0, 29.066666666666666, 27, 32, 29.0, 32.0, 32.0, 32.0, 1.1485451761102605, 2.921761341883614, 0.2512442572741194], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-1", 15, 0, 0.0, 0.20000000000000004, 0, 1, 0.0, 1.0, 1.0, 1.0, 1.0793696481254946, 16.49622557926171, 0.15284042868964526], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-2", 15, 0, 0.0, 1646.4666666666667, 1604, 1844, 1630.0, 1746.8, 1844.0, 1844.0, 0.9676170816668818, 1.0167538865952779, 0.15308004612308088], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-0", 15, 0, 0.0, 2.1333333333333337, 0, 23, 1.0, 9.800000000000008, 23.0, 23.0, 1.075268817204301, 1.158224126344086, 0.13650873655913978], "isController": false}, {"data": ["comparison temperature (1w)", 15, 0, 0.0, 28.333333333333332, 27, 33, 28.0, 30.6, 33.0, 33.0, 1.1498658489842852, 0.9552270985051744, 0.2515331544653124], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-5", 15, 0, 0.0, 0.39999999999999997, 0, 1, 0.0, 1.0, 1.0, 1.0, 1.1052980620440644, 6.248603985520596, 0.17054403691695527], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-3", 15, 0, 0.0, 32.93333333333334, 30, 36, 33.0, 36.0, 36.0, 36.0, 1.1027790030877813, 1.2471597697029848, 0.17877081495368327], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-4", 15, 0, 0.0, 2.0, 2, 2, 2.0, 2.0, 2.0, 2.0, 1.1052166224580018, 600.9561418959992, 0.16837284482758622], "isController": false}, {"data": ["comparison temperature (3h)", 15, 0, 0.0, 30.8, 29, 35, 30.0, 33.8, 35.0, 35.0, 1.1470520761642578, 18.168453558729066, 0.2565184818765772], "isController": false}, {"data": ["comparison pollen (1m)", 15, 0, 0.0, 28.399999999999995, 27, 31, 28.0, 30.4, 31.0, 31.0, 1.1517199017199018, 0.5496913150721745, 0.2463150961686118], "isController": false}, {"data": ["SET metrics", 15, 0, 0.0, 19.333333333333332, 0, 284, 0.0, 114.2000000000001, 284.0, 284.0, 1.1184848258891955, 0.0, 0.0], "isController": false}, {"data": ["comparison pollen (1w)", 15, 0, 0.0, 28.133333333333333, 27, 29, 28.0, 29.0, 29.0, 29.0, 1.150483202945237, 0.8277337158689982, 0.24605060687988956], "isController": false}, {"data": ["comparison humidity (1w)", 15, 0, 0.0, 28.333333333333336, 26, 31, 28.0, 29.8, 31.0, 31.0, 1.1502185415228894, 0.8366042673107891, 0.24824052507476418], "isController": false}, {"data": ["Initial Page TTLB", 15, 0, 0.0, 1697.1333333333334, 1643, 2067, 1666.0, 1859.4, 2067.0, 2067.0, 0.9592019439826065, 544.76962667061, 0.8589728346016114], "isController": true}, {"data": ["comparison humidity (1m)", 15, 0, 0.0, 28.533333333333335, 27, 31, 29.0, 29.8, 31.0, 31.0, 1.1515430677107323, 0.55418010133579, 0.24852638473053892], "isController": false}, {"data": ["comparison particulate_matter (3h)", 15, 0, 0.0, 29.800000000000004, 28, 31, 30.0, 31.0, 31.0, 31.0, 1.1473152822395596, 17.420966708734895, 0.2644203189536485], "isController": false}, {"data": ["Click 1d", 15, 0, 0.0, 117.33333333333333, 112, 133, 115.0, 126.4, 133.0, 133.0, 1.1397310234784592, 10.913369757237293, 0.9961516269660361], "isController": true}, {"data": ["Click 3h", 15, 0, 0.0, 129.86666666666665, 118, 206, 124.0, 164.60000000000002, 206.0, 206.0, 1.1320754716981132, 69.96410672169812, 1.0115713443396226], "isController": true}, {"data": ["comparison particulate_matter (1d)", 15, 0, 0.0, 28.2, 27, 31, 28.0, 30.4, 31.0, 31.0, 1.1488970588235294, 2.678964652267157, 0.25917502010569854], "isController": false}, {"data": ["comparison humidity (3h)", 15, 0, 0.0, 30.266666666666666, 28, 34, 30.0, 33.4, 34.0, 34.0, 1.147227533460803, 17.813844407265776, 0.2531967017208413], "isController": false}, {"data": ["comparison pollen (3h)", 15, 0, 0.0, 30.533333333333335, 28, 34, 30.0, 33.4, 34.0, 34.0, 1.147227533460803, 17.495817399617593, 0.25095602294455066], "isController": false}, {"data": ["comparison pollen (1d)", 15, 0, 0.0, 28.133333333333336, 26, 30, 28.0, 29.4, 30.0, 30.0, 1.1489850631941785, 2.678047802566067, 0.24573020394484874], "isController": false}, {"data": ["Click 1m", 15, 0, 0.0, 117.33333333333334, 113, 131, 117.0, 125.0, 131.0, 131.0, 1.1426830197303268, 2.237531066694599, 0.9987317408775805], "isController": true}, {"data": ["comparison particulate_matter (1m)", 15, 0, 0.0, 28.2, 27, 29, 28.0, 29.0, 29.0, 29.0, 1.1516314779270633, 0.5631447936660269, 0.25979186660268716], "isController": false}, {"data": ["comparison humidity (1d)", 15, 0, 0.0, 28.399999999999995, 27, 31, 28.0, 30.4, 31.0, 31.0, 1.1489850631941785, 2.7218827795863656, 0.24797431539639986], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/", 15, 0, 0.0, 1693.7333333333336, 1643, 2021, 1666.0, 1840.4, 2021.0, 2021.0, 0.9620318111852232, 546.3768228498589, 0.8615070027898922], "isController": false}, {"data": ["comparison particulate_matter (1w)", 15, 0, 0.0, 28.399999999999995, 27, 30, 28.0, 30.0, 30.0, 30.0, 1.150483202945237, 0.8389689033977604, 0.25953283191440407], "isController": false}, {"data": ["comparison temperature (1m)", 15, 0, 0.0, 28.8, 27, 30, 29.0, 30.0, 30.0, 30.0, 1.1515430677107323, 0.5879916848994319, 0.2519000460617227], "isController": false}, {"data": ["Click 1w", 15, 0, 0.0, 116.93333333333332, 111, 138, 116.0, 127.2, 138.0, 138.0, 1.1409447022134327, 3.430559253061535, 0.9972124106259983], "isController": true}]}, function(index, item){
        switch(index){
            // Errors pct
            case 3:
                item = item.toFixed(2) + '%';
                break;
            // Mean
            case 4:
            // Mean
            case 7:
            // Median
            case 8:
            // Percentile 1
            case 9:
            // Percentile 2
            case 10:
            // Percentile 3
            case 11:
            // Throughput
            case 12:
            // Kbytes/s
            case 13:
            // Sent Kbytes/s
                item = item.toFixed(2);
                break;
        }
        return item;
    }, [[0, 0]], 0, summaryTableHeader);

    // Create error table
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": []}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 360, 0, "", "", "", "", "", "", "", "", "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
