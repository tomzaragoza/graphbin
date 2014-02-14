var sys = arbor.ParticleSystem({repulsion: 0, stiffness:1000, friction: 0.5, gravity: false});
sys.parameters({gravity:false});
sys.renderer = Renderer("#viewport") ;
var data = {
	nodes:{
		n1:{'color':'black','shape':'dot','label':'200', 'mass': 50, 'fixed': true},
		n2:{'color':'black','shape':'dot','label':'100', 'mass': 50, 'fixed': true},
		n3:{'color':'black','shape':'dot','label':'300', 'mass': 50, 'fixed': true},
		n4:{'color':'black','shape':'dot','label':'350', 'mass': 50, 'fixed': true},
		n5:{'color':'black','shape':'dot','label':'150', 'mass': 50, 'fixed': true},
	},
	edges:{
		n1:{ n2:{}, n3:{} },
		n2:{ n5:{} },
		n3:{ n4:{} }
	}
};

$("#viewport").mousedown(function(e){
	var pos = $(this).offset();
	var p = {x:e.pageX-pos.left, y:e.pageY-pos.top}
	selected = nearest = dragged = sys.nearest(p);

	if (selected.node !== null && selected.distance < 15){
		console.log("===========================");
		console.log("This is the nearest node");
		console.log(nearest.distance);
		console.log(selected.node);
		console.log("x coordinates of selected node");
		console.log(selected.node.p.x);
		console.log("y coordinates of selected node");
		console.log(selected.node.p.y);
		dragged.node.fixed = true;
	}
	return false;
});

sys.graft(data);