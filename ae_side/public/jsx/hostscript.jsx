if (typeof JSON !== "object") { JSON = {} } (function () { "use strict"; var rx_one = /^[\],:{}\s]*$/, rx_two = /\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g, rx_three = /"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g, rx_four = /(?:^|:|,)(?:\s*\[)+/g, rx_escapable = /[\\\"\u0000-\u001f\u007f-\u009f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g, rx_dangerous = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g; function f(n) { return n < 10 ? "0" + n : n } function this_value() { return this.valueOf() } if (typeof Date.prototype.toJSON !== "function") { Date.prototype.toJSON = function () { return isFinite(this.valueOf()) ? this.getUTCFullYear() + "-" + f(this.getUTCMonth() + 1) + "-" + f(this.getUTCDate()) + "T" + f(this.getUTCHours()) + ":" + f(this.getUTCMinutes()) + ":" + f(this.getUTCSeconds()) + "Z" : null }; Boolean.prototype.toJSON = this_value; Number.prototype.toJSON = this_value; String.prototype.toJSON = this_value } var gap, indent, meta, rep; function quote(string) { rx_escapable.lastIndex = 0; return rx_escapable.test(string) ? '"' + string.replace(rx_escapable, function (a) { var c = meta[a]; return typeof c === "string" ? c : "\\u" + ("0000" + a.charCodeAt(0).toString(16)).slice(-4) }) + '"' : '"' + string + '"' } function str(key, holder) { var i, k, v, length, mind = gap, partial, value = holder[key]; if (value && typeof value === "object" && typeof value.toJSON === "function") { value = value.toJSON(key) } if (typeof rep === "function") { value = rep.call(holder, key, value) } switch (typeof value) { case "string": return quote(value); case "number": return isFinite(value) ? String(value) : "null"; case "boolean": case "null": return String(value); case "object": if (!value) { return "null" } gap += indent; partial = []; if (Object.prototype.toString.apply(value) === "[object Array]") { length = value.length; for (i = 0; i < length; i += 1) { partial[i] = str(i, value) || "null" } v = partial.length === 0 ? "[]" : gap ? "[\n" + gap + partial.join(",\n" + gap) + "\n" + mind + "]" : "[" + partial.join(",") + "]"; gap = mind; return v } if (rep && typeof rep === "object") { length = rep.length; for (i = 0; i < length; i += 1) { if (typeof rep[i] === "string") { k = rep[i]; v = str(k, value); if (v) { partial.push(quote(k) + (gap ? ": " : ":") + v) } } } } else { for (k in value) { if (Object.prototype.hasOwnProperty.call(value, k)) { v = str(k, value); if (v) { partial.push(quote(k) + (gap ? ": " : ":") + v) } } } } v = partial.length === 0 ? "{}" : gap ? "{\n" + gap + partial.join(",\n" + gap) + "\n" + mind + "}" : "{" + partial.join(",") + "}"; gap = mind; return v } } if (typeof JSON.stringify !== "function") { meta = { "\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f", "\r": "\\r", '"': '\\"', "\\": "\\\\" }; JSON.stringify = function (value, replacer, space) { var i; gap = ""; indent = ""; if (typeof space === "number") { for (i = 0; i < space; i += 1) { indent += " " } } else { if (typeof space === "string") { indent = space } } rep = replacer; if (replacer && typeof replacer !== "function" && (typeof replacer !== "object" || typeof replacer.length !== "number")) { throw new Error("JSON.stringify") } return str("", { "": value }) } } if (typeof JSON.parse !== "function") { JSON.parse = function (text, reviver) { var j; function walk(holder, key) { var k, v, value = holder[key]; if (value && typeof value === "object") { for (k in value) { if (Object.prototype.hasOwnProperty.call(value, k)) { v = walk(value, k); if (v !== undefined) { value[k] = v } else { delete value[k] } } } } return reviver.call(holder, key, value) } text = String(text); rx_dangerous.lastIndex = 0; if (rx_dangerous.test(text)) { text = text.replace(rx_dangerous, function (a) { return "\\u" + ("0000" + a.charCodeAt(0).toString(16)).slice(-4) }) } if (rx_one.test(text.replace(rx_two, "@").replace(rx_three, "]").replace(rx_four, ""))) { j = eval("(" + text + ")"); return typeof reviver === "function" ? walk({ "": j }, "") : j } throw new SyntaxError("JSON.parse") } } }());

function importSceneData(jsonPath) {
    var file = new File(jsonPath);
    if (!file.exists) return "Error: JSON not found";
    file.open("r");
    var content = file.read();
    file.close();

    try {
        var data = JSON.parse(content);
        var scene = data.scene_data;
        var fps = scene.scene_info.fps || 24;

        var comp = app.project.activeItem;
        if (!comp || !(comp instanceof CompItem)) {
            comp = app.project.items.addComp("Maya Import", 1920, 1080, 1, 10, fps);
            comp.openInViewer();
        }

        var rootName = "Maya_World_Origin";
        var root = comp.layers.byName(rootName);
        if (!root) {
            root = comp.layers.addNull();
            root.name = rootName;
            root.threeDLayer = true;
            root.position.setValue([comp.width / 2, comp.height / 2, 0]);
            root.scale.setValue([100, 100, 100]);
            root.guideLayer = true;
            root.label = 11;
        }

        function applyAnimation(layer, animData, isCamera) {
            layer.threeDLayer = true;
            layer.parent = root;

            layer.autoOrient = AutoOrientType.NO_AUTO_ORIENT;

            for (var i = 0; i < animData.length; i++) {
                var frame = animData[i];
                var t = frame.f / fps;

                var pos = frame.t;
                var aeX = pos[0];
                var aeY = -pos[1];
                var aeZ = -pos[2];

                layer.position.setValueAtTime(t, [aeX, aeY, aeZ]);

                var rot = frame.r;
                if (isCamera) {
                    layer.rotationX.setValueAtTime(t, -rot[0]);
                    layer.rotationY.setValueAtTime(t, rot[1]);
                    layer.rotationZ.setValueAtTime(t, rot[2]);
                } else {
                    layer.rotationX.setValueAtTime(t, -rot[0]);
                    layer.rotationY.setValueAtTime(t, rot[1]);
                    layer.rotationZ.setValueAtTime(t, rot[2]);
                }
            }
        }

        var layersCreated = 0;

        if (scene.cameras) {
            for (var i = 0; i < scene.cameras.length; i++) {
                var c = scene.cameras[i];

                if (c.name.toLowerCase().indexOf("front") !== -1 || c.name.toLowerCase().indexOf("side") !== -1) {
                    alert("Warning: You are importing '" + c.name + "'. After Effects does not support Orthographic cameras. The view will look distorted (Perspective). Use a Perspective camera in Maya for best results.");
                }

                var existing = comp.layers.byName(c.name);
                if (existing) existing.remove();

                var l = comp.layers.addCamera(c.name, [comp.width / 2, comp.height / 2]);

                var film = c.film_back || 36;
                var zoom = (comp.width * c.focal_length) / film;
                l.property("Camera Options").property("Zoom").setValue(zoom);

                if (c.animation) applyAnimation(l, c.animation, true);

                l.moveToBeginning();
                layersCreated++;
            }
        }

        var objects = (scene.locators || []).concat(scene.meshes || []);
        for (var i = 0; i < objects.length; i++) {
            var obj = objects[i];
            var l = comp.layers.byName(obj.name);
            if (!l) {
                l = comp.layers.addNull();
                l.name = obj.name;
                l.source.name = obj.name;
            }
            if (obj.animation) applyAnimation(l, obj.animation, false);
            layersCreated++;
        }

        return "Synced Data (" + layersCreated + " items)";

    } catch (e) { return "Error: " + e.toString(); }
}

function getOrCreateFolder(folderName) {
    for (var i = 1; i <= app.project.numItems; i++) {
        var item = app.project.item(i);
        if (item instanceof FolderItem && item.name === folderName) return item;
    }
    return app.project.items.addFolder(folderName);
}

function importAndOrganize(filePath, passName) {
    try {
        var project = app.project;
        var parentFolder = getOrCreateFolder("Maya Renders");
        var importOptions = new ImportOptions();
        var f = new File(filePath);
        if (!f.exists) return "Error: File missing";
        importOptions.file = f;
        try { importOptions.sequence = true; var item = project.importFile(importOptions); }
        catch (e) { importOptions.sequence = false; var item = project.importFile(importOptions); }
        item.name = passName;
        item.parentFolder = parentFolder;
        var activeComp = project.activeItem;
        if (activeComp) activeComp.layers.add(item);
        return "Success";
    } catch (e) { return e.toString(); }
}