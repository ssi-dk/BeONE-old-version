if (!window.dash_clientside) {
     window.dash_clientside = {}
 }

window.dash_clientside.clientside = {
    tab_children = function(Phylocanvas) {
    var tree = Phylocanvas.createTree('phylocanvas');
      tree.load('(A:0.1,B:0.2,(C:0.3,D:0.4)E:0.5)F;');
    };

    window.Phylocanvas
    }