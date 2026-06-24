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
  
  // 1. AÇÃO: RESERVAR ITEM (CONVIDADO)
  if (params.action === "reservar") {
    var data = sheet.getDataRange().getValues();
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == params.codigo) {
        sheet.getRange(i + 1, 7).setValue("⏳ Reservado (Falta receber)");
        sheet.getRange(i + 1, 8).setValue(params.doador);
        sheet.getRange(i + 1, 9).setValue(params.telefone);
        return ContentService.createTextOutput(JSON.stringify({"sucesso": true})).setMimeType(ContentService.MimeType.JSON);
      }
    }
  }
  
  // 2. AÇÃO: ADICIONAR NOVO ITEM (PAIS)
  if (params.action === "adicionar") {
    var novoCodigo = "ELIS-" + Math.random().toString(36).substring(2, 8).toUpperCase();
    sheet.appendRow([
      novoCodigo, 
      params.nome, 
      params.tipo, 
      params.tamanho, 
      parseInt(params.quantidade) || 1, 
      params.foto || "", 
      params.status, 
      params.doador || "", 
      params.telefone || ""
    ]);
    return ContentService.createTextOutput(JSON.stringify({"sucesso": true})).setMimeType(ContentService.MimeType.JSON);
  }
  
  return ContentService.createTextOutput(JSON.stringify({"erro": "Ação não encontrada"})).setMimeType(ContentService.MimeType.JSON);
}