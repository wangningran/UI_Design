# Receiving commission requests (Google Sheet + WhatsApp)

When a customer presses **Continue on WhatsApp**:
1. Their request (including their WhatsApp / phone number, which is required) is saved as a new row in your Google Sheet (and you get an email).
2. WhatsApp opens with the request already written. They press send and add photos of their pet in the chat.

## 1. Create the sheet (about 5 minutes)
1. Go to sheets.google.com and create a blank sheet, e.g. "STRATA orders".
2. Menu **Extensions → Apps Script**.
3. Delete everything in the editor and paste the contents of `tools/google-sheet-orders.gs`. Click **Save** (disk icon).
4. Click **Deploy → New deployment**. Click the gear next to "Select type" and choose **Web app**.
   - Description: `orders`
   - Execute as: **Me**
   - Who has access: **Anyone**
5. Click **Deploy**, then **Authorize access**, choose your Google account.
   Google warns the app is unverified because you wrote it yourself: click **Advanced → Go to (project name) → Allow**.
6. Copy the **Web app URL** (it ends in `/exec`).

## 2. Connect the website
In `index.html`, find `ORDER_CONFIG` and fill in:
```js
const ORDER_CONFIG={
  whatsapp:'16047295833',  // your number: country code + number, digits only
  sheetUrl:'https://script.google.com/macros/s/.../exec'
};
```

## 3. Test
Submit the form once yourself. Check that a row appears in the **Orders** tab, the email arrives, and WhatsApp opens with the message.

## Using the sheet
- **Status** starts as `New`. Change it as you go (e.g. Contacted, Sketch sent, Paid, Shipped). Data → Data validation can turn it into a dropdown.
- **Follow-up notes** is free for your own notes.
- If you edit the script later, use **Deploy → Manage deployments → Edit → New version** so the URL stays the same.
