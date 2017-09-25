function newResidueInput() {
  var residueInput = $("#residue-inputs .residue-input:last").clone();
  residueInput.find("input").val("");
  residueInput.insertBefore($("#new-residue-input"))
}

function removeResidueInput(button) {
  if ($(".residue-input").length > 1) {
    var input = $(button).closest("div");
    input.remove();
  }
}
