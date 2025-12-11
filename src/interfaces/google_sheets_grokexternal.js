// E*TRADE → Google Sheets – FULLY WORKING (Dec 2025) – With In-Script Encryption Update

// Encryption/Decryption Helpers
function deriveKey(password) {
  const digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, password);
  return digest.map(byte => (byte < 0 ? byte + 256 : byte));
}

function encryptString(text, password) {
  const keyBytes = deriveKey(password);
  const textBytes = Utilities.newBlob(text).getBytes();
  const encryptedBytes = textBytes.map((byte, i) => byte ^ keyBytes[i % keyBytes.length]);
  return Utilities.base64Encode(encryptedBytes);
}

function decryptString(encryptedText, password) {
  const keyBytes = deriveKey(password);
  const encryptedBytes = Utilities.base64Decode(encryptedText);
  const decryptedBytes = encryptedBytes.map((byte, i) => byte ^ keyBytes[i % keyBytes.length]);
  return Utilities.newBlob(decryptedBytes).getDataAsString();  // Safe method
}

// Update Phase: Run this to encrypt and store new key/secret
function updateEncryptedCredentials() {
  const ui = SpreadsheetApp.getUi();
  const password = ui.prompt('Enter decryption password:').getResponseText().trim();
  if (!password) throw new Error('Password required');

  const key = ui.prompt('Enter actual E*TRADE consumer key:').getResponseText().trim();
  if (!key) throw new Error('Key required');

  const secret = ui.prompt('Enter actual E*TRADE consumer secret:').getResponseText().trim();
  if (!secret) throw new Error('Secret required');

  const encryptedKey = encryptString(key, password);
  const encryptedSecret = encryptString(secret, password);

  PropertiesService.getScriptProperties()
    .setProperty('ENCRYPTED_KEY', encryptedKey)
    .setProperty('ENCRYPTED_SECRET', encryptedSecret);

  ui.alert('Success! Encrypted values stored in script properties.');
}

// Runtime Decryption
function decryptCredentials() {
  const ui = SpreadsheetApp.getUi();
  const password = ui.prompt('Enter decryption password:').getResponseText().trim();
  if (!password) throw new Error('Password required');

  const encryptedKey = PropertiesService.getScriptProperties().getProperty('ENCRYPTED_KEY');
  const encryptedSecret = PropertiesService.getScriptProperties().getProperty('ENCRYPTED_SECRET');

  if (!encryptedKey || !encryptedSecret) throw new Error('Encrypted values not found — run updateEncryptedCredentials()');

  const key = decryptString(encryptedKey, password);
  const secret = decryptString(encryptedSecret, password);

  return { key, secret };
}

// E*TRADE Flow
function getRequestToken() {
  const { key: ck, secret: cs } = decryptCredentials();

  const baseUrl = 'https://api.etrade.com';  // PRODUCTION
  const requestUrl = baseUrl + '/oauth/request_token';

  const params = {
    oauth_callback: 'oob',
    oauth_consumer_key: ck,
    oauth_nonce: Utilities.getUuid().replace(/-/g, '').substring(0,32),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now()/1000).toString(),
    oauth_version: '1.0'
  };

  params.oauth_signature = getOAuthSignature('POST', requestUrl, params, cs, '');

  const authHeader = 'OAuth ' + Object.keys(params)
    .map(k => `${k}="${encodeURIComponent(params[k])}"`)
    .join(', ');

  const resp = UrlFetchApp.fetch(requestUrl, {
    method: 'post',
    headers: { Authorization: authHeader },
    muteHttpExceptions: true
  });

  Logger.log('Response: ' + resp.getResponseCode() + ' – ' + resp.getContentText());

  if (resp.getResponseCode() !== 200) throw new Error('Request token failed: ' + resp.getContentText());

  const result = resp.getContentText().split('&').reduce((o,p)=>{let [k,v]=p.split('='); o[k]=decodeURIComponent(v); return o}, {});

  PropertiesService.getUserProperties()
    .setProperties({REQ_TOKEN: result.oauth_token, REQ_SECRET: result.oauth_token_secret});

  const authUrl = `https://us.etrade.com/e/t/etws/authorize?key=${ck}&token=${result.oauth_token}`;

  SpreadsheetApp.getUi().alert(
    'Copy this full URL and paste it into a new browser tab:\n\n' +
    authUrl + 
    '\n\nLog in → click Allow → copy the 6-character verifier code → run "2. Exchange Token (paste verifier code)"'
  );

  Logger.log('Auth URL: ' + authUrl);
}

function exchangeToken() {
  const verifier = Browser.inputBox('Paste the 6-character verifier code (e.g., ZRFK1):').trim();
  if (!verifier || verifier.length < 5 || verifier.length > 20) {
    throw new Error('Verifier code looks wrong — it should be around 6 characters. Try copying again.');
  }

  const { key: ck, secret: cs } = decryptCredentials();
  const token = PropertiesService.getUserProperties().getProperty('REQ_TOKEN');
  const tokenSecret = PropertiesService.getUserProperties().getProperty('REQ_SECRET');

  const baseUrl = 'https://api.etrade.com';
  const url = baseUrl + '/oauth/access_token';

  const params = {
    oauth_consumer_key: ck,
    oauth_nonce: Utilities.getUuid().replace(/-/g, '').substring(0,32),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now()/1000).toString(),
    oauth_token: token,
    oauth_verifier: verifier,
    oauth_version: '1.0'
  };

  params.oauth_signature = getOAuthSignature('POST', url, params, cs, tokenSecret);

  const authHeader = 'OAuth ' + Object.keys(params)
    .map(k => `${k}="${encodeURIComponent(params[k])}"`)
    .join(', ');

  const resp = UrlFetchApp.fetch(url, {
    method: 'post',
    headers: { Authorization: authHeader },
    muteHttpExceptions: true
  });

  Logger.log('Exchange response: ' + resp.getResponseCode() + ' – ' + resp.getContentText());

  if (resp.getResponseCode() !== 200) throw new Error('Access token failed: ' + resp.getContentText());

  const result = resp.getContentText().split('&').reduce((o,p)=>{let [k,v]=p.split('='); o[k]=decodeURIComponent(v); return o}, {});

  PropertiesService.getUserProperties()
    .setProperties({ACCESS_TOKEN: result.oauth_token, ACCESS_SECRET: result.oauth_token_secret});

  Browser.msgBox('SUCCESS! Access token saved. Run "3. Fetch Positions".');
}

function getEtradePositions() {
  const { key: ck, secret: cs } = decryptCredentials();

  const baseUrl = 'https://api.etrade.com';
  const accountsResp = signedFetch(baseUrl + '/v1/accounts/list.json', 'GET', ck, cs);
  Logger.log('Accounts response: ' + accountsResp.getContentText());

  const accountsData = JSON.parse(accountsResp.getContentText());

  let accountList = accountsData?.AccountListResponse?.Accounts?.Account || [];

  if (!Array.isArray(accountList)) accountList = [accountList];

  if (accountList.length === 0) {
    Browser.msgBox('No accounts found. Check key activation with E*TRADE support.');
    return;
  }

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Holdings') ||
                SpreadsheetApp.getActiveSpreadsheet().insertSheet('Holdings');
  sheet.clear().appendRow(['Account ID','Symbol','Quantity','Price','Market Value','Time']);

  let totalPositions = 0;

  accountList.forEach(account => {
    if (account.accountStatus !== 'ACTIVE') {
      Logger.log('Skipping closed account: ' + account.accountIdKey);
      return;
    }

    const accountId = account.accountIdKey;
    Logger.log('Fetching positions for account: ' + accountId);

    const portfolioResp = signedFetch(baseUrl + '/v1/accounts/' + accountId + '/portfolio.json?view=QUICK', 'GET', ck, cs);
    const portfolioCode = portfolioResp.getResponseCode();
    Logger.log('Portfolio response code for ' + accountId + ': ' + portfolioCode);
    Logger.log('Portfolio response body for ' + accountId + ': ' + portfolioResp.getContentText());

    if (portfolioCode !== 200) {
      Logger.log('Skipping account ' + accountId + ' due to error: ' + portfolioResp.getContentText());
      return;
    }

    const data = JSON.parse(portfolioResp.getContentText());

    const positions = data?.PortfolioResponse?.AccountPortfolio?.[0]?.Position || [];
    positions.forEach(p => {
      sheet.appendRow([
        accountId,
        p.symbolDescription || p.symbol || 'N/A',
        p.quantity || 0,
        p.currentPrice || p.pricePaid || 0,
        p.marketValue || 0,
        new Date()
      ]);
      totalPositions++;
    });
  });

  Browser.msgBox(`Success! Loaded ${totalPositions} positions across ${accountList.length} accounts. Check Holdings tab.`);
}

// ────── Helper Functions ──────
function getOAuthSignature(method, url, params, consumerSecret, tokenSecret = '') {
  const sorted = Object.keys(params).sort().map(k => 
    encodeURIComponent(k) + '=' + encodeURIComponent(params[k])
  ).join('&');
  const baseString = method + '&' + encodeURIComponent(url) + '&' + encodeURIComponent(sorted);
  const key = encodeURIComponent(consumerSecret) + '&' + encodeURIComponent(tokenSecret);
  const signature = Utilities.computeHmacSignature(Utilities.MacAlgorithm.HMAC_SHA_1, baseString, key);
  return Utilities.base64Encode(signature);
}

function signedFetch(fullUrl, method, ck, cs) {
  const token = PropertiesService.getUserProperties().getProperty('ACCESS_TOKEN');
  const tokenSecret = PropertiesService.getUserProperties().getProperty('ACCESS_SECRET');

  // Split URL into base and query string
  const urlParts = fullUrl.split('?');
  const base = urlParts[0];
  const queryString = urlParts[1] || '';

  // Parse query params
  const queryParams = {};
  queryString.split('&').forEach(pair => {
    if (pair) {
      const [k, v] = pair.split('=');
      queryParams[decodeURIComponent(k)] = decodeURIComponent(v || '');
    }
  });

  const oauthParams = {
    oauth_consumer_key: ck,
    oauth_nonce: Utilities.getUuid().replace(/-/g, '').substring(0,32),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now()/1000).toString(),
    oauth_token: token,
    oauth_version: '1.0'
  };

  // Merge OAuth and query params for signature
  const allParams = { ...oauthParams, ...queryParams };

  // Sort and normalize for base string
  const sorted = Object.keys(allParams).sort().map(k => 
    encodeURIComponent(k) + '=' + encodeURIComponent(allParams[k])
  ).join('&');

  const baseString = method + '&' + encodeURIComponent(base) + '&' + encodeURIComponent(sorted);
  const key = encodeURIComponent(cs) + '&' + encodeURIComponent(tokenSecret);
  const signature = Utilities.base64Encode(Utilities.computeHmacSignature(Utilities.MacAlgorithm.HMAC_SHA_1, baseString, key));

  oauthParams.oauth_signature = signature;

  const authHeader = 'OAuth ' + Object.keys(oauthParams)
    .map(k => `${k}="${encodeURIComponent(oauthParams[k])}"`)
    .join(', ');

  return UrlFetchApp.fetch(fullUrl, {
    method: method.toLowerCase(),
    headers: { Authorization: authHeader },
    muteHttpExceptions: true
  });
}
function onOpen() {
  SpreadsheetApp.getUi().createMenu('E*TRADE')
    .addItem('Update Encrypted Credentials', 'updateEncryptedCredentials')
    .addItem('1. Get Request Token', 'getRequestToken')
    .addItem('2. Exchange Token', 'exchangeToken')
    .addItem('3. Fetch Positions', 'getEtradePositions')
    .addToUi();
}