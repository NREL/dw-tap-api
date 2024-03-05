// // Options accordion
// var acc = document.getElementsByClassName("accordion");
// var i;
//
// for (i = 0; i < acc.length; i++) {
// acc[i].addEventListener("click", function() {
// this.classList.toggle("active");
// var panel = this.nextElementSibling;
// if (panel.style.maxHeight) {
// panel.style.maxHeight = null;
// } else {
// panel.style.maxHeight = panel.scrollHeight + "px";
// }
// });
// }
//
// // Results accordion
// var acc = document.getElementsByClassName("results_accordion");
// var i;
//
// for (i = 0; i < acc.length; i++) {
// acc[i].addEventListener("click", function() {
// this.classList.toggle("active");
// var panel = this.nextElementSibling;
// if (panel.style.maxHeight) {
// panel.style.maxHeight = null;
// } else {
// panel.style.maxHeight = panel.scrollHeight + "px";
// }
// });
// }


// Options accordion
function accordion_update() {
  var acc = document.getElementsByClassName("accordion");
  var i;

  for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
  this.classList.toggle("active");
  var panel = this.nextElementSibling;
  if (panel.style.maxHeight) {
  panel.style.maxHeight = null;
  } else {
  panel.style.maxHeight = panel.scrollHeight + "px";
  }
  });
  }
}
accordion_update();

// Results accordion
function results_accordion_update() {
  var acc = document.getElementsByClassName("results_accordion");
  var i;

  for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
  this.classList.toggle("active");
  var panel = this.nextElementSibling;
  if (panel.style.maxHeight) {
  panel.style.maxHeight = null;
  } else {
  panel.style.maxHeight = panel.scrollHeight + "px";
  }
  });
  }
}
results_accordion_update();
