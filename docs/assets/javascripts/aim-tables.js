/* Table row labels.
 *
 * Below 38em a table stops being a grid and each row becomes a stacked block of label and value
 * pairs, so a wide table does not squeeze to one word per line. The value comes from the cell, but
 * the label is the text of that column's heading, and CSS cannot read another element's text. This
 * copies each heading onto the cells under it as data-label, which aim.css then prints with
 * ::before.
 *
 * A reader without JavaScript loses the labels, not the content: the stacked cells still carry
 * every value in row order. */
(function () {
  "use strict";

  function label(table) {
    var heads = [].map.call(table.querySelectorAll("thead th"), function (th) {
      return th.textContent.trim();
    });
    if (!heads.length) return;
    [].forEach.call(table.querySelectorAll("tbody tr"), function (row) {
      [].forEach.call(row.children, function (cell, index) {
        if (heads[index]) cell.setAttribute("data-label", heads[index]);
      });
    });
  }

  function run() {
    [].forEach.call(document.querySelectorAll(".md-typeset table:not([class])"), label);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
