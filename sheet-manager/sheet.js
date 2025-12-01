
const SHEET_NAME = 'Sheet1';  // change if needed
const API_URL    = 'http://94.130.143.251:9710/subnets'; // <-- your endpoint

// Map "logical" field names to header text in row 1
const HEADER_NAMES = {
  netuid: 'Netuid',
  name: 'Name',
  network_reg_time: 'Due Date',
  top_miner_reg_time: 'Top Due Date',
  first_miner_reg_time: 'First Due Date',
  owner_incentive: 'Burn Rate',
  github: 'Github',
  subnet_url: 'Subnet Url',
  price: 'Price',
  tao_in: 'TAO IN',
  
  // note/status are present in the sheet, but we don't touch them
  note: 'Notes',
  status: 'Status'
};

// ========== DATA FETCHER ==========
// API should return something like:
// [
//   { netuid: 1, name: 'Apex', reg_time: '2023-10-15 17:52:24',
//     owner_incentive: 1, github: '...', subnet_url: '...',
//     price: 0.009408748, tao_in: 23126.30060798 },
//   ...
// ]
function fetchSubnetObjects() {
  const resp = UrlFetchApp.fetch(API_URL, { muteHttpExceptions: true });
  if (resp.getResponseCode() !== 200) {
    throw new Error('Bad response from API: ' + resp.getResponseCode() +
                    ' body=' + resp.getContentText());
  }
  const data = JSON.parse(resp.getContentText());
  if (!Array.isArray(data)) {
    throw new Error('API did not return an array');
  }
  return data;
}

// ========== MAIN UPDATE FUNCTION ==========
function updateSubnetsSheet() {
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);

  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow < 1) {
    throw new Error('Sheet has no header row yet');
  }

  // --- 1. Build a map from header name -> column index ---
  const headerRow = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  const colIndex = {}; // e.g. colIndex.netuid = 1
  Object.keys(HEADER_NAMES).forEach(key => {
    const headerText = HEADER_NAMES[key];
    const idx = headerRow.indexOf(headerText);
    if (idx !== -1) {
      colIndex[key] = idx + 1; // 1-based index
    }
  });

  if (!colIndex.netuid) {
    throw new Error('Could not find "Netuid" column in header row');
  }

  // --- 2. Fetch latest subnet data and index by netuid ---
  const subnets = fetchSubnetObjects();
  const subnetByNetuid = {};
  subnets.forEach(s => {
    if (s.netuid !== undefined && s.netuid !== null) {
      subnetByNetuid[String(s.netuid)] = s;
    }
  });

  // --- 3. Read all existing netuids from sheet ---
  const netuidRange = sheet.getRange(2, colIndex.netuid, Math.max(lastRow - 1, 0), 1);
  const netuidValues = lastRow >= 2 ? netuidRange.getValues() : [];
  const existingNetuids = new Set();
  const rowNetuidMap = {}; // maps netuid string -> row number

  for (let i = 0; i < netuidValues.length; i++) {
    const rowNum = i + 2; // actual sheet row
    const v = netuidValues[i][0];
    if (v === '' || v === null) continue;
    const key = String(v);
    existingNetuids.add(key);
    rowNetuidMap[key] = rowNum;
  }

  // --- 4. Update rows where netuid matches ---
  Object.keys(rowNetuidMap).forEach(netuidStr => {
    const subnet = subnetByNetuid[netuidStr];
    if (!subnet) return; // nothing to update for this row

    const row = rowNetuidMap[netuidStr];

    // Only set columns that exist & that we want to overwrite
    if (colIndex.name)             sheet.getRange(row, colIndex.name).setValue(subnet.name);
    if (colIndex.network_reg_time)         sheet.getRange(row, colIndex.network_reg_time).setValue(subnet.network_reg_time);
    if (colIndex.owner_incentive)  sheet.getRange(row, colIndex.owner_incentive).setValue(subnet.owner_incentive);
    if (colIndex.github)           sheet.getRange(row, colIndex.github).setValue(subnet.github);
    if (colIndex.subnet_url)       sheet.getRange(row, colIndex.subnet_url).setValue(subnet.subnet_url);
    if (colIndex.price)            sheet.getRange(row, colIndex.price).setValue(subnet.price);
    if (colIndex.tao_in)           sheet.getRange(row, colIndex.tao_in).setValue(subnet.tao_in);
    if (colIndex.top_miner_reg_time)         sheet.getRange(row, colIndex.top_miner_reg_time).setValue(subnet.top_miner_reg_time);
    if (colIndex.first_miner_reg_time)         sheet.getRange(row, colIndex.first_miner_reg_time).setValue(subnet.first_miner_reg_time);

    // We deliberately DO NOT touch note/status columns,
    // so whatever you type there stays.
  });

  // --- 5. Append any new netuids that are not yet in the sheet ---
  const rowsToAppend = [];
  subnets.forEach(subnet => {
    const key = String(subnet.netuid);
    if (existingNetuids.has(key)) return; // already handled above

    const rowArr = new Array(lastCol).fill('');

    if (colIndex.netuid)           rowArr[colIndex.netuid - 1] = subnet.netuid;
    if (colIndex.name)             rowArr[colIndex.name - 1] = subnet.name;
    if (colIndex.network_reg_time)         rowArr[colIndex.network_reg_time - 1] = subnet.network_reg_time;
    if (colIndex.owner_incentive)  rowArr[colIndex.owner_incentive - 1] = subnet.owner_incentive;
    if (colIndex.github)           rowArr[colIndex.github - 1] = subnet.github;
    if (colIndex.subnet_url)       rowArr[colIndex.subnet_url - 1] = subnet.subnet_url;
    if (colIndex.price)            rowArr[colIndex.price - 1] = subnet.price;
    if (colIndex.tao_in)           rowArr[colIndex.tao_in - 1] = subnet.tao_in;
    if (colIndex.top_miner_reg_time)         rowArr[colIndex.top_miner_reg_time - 1] = subnet.top_miner_reg_time;
    if (colIndex.first_miner_reg_time)         rowArr[colIndex.first_miner_reg_time - 1] = subnet.first_miner_reg_time;
    // note/status left as '' so you can fill them in later

    rowsToAppend.push(rowArr);
  });

  if (rowsToAppend.length > 0) {
    const startRow = sheet.getLastRow() + 1;
    sheet.getRange(startRow, 1, rowsToAppend.length, lastCol).setValues(rowsToAppend);
  }

  // Optional timestamp somewhere (e.g. first row in a spare column)
  sheet.getRange(1, lastCol).setValue('Last update: ' + new Date());
}
