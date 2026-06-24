function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  var jsonArray = [];
  
  for (var i = 1; i < data.length; i++) {
    var obj = {};
    for (var j = 0; j < headers.length; j++) {
      obj[headers[j]] = data[i][j];
    }
    jsonArray.push(obj);
  }
  
  return ContentService.createTextOutput(JSON.stringify(jsonArray))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var params = JSON.parse(e.postData.contents);
  
  if (params.action === "reservar") {
    var data = sheet.getDataRange().getValues();
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == params.codigo) { // Coluna A (Código)
        sheet.getRange(i + 1, 7).setValue("⏳ Reservado (Falta receber)"); // Coluna G
        sheet.getRange(i + 1, 8).setValue(params.doador);               // Coluna H
        sheet.getRange(i + 1, 9).setValue(params.telefone);              // Coluna I
        return ContentService.createTextOutput(JSON.stringify({"sucesso": true})).setMimeType(ContentService.MimeType.JSON);
      }
    }
  }
  return ContentService.createTextOutput(JSON.stringify({"erro": "Item não encontrado"})).setMimeType(ContentService.MimeType.JSON);
}