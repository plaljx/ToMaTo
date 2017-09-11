var Workspace = Class.extend({
	init: function(container, editor) {
		this.container = container;
		this.editor = editor;
		container.addClass("ui-widget-content").addClass("ui-corner-all")
		container.addClass("tomato").addClass("workspace");
		container[0].obj = editor.topology;
		this.container.click(function(){});
    	this.size = {x: this.container.width(), y: this.container.height()};
    	this.canvas = Raphael(this.container[0], this.size.x, this.size.y);
    	var c = this.canvas;
		var fs = this.editor.options.frame_size;
    	this.canvas.absPos = function(pos) {
    		return {x: fs + pos.x * (c.width-2*fs), y: fs + pos.y * (c.height-2*fs)};
    	}
    	this.canvas.relPos = function(pos) {
    		return {x: (pos.x - fs) / (c.width-2*fs), y: (pos.y - fs) / (c.height-2*fs)};
    	}
    	
    	//tutorial UI
    	this.tutorialWindow = new TutorialWindow({ 
			autoOpen: false, 
			draggable: true,  
			resizable: false, 
			title: ".", 
			modal: false, 
			buttons: {},
			width:500,
			closeOnEscape: false,
			tutorialVisible:this.editor.options.tutorial_show,
			tutorial_state:this.editor.options.tutorial_state,
			hideCloseButton: true,
			editor: this.editor
		});
    	
    	this.permissionsWindow = new PermissionsWindow({
    		autoOpen: false,
    		draggable: true,
    		resizable: false,
    		title: "Permissions",
    		modal: false,
    		width: 500,
    		topology: this.editor.topology,
    		isGlobalOwner: this.editor.options.isGlobalOwner, //todo: set value depending on user permissions
    		ownUserId: this.editor.options.user.id,
    		permissions: this.editor.options.permission_list
    	});
    	
    	var t = this;
    	this.editor.listeners.push(function(obj){
    		t.tutorialWindow.triggerProgress(obj);
    	});
    	
    	
		this.connectPath = this.canvas.path("M0 0L0 0").attr({"stroke-dasharray": "- "});
		this.container.click(function(evt){
			t.onClicked(evt);
		});
		this.container.mousemove(function(evt){
			t.onMouseMove(evt);
		});
		this.busyIcon = this.canvas.image("img/loading_big.gif", this.size.x/2, this.size.y/2, 32, 32);
		this.busyIcon.attr({opacity: 0.0});
	},
	// With old SubTopology
	_old_init: function(container, editor) {
		this.container = container;
		this.editor = editor;
		container.addClass("ui-widget-content").addClass("ui-corner-all")
		container.addClass("tomato").addClass("workspace");
		container[0].obj = editor.topology;
		this.container.click(function(){});
		this.size = {x: this.container.width(), y: this.container.height()};


		this.subtopologyInfoList = [];
		// this.subtopologyList = [];
		this.canvas_dict = {};

		var t = this;

		ajax({
			// url:'topology/'+ this.editor.options.topology + '/getsubtopology',
			url: 'topology/' + this.editor.options.topology + '/subtopology',
			data: '',
			synchronous: true,
			successFn:function(result){
				t.subtopologyInfoList = result;
				// for (var i = 0; i < t.subtopologyInfoList.length; i++) {
				// 	t.subtopologyList.push(t.subtopologyInfoList[i].name);
				// }
				for (var i = 0; i < t.subtopologyInfoList.length; i++){
					t.canvas_dict[t.subtopologyInfoList[i].id] = Raphael(t.container[0], t.size.x, t.size.y);
					t.canvas_dict[t.subtopologyInfoList[i].id].canvas.id = t.subtopologyInfoList[i].id;
					t.canvas_dict[t.subtopologyInfoList[i].id].workspace = t;
					t.canvas_dict[t.subtopologyInfoList[i].id].connectPath = t.canvas_dict[t.subtopologyInfoList[i].id].path("M0 0L0 0").attr({"stroke-dasharray": "- "});
				}
				for (var i = 0; i < t.subtopologyInfoList.length; i++) {
					if (t.subtopologyInfoList[i].permitted)
                        t.editor.topology.subtopology_tabMenu(t.subtopologyInfoList[i].name, t.subtopologyInfoList[i].id);
				}
				$('#workspace>svg').hide();
				// $('#main').show()
				$('#' + t.subtopologyInfoList[0].id).show();
			},
			errorFn:function(error){
				new errorWindow({error:error});
			}
		});

		var c = this.canvas_dict[t.subtopologyInfoList[0].id];
		var fs = t.editor.options.frame_size;
		this.absPos = function(pos){
			return {x: fs + pos.x * (c.width-2*fs), y: fs + pos.y * (c.height-2*fs)};
		};
		this.relPos = function(pos){
			return {x: (pos.x - fs) / (c.width-2*fs), y: (pos.y - fs) / (c.height-2*fs)};
		};

		//tutorial UI
		this.tutorialWindow = new TutorialWindow({
			autoOpen: false, 
			draggable: true,  
			resizable: false, 
			title: ".", 
			modal: false, 
			buttons: {},
			width:500,
			closeOnEscape: false,
			tutorialVisible:this.editor.options.tutorial_show,
			tutorial_state:this.editor.options.tutorial_state,
			hideCloseButton: true,
			editor: this.editor
		});

		this.permissionsWindow = new PermissionsWindow({
			autoOpen: false,
			draggable: true,
			resizable: false,
			title: "Permissions",
			modal: false,
			width: 500,
			topology: this.editor.topology,
			isGlobalOwner: this.editor.options.isGlobalOwner, //todo: set value depending on user permissions
			ownUserId: this.editor.options.user.id,
			permissions: this.editor.options.permission_list
		});
		this.groupWindow = new GroupWindow({
			autoOpen: false,
			draggable: true,
			resizable: false,
			title: gettext("Group Settings"),
			modal: false,
			width: 500,
			topology: this.editor.topology,
			ownUserId: this.editor.options.user.id
		});
		var t = this;

		this.canvas = this.canvas_dict[t.subtopologyInfoList[0].id];
		this.editor.listeners.push(function(obj){
			t.tutorialWindow.triggerProgress(obj);
		});

		this.connectPath = this.canvas.connectPath
		this.container.click(function(evt){
			t.onClicked(evt);
		});
		this.container.mousemove(function(evt){
			t.onMouseMove(evt);
		});
		this.busyIcon = this.canvas.image("img/loading_big.gif", this.size.x/2, this.size.y/2, 32, 32);
		this.busyIcon.attr({opacity: 0.0});


	},
	
	// SubTopology old
	// addCanvas(canvasName): send ajax request and add tab in bottom sub-menu
	// removeCanvas(canvasName): send ajax request
	// tabCanvas(canvasName): change canvas ?
	// hideCanvas(canvasName): hide canvas

	setBusy: function(busy) {
		this.busyIcon.attr({opacity: busy ? 1.0 : 0.0});
	},
	
	
	onMouseMove: function(evt) {
		if (! this.editor.connectElement) {
			this.connectPath.hide();
			return;
		}
		this.connectPath.show();
		var pos = this.editor.connectElement.getAbsPos();
		var mousePos = {x: evt.pageX - this.container.offset().left, y: evt.pageY - this.container.offset().top};
		this.connectPath.attr({path: "M"+pos.x+" "+pos.y+"L"+mousePos.x+" "+mousePos.y});
	},
	onClicked: function(evt) {
		switch (this.editor.mode) {
			case Mode.position:
				var pos;
				if (evt.offsetX) pos = this.canvas.relPos({x: evt.offsetX, y: evt.offsetY});
				else {
					var objPos = this.container.offset();
					pos = this.canvas.relPos({x: evt.pageX - objPos.left, y: evt.pageY - objPos.top});
				}
				this.editor.positionElement(pos);
				break;
			default:
				break;
		}
	},
	onOptionChanged: function(name) {
    		this.tutorialWindow.updateText();
	},
	onModeChanged: function(mode) {
		for (var name in Mode) this.container.removeClass("mode_" + Mode[name]);
		this.container.addClass("mode_" + mode);
	},
	
	updateTopologyTitle: function() {
		var t = editor.topology;
		var new_name="Topology '"+t.data.name+"'"+(editor.options.show_ids ? " ["+t.id+"]" : "");
		$('#topology_name').text(new_name);
		document.title = new_name+" - Provisec";
	}
});


['right', 'longclick'].forEach(function(trigger) {
	$.contextMenu({
		selector: 'rect,circle', //filtering on classes of SVG objects does not work
		trigger: trigger,
		build: function(trigger, e) {
			return createComponentMenu(trigger[0].obj);
		}
	});	
});
