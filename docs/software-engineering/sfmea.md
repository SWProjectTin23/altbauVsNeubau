# SFMEA Project – Altbau vs. Neubau

## Components - Functinalities of the System
- Arduino
- Subscription script
- Database
- UI

---

## Classification
1. Deployment 
2. Runtime Failures
3. Design/Conceptional Mistakes

<table cellspacing="0" cellpadding="8">
  <thead>
    <tr>
      <th>ID</th>
      <th>Component</th>
      <th>Failure Mode</th>
      <th>Failure Effect</th>
      <th>Cause of Failure</th>
      <th>Effectlocation</th>
    </tr>
  </thead>
  <tbody>
    <!-- Arduino -->
    <tr>
      <td>FA1</td>
      <td>Arduino</td>
      <td>Data Missing</td>
      <td>Loss of function</td>
      <td>Power/Wi-Fi loss; device offline</td>
      <td>Database, UI, Subscription script</td>
    </tr>
    <tr>
      <td>FA2</td>
      <td>Arduino</td>
      <td>Data Inaccurate</td>
      <td>Incorrect function</td>
      <td>Sensor read errors; inconsistent payload values</td>
      <td>Database, UI, Subscription script</td>
    </tr>
    <tr>
      <td>FA3</td>
      <td>Arduino</td>
      <td>Data Timeless</td>
      <td>Erroneous function</td>
      <td>Clock/NTP issues; invalid or missing timestamp</td>
      <td>Database, UI, Subscription script</td>
    </tr>
    <tr>
      <td>FA4</td>
      <td>Arduino</td>
      <td>Erroneous/Inconsistent Datapoints</td>
      <td>Loss of function</td>
      <td>Out-of-range values; wrong topic→metric mapping (e.g. ikea/01→pollen, ikea/02→particulate_matter, temperature/01→temperature)</td>
      <td>Database, UI, Subscription script</td>
    </tr>
    <tr>
      <td>FA5</td>
      <td>Arduino</td>
      <td>Data cannot be transferred</td>
      <td>Erroneous function</td>
      <td>MQTT connection/publish failure (primary/backup broker unreachable)</td>
      <td>Database, UI, Subscription script</td>
    </tr>
    <!-- Subscription Script -->
    <tr>
      <td>FA6</td>
      <td>Subscription Script</td>
      <td>Data cannot be received (from MQTT-Server)</td>
      <td>Loss of function</td>
      <td>Broker down/unreachable; invalid client configuration</td>
      <td>Database, UI</td>
    </tr>
    <tr>
      <td>FA7</td>
      <td>Subscription Script</td>
      <td>Data cannot be transferred (to the database)</td>
      <td>Erroneous function</td>
      <td>DB connection error; DB service down; credentials/port mismatch</td>
      <td>Database, UI</td>
    </tr>
    <!-- Database -->
    <tr>
      <td>FA8</td>
      <td>Database</td>
      <td>Not available (permanent)</td>
      <td>Loss of function</td>
      <td>Container/service stopped or crashed</td>
      <td>Database, UI, Subscription script</td>
    </tr>
    <tr>
      <td>FA9</td>
      <td>Database</td>
      <td>Not available (temporary)</td>
      <td>Loss of function</td>
      <td>Restart/maintenance/overload</td>
      <td>Database, UI, Subscription script</td>
    </tr>
    <tr>
      <td>FA10</td>
      <td>Database</td>
      <td>Availability views broken/missing</td>
      <td>Incorrect function</td>
      <td>Init ran once; required SQL views not (re)applied</td>
      <td>Database, UI</td>
    </tr>
    <tr>
      <td>FA11</td>
      <td>Database</td>
      <td>Reading not possible</td>
      <td>Incorrect function</td>
      <td>Query/permission issues; DB under heavy load</td>
      <td>Database, UI, Subscription script</td>
    </tr>
    <tr>
      <td>FA12</td>
      <td>Database</td>
      <td>Writing not possible</td>
      <td>Incorrect function</td>
      <td>Disk full; permission issues; DB connection limits</td>
      <td>Database, UI, Subscription script</td>
    </tr>
  </tbody>
</table>

## Risk and Criticality
1. (S)everity can be rated in a scope of 1 (No effect) - 10 (Severe System Failure)  
2. (O)ccurrence can be rated in a likelyhood of 1 (Failure unlikely) - 10 (Failure is almost inevitable)  
3. (D)etectability can be rated in a scope of detectable from 1 (certain to be detected) - 10 (Not likely to be detected)  

Risk priority number (RPN) = S * O * D, The higher the RPN, the more critical the failure mode.
// ...existing code...
<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Effect of Failure</th>
      <th>Severity</th>
      <th>Occurrence</th>
      <th>Detection</th>
      <th>RPN (S×O×D)</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>FA1</td><td>Database, UI, Subscription script</td><td>9</td><td>4</td><td>2</td><td>72</td></tr>
    <tr><td>FA2</td><td>Database, UI, Subscription script</td><td>7</td><td>5</td><td>4</td><td>140</td></tr>
    <tr><td>FA3</td><td>Database, UI, Subscription script</td><td>6</td><td>3</td><td>6</td><td>108</td></tr>
    <tr><td>FA4</td><td>Database, UI, Subscription script</td><td>8</td><td>3</td><td>3</td><td>72</td></tr>
    <tr><td>FA5</td><td>Database, UI, Subscription script</td><td>8</td><td>2</td><td>2</td><td>32</td></tr>
    <tr><td>FA6</td><td>Database, UI</td><td>9</td><td>2</td><td>2</td><td>36</td></tr>
    <tr><td>FA7</td><td>Database, UI</td><td>7</td><td>3</td><td>3</td><td>63</td></tr>
    <tr><td>FA8</td><td>Database, UI, Subscription script</td><td>10</td><td>1</td><td>1</td><td>10</td></tr>
    <tr><td>FA9</td><td>Database, UI, Subscription script</td><td>8</td><td>2</td><td>2</td><td>32</td></tr>
    <tr><td>FA10</td><td>Database, UI</td><td>6</td><td>2</td><td>5</td><td>60</td></tr>
    <tr><td>FA11</td><td>Database, UI, Subscription script</td><td>7</td><td>2</td><td>2</td><td>28</td></tr>
    <tr><td>FA12</td><td>Database, UI, Subscription script</td><td>8</td><td>2</td><td>2</td><td>32</td></tr>
  </tbody>
</table>


## Detection means
- EVIDENT: The failure is readily detected during operation.
- DORMANT: The failure can be detected when maintenance is performed.
- HIDDEN: The failure is not detected unless intentionally sought, for instance, by testing the system.

<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Component</th>
      <th>Failure Mode</th>
      <th>Detection measure</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>FA1</td><td>Arduino</td><td>Data Missing</td><td>Evident (Grafana alert “Sensor-offline”, last sample &gt; 600 s; eval 30 s)</td></tr>
    <tr><td>FA2</td><td>Arduino</td><td>Data Inaccurate</td><td>Evident (validation drop/warn logs)</td></tr>
    <tr><td>FA3</td><td>Arduino</td><td>Data Timeless</td><td>Dormant (time drift in charts; NTP client on device)</td></tr>
    <tr><td>FA4</td><td>Arduino</td><td>Erroneous/Inconsistent Datapoints</td><td>Evident (server-side ranges & integer enforcement for pollen/PM)</td></tr>
    <tr><td>FA5</td><td>Arduino</td><td>Data cannot be transferred</td><td>Evident (ingestion stops; logs)</td></tr>
    <tr><td>FA6</td><td>Subscription Script</td><td>Cannot receive from MQTT</td><td>Evident (connection errors; exporter metrics)</td></tr>
    <tr><td>FA7</td><td>Subscription Script</td><td>Cannot transfer to DB</td><td>Evident (insert/connection errors)</td></tr>
    <tr><td>FA8</td><td>Database</td><td>Not available (permanent)</td><td>Evident (service down)</td></tr>
    <tr><td>FA9</td><td>Database</td><td>Not available (temporary)</td><td>Evident (restart/overload)</td></tr>
    <tr><td>FA10</td><td>Database</td><td>Availability views broken/missing</td><td>Dormant (panel SQL errors until view re-applied)</td></tr>
    <tr><td>FA11</td><td>Database</td><td>Reading not possible</td><td>Evident (5xx, query errors)</td></tr>
    <tr><td>FA12</td><td>Database</td><td>Writing not possible</td><td>Evident (insert failures; disk full)</td></tr>
  </tbody>
</table>



## Summary
The SFMEA covers Arduino → MQTT → Subscription script → Database → UI. Failure modes, detection and corrective actions are aligned with the project’s implementation (topics, validation ranges, availability views, alerting and monitoring).