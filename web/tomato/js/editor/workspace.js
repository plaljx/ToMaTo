var Workspace = Class.extend({
	init: function(container, editor) {
		this.container = container;
		this.editor = editor;
		container.addClass("ui-widget-content").addClass("ui-corner-all")
		container.addClass("tomato").addClass("workspace");
		container[0].obj = editor.topology;
		this.container.click(function(){});
    	this.size = {x: this.container.width(), y: this.container.height()};


    	this.subtopologyList = [];
    	this.canvas_dict = {};

    	var t = this;

    	ajax({
			url:'topology/'+ this.editor.options.topology + '/getsubtopology',
			synchronous: true,
			successFn:function(result){
				t.subtopologyList = result
				for (var i = 0; i < t.subtopologyList.length; i++){
    				t.canvas_dict[t.subtopologyList[i]] = Raphael(t.container[0], t.size.x, t.size.y);
    				t.canvas_dict[t.subtopologyList[i]].canvas.id = t.subtopologyList[i]
    				t.canvas_dict[t.subtopologyList[i]].workspace = t
    				t.canvas_dict[t.subtopologyList[i]].connectPath = t.canvas_dict[t.subtopologyList[i]].path("M0 0L0 0").attr({"stroke-dasharray": "- "});
    				t.editor.topology.subtopology_tabMenu(t.subtopologyList[i])
    			}
    			$('#workspace>svg').hide()
    			$('#main').show()
			},
			errorFn:function(error){
				new errorWindow({error:error});
			}
		});

		var c = this.canvas_dict[t.subtopologyList[0]];
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

    	this.canvas = this.canvas_dict[t.subtopologyList[0]]
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
	
	addCanvas:function(canvasname){
		var t = this;
		this.canvas_dict[canvasname] = Raphael(this.container[0], this.size.x, this.size.y);

		this.canvas_dict[canvasname].canvas.id = canvasname
		this.canvas_dict[canvasname].workspace = this

		this.canvas_dict[canvasname].connectPath = this.canvas_dict[canvasname].path("M0 0L0 0").attr({"stroke-dasharray": "- "});

		$("#" + canvasname).hide()
		var data = {
			'name': canvasname,
		}
		ajax({
			url:'topology/'+ this.editor.topology.id + '/addsubtopology',
			data:data,
			successFn:function(){
			},
			errorFn:function(error){
				new errorWindow({error:error});
			}
		})
	},

	tabCanvas:function(canvasname){

		var t = this;
		this.canvas = this.canvas_dict[canvasname]
    	this.connectPath = this.canvas.connectPath
    	$('#workspace>svg').hide();
    	$('#' + canvasname).show();

	},

	hideCanvas:function(){
		$('#workspace>svg').hide()
	},



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
				if (evt.offsetX) {
					pos = this.relPos({x: evt.offsetX, y: evt.offsetY});
				}
				else {
					var objPos = this.container.offset();
					pos = this.relPos({x: evt.pageX - objPos.left, y: evt.pageY - objPos.top});
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
