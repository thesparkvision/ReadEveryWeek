const CONFIG = {
  DOC_ID: 'DOC_ID_HERE',
  SPREADSHEET_ID: 'SPREADSHEET_ID_HERE',
  SHEET_NAME: 'blogs to read'
};

function syncDocLinks() {
  syncDocLinksWithTitles(CONFIG);
}

function syncDocLinksWithTitles({ DOC_ID, SPREADSHEET_ID, SHEET_NAME }) {
  const doc = DocumentApp.openById(DOC_ID);
  const paragraphs = doc.getBody().getParagraphs();

  const sheet = SpreadsheetApp
    .openById(SPREADSHEET_ID)
    .getSheetByName(SHEET_NAME);

  if (!sheet) {
    throw new Error(`Sheet "${SHEET_NAME}" not found`);
  }

  const rows = [];

  paragraphs.forEach(p => {
    const text = p.getText();
    const urls = extractUrls(text);
    if (!urls.length) return;

    urls.forEach(url => {
      rows.push([extractTitle(text, url), url]);
    });
  });

  if (rows.length) {
    sheet
      .getRange(sheet.getLastRow() + 1, 1, rows.length, 2)
      .setValues(rows);
  }
}

function extractUrls(text) {
  return text.match(/https?:\/\/[^\s]+/g) || [];
}

function extractTitle(text, url) {
  const title = text.replace(url, '').trim();
  if (title) return title;

  try {
    return new URL(url).hostname.replace('www.', '');
  } catch {
    return 'Untitled';
  }
}
