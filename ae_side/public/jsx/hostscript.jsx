function importExrFile(filePath) {
    try {
        var importOptions = new ImportOptions();

        importOptions.file = new File(filePath);

        if (importOptions.file.exists) {
            var importedItem = app.project.importFile(importOptions);

            importedItem.selected = true;

            return "Success: Imported " + filePath;
        } else {
            return "Error: File does not exist at " + filePath;
        }
    } catch (err) {
        return "Error: " + err.toString();
    }
}