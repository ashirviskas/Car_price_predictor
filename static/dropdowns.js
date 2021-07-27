// This section creates the dynamic dropdowns

window.onload = function() {
  var makeSel = document.getElementById("makeSel"),
    modelSel = document.getElementById("modelSel"),
    yearSel = document.getElementById("yearSel");
  for (var make in makeObject) {
    makeSel.options[makeSel.options.length] = new Option(make, make);
  }
  makeSel.onchange = function() {
    modelSel.length = 1; // remove all options bar first
    yearSel.length = 1; // remove all options bar first
    if (this.selectedIndex < 1) return; // done
    for (var model in makeObject[this.value]) {
      modelSel.options[modelSel.options.length] = new Option(model, model);
    }
  }
  makeSel.onchange(); // reset in case page is reloaded
  modelSel.onchange = function() {
    yearSel.length = 1; // remove all options bar first
    if (this.selectedIndex < 1) return; // done
    var years = makeObject[makeSel.value][this.value];
    for (var i = 0; i < years.length; i++) {
      yearSel.options[yearSel.options.length] = new Option(years[i], years[i]);
    }
  }
}