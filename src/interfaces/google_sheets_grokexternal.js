function getEtradePositions() {
  const { key: ck, secret: cs } = decryptCredentials();

  const baseUrl = 'https://api.etrade.com';
  const accountsResp = signedFetch(baseUrl + '/v1/accounts/list.json', 'GET', ck, cs);
  const accountsData = JSON.parse(accountsResp.getContentText());

  let accountList = accountsData?.AccountListResponse?.Accounts?.Account || [];
  if (!Array.isArray(accountList)) accountList = [accountList];

  const activeAccounts = accountList.filter(acc => acc.accountStatus === 'ACTIVE');
  if (activeAccounts.length === 0) {
    Browser.msgBox('No active accounts found.');
    return;
  }

  // Collect positions
  const allPositions = {};
  activeAccounts.forEach(acc => {
    const accountId = acc.accountIdKey;

    const portfolioResp = signedFetch(baseUrl + '/v1/accounts/' + accountId + '/portfolio.json?view=QUICK', 'GET', ck, cs);
    if (portfolioResp.getResponseCode() !== 200) return;

    const data = JSON.parse(portfolioResp.getContentText());
    const positions = data?.PortfolioResponse?.AccountPortfolio?.[0]?.Position || [];

    positions.forEach(p => {
      const symbol = p.symbolDescription || p.symbol || 'N/A';
      if (!allPositions[symbol]) allPositions[symbol] = { symbol };

      allPositions[symbol][accountId + '_qty'] = p.quantity || 0;
      allPositions[symbol][accountId + '_value'] = p.marketValue || 0;
    });
  });

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Holdings') ||
                SpreadsheetApp.getActiveSpreadsheet().insertSheet('Holdings');
  sheet.clear();

  // Headers
  const headers = ['Symbol'];
  activeAccounts.forEach(acc => {
    const desc = acc.accountDesc || acc.accountType || acc.accountIdKey;
    headers.push(`${desc} Qty`);
    headers.push(`${desc} Value`);
  });
  headers.push('Total Qty');
  headers.push('Total Value');
  headers.push('Time');

  sheet.appendRow(headers);

  const now = new Date();
  Object.values(allPositions).forEach(pos => {
    const row = new Array(headers.length).fill(0);
    row[0] = pos.symbol;
    row[row.length - 1] = now;

    let totalQty = 0;
    let totalValue = 0;

    activeAccounts.forEach(acc => {
      const qtyCol = headers.indexOf(`${acc.accountDesc || acc.accountType || acc.accountIdKey} Qty`);
      const valCol = qtyCol + 1;

      const qty = pos[acc.accountIdKey + '_qty'] || 0;
      const value = pos[acc.accountIdKey + '_value'] || 0;

      row[qtyCol] = qty;
      row[valCol] = value;

      totalQty += Number(qty);
      totalValue += Number(value);
    });

    row[row.length - 3] = totalQty;
    row[row.length - 2] = totalValue;

    sheet.appendRow(row);
  });

  // Add formula-based total row
  const lastDataRow = sheet.getLastRow();
  const totalRowNum = lastDataRow + 1;
  const totalRow = new Array(headers.length).fill('');
  totalRow[0] = 'TOTAL';

  // Per-account totals (Qty and Value columns)
  activeAccounts.forEach(acc => {
    const desc = acc.accountDesc || acc.accountType || acc.accountIdKey;
    const qtyColLetter = SpreadsheetApp.getActiveSheet().getRange(1, headers.indexOf(`${desc} Qty`) + 1).getA1Notation().replace(/\d+/, '');
    const valColLetter = SpreadsheetApp.getActiveSheet().getRange(1, headers.indexOf(`${desc} Value`) + 1).getA1Notation().replace(/\d+/, '');

    const qtyFormula = `=SUM(${qtyColLetter}2:${qtyColLetter}${lastDataRow})`;
    const valFormula = `=SUM(${valColLetter}2:${valColLetter}${lastDataRow})`;

    sheet.getRange(totalRowNum, headers.indexOf(`${desc} Qty`) + 1).setFormula(qtyFormula);
    sheet.getRange(totalRowNum, headers.indexOf(`${desc} Value`) + 1).setFormula(valFormula);
  });

  // Grand totals
  const totalQtyColLetter = SpreadsheetApp.getActiveSheet().getRange(1, headers.length - 2).getA1Notation().replace(/\d+/, '');
  const totalValueColLetter = SpreadsheetApp.getActiveSheet().getRange(1, headers.length - 1).getA1Notation().replace(/\d+/, '');

  sheet.getRange(totalRowNum, headers.length - 2).setFormula(`=SUM(${totalQtyColLetter}2:${totalQtyColLetter}${lastDataRow})`);
  sheet.getRange(totalRowNum, headers.length - 1).setFormula(`=SUM(${totalValueColLetter}2:${totalValueColLetter}${lastDataRow})`);

  sheet.getRange(totalRowNum, headers.length).setValue(now);

  // Formatting
  sheet.autoResizeColumns(1, headers.length);
  sheet.getRange(totalRowNum, 1, 1, headers.length).setFontWeight('bold').setBackground('#d9e1f2');

  // Quantity columns as numbers
  const qtyCols = [];
  for (let col = 2; col < headers.length - 2; col += 2) qtyCols.push(col);
  qtyCols.push(headers.length - 2);
  qtyCols.forEach(col => sheet.getRange(2, col, totalRowNum, 1).setNumberFormat('0'));

  // Value columns as currency
  const valueCols = [];
  for (let col = 3; col < headers.length - 2; col += 2) valueCols.push(col);
  valueCols.push(headers.length - 1);
  valueCols.forEach(col => sheet.getRange(2, col, totalRowNum, 1).setNumberFormat('$#,##0.00'));

  // Date column
  sheet.getRange(2, headers.length, totalRowNum, 1).setNumberFormat('yyyy-mm-dd hh:mm');

  Browser.msgBox('Success! Holdings tab with formula-based total row (per-account and grand totals).');
}