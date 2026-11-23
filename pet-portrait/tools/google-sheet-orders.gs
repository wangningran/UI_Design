/**
 * Saves website commission requests into this Google Sheet.
 * Paste into Extensions → Apps Script, then Deploy → New deployment → Web app
 * (Execute as: Me, Who has access: Anyone). Put the web app URL in ORDER_CONFIG.sheetUrl.
 */
const SHEET_NAME = 'Orders';
const NOTIFY_BY_EMAIL = true;   // email you whenever a new request arrives
const HEADERS = ['Submitted', 'Name', 'WhatsApp / phone', 'Email', 'Pet name', 'Size', 'Frame', 'Notes', 'Status', 'Follow-up notes'];

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.setFrozenRows(1);
      sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    }
    const p = e.parameter || {};
    const row = [new Date(), p.name, p.phone, p.email, p.pet, p.size, p.frame, p.msg, 'New', ''].map(clean);
    sheet.appendRow(row);

    if (NOTIFY_BY_EMAIL) {
      MailApp.sendEmail(Session.getEffectiveUser().getEmail(),
        'New portrait request: ' + (p.name || 'someone'),
        HEADERS.slice(0, 8).map((h, i) => h + ': ' + (row[i] || '-')).join('\n') +
        '\n\nThey should also be messaging you on WhatsApp.\n' + ss.getUrl());
    }
    return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

/** Keep text short and stop it from being read as a spreadsheet formula. */
function clean(v) {
  if (v instanceof Date) return v;
  v = String(v == null ? '' : v).slice(0, 1000);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}
