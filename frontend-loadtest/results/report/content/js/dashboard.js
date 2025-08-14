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
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 360, 0, 0.0, 172.01111111111126, 0, 2172, 30.0, 34.900000000000034, 1762.0, 1817.73, 22.179779434415625, 1088.3837496534409, 4.904171608342061], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["comparison temperature (1d)", 15, 0, 0.0, 30.333333333333332, 29, 35, 30.0, 33.2, 35.0, 35.0, 1.154912226670773, 3.0581865231367416, 0.2526370495842316], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-1", 15, 0, 0.0, 0.5333333333333333, 0, 1, 1.0, 1.0, 1.0, 1.0, 1.081626766657052, 16.530721580256706, 0.15316004020046148], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-2", 15, 0, 0.0, 1765.2, 1725, 1949, 1755.0, 1849.4, 1949.0, 1949.0, 0.9601228957306535, 1.0088791365294758, 0.15189444248863856], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-0", 15, 0, 0.0, 2.3333333333333335, 0, 24, 1.0, 10.200000000000008, 24.0, 24.0, 1.0766580534022396, 1.1597205399440138, 0.13668510443583118], "isController": false}, {"data": ["comparison temperature (1w)", 15, 0, 0.0, 30.799999999999997, 29, 33, 31.0, 32.4, 33.0, 33.0, 1.1570502931194075, 3.063848084117556, 0.2531047516198704], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-5", 15, 0, 0.0, 0.39999999999999997, 0, 1, 0.0, 1.0, 1.0, 1.0, 1.1057869517139698, 6.251367835422042, 0.17061947106524145], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-3", 15, 0, 0.0, 33.199999999999996, 31, 45, 32.0, 39.0, 45.0, 45.0, 1.1029411764705883, 1.2365004595588236, 0.17879710477941177], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/-4", 15, 0, 0.0, 2.266666666666667, 1, 3, 2.0, 3.0, 3.0, 3.0, 1.1057869517139698, 601.266255644121, 0.16845973092517508], "isController": false}, {"data": ["comparison temperature (3h)", 15, 0, 0.0, 30.6, 29, 32, 31.0, 32.0, 32.0, 32.0, 1.1526048870447212, 3.0520767298678346, 0.2577602725910558], "isController": false}, {"data": ["comparison pollen (1m)", 15, 0, 0.0, 30.26666666666667, 29, 32, 30.0, 32.0, 32.0, 32.0, 1.1590171534538711, 3.006804396538402, 0.24787573887343534], "isController": false}, {"data": ["SET metrics", 15, 0, 0.0, 22.200000000000006, 0, 324, 1.0, 130.80000000000013, 324.0, 324.0, 1.1198208286674132, 0.0, 0.0], "isController": false}, {"data": ["comparison pollen (1w)", 15, 0, 0.0, 30.400000000000002, 29, 33, 30.0, 32.4, 33.0, 33.0, 1.1572288227125442, 3.0021649822558247, 0.24749327360746798], "isController": false}, {"data": ["comparison humidity (1w)", 15, 0, 0.0, 30.133333333333333, 29, 33, 30.0, 31.8, 33.0, 33.0, 1.1570502931194075, 3.0053929391005862, 0.24971495583924713], "isController": false}, {"data": ["Initial Page TTLB", 15, 0, 0.0, 1820.7999999999997, 1762, 2234, 1796.0, 1987.4, 2234.0, 2234.0, 0.9494271789353756, 539.2088082117539, 0.8502194561364643], "isController": true}, {"data": ["comparison humidity (1m)", 15, 0, 0.0, 30.799999999999997, 29, 33, 31.0, 32.4, 33.0, 33.0, 1.1588380716934485, 3.0100366241115575, 0.2501007947697775], "isController": false}, {"data": ["comparison particulate_matter (3h)", 15, 0, 0.0, 30.133333333333333, 29, 31, 30.0, 31.0, 31.0, 31.0, 1.1533138551437798, 3.0227184808934338, 0.26580280255266797], "isController": false}, {"data": ["Click 1d", 15, 0, 0.0, 126.73333333333333, 121, 147, 124.0, 146.4, 147.0, 147.0, 1.1452130096197892, 11.979628927126278, 1.0009430113376088], "isController": true}, {"data": ["Click 3h", 15, 0, 0.0, 130.66666666666666, 122, 219, 125.0, 163.80000000000004, 219.0, 219.0, 1.1368804001819008, 11.892464733022585, 1.0158648107094133], "isController": true}, {"data": ["comparison particulate_matter (1d)", 15, 0, 0.0, 30.73333333333333, 29, 32, 31.0, 32.0, 32.0, 32.0, 1.1553570053146422, 3.028073369983825, 0.26063229319109604], "isController": false}, {"data": ["comparison humidity (3h)", 15, 0, 0.0, 30.133333333333336, 28, 33, 30.0, 32.4, 33.0, 33.0, 1.1530478899223615, 2.9949968531401336, 0.25448127258052117], "isController": false}, {"data": ["comparison pollen (3h)", 15, 0, 0.0, 30.266666666666662, 29, 32, 30.0, 31.4, 32.0, 32.0, 1.1532251864380718, 2.9917784654416852, 0.25226800953332823], "isController": false}, {"data": ["comparison pollen (1d)", 15, 0, 0.0, 30.2, 28, 33, 30.0, 32.4, 33.0, 33.0, 1.1552680221811462, 2.9970781346272335, 0.2470739227125693], "isController": false}, {"data": ["Click 1m", 15, 0, 0.0, 126.8, 121, 142, 124.0, 141.4, 142.0, 142.0, 1.1492491572172847, 12.021849501034325, 1.0044706989350292], "isController": true}, {"data": ["comparison particulate_matter (1m)", 15, 0, 0.0, 30.26666666666667, 29, 33, 30.0, 31.8, 33.0, 33.0, 1.1591067150915695, 3.037900978479252, 0.2614781749864771], "isController": false}, {"data": ["comparison humidity (1d)", 15, 0, 0.0, 30.266666666666662, 29, 32, 30.0, 32.0, 32.0, 32.0, 1.155001155001155, 3.0000703828828827, 0.24927271021021022], "isController": false}, {"data": ["GET http://altbau_vs_neubau_frontend/", 15, 0, 0.0, 1816.0666666666664, 1762, 2172, 1795.0, 1962.0, 2172.0, 2172.0, 0.9532282663955262, 541.3675623371569, 0.8536233596530248], "isController": false}, {"data": ["comparison particulate_matter (1w)", 15, 0, 0.0, 30.400000000000002, 29, 35, 30.0, 32.6, 35.0, 35.0, 1.1573181081706658, 3.033213221394954, 0.26107469041740605], "isController": false}, {"data": ["comparison temperature (1m)", 15, 0, 0.0, 30.333333333333336, 29, 35, 30.0, 32.6, 35.0, 35.0, 1.1587485515643106, 3.068345041521823, 0.2534762456546929], "isController": false}, {"data": ["Click 1w", 15, 0, 0.0, 126.8, 121, 147, 124.0, 146.4, 147.0, 147.0, 1.1470520761642578, 11.998866688651832, 1.0025503986005964], "isController": true}]}, function(index, item){
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
