// MathJax configuration for CulicidaeLab Server Documentation

window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};

// Additional configuration for better integration with Material theme
document$.subscribe(() => {
  MathJax.typesetPromise()
});