var Topology = Class.extend({
	init: function(editor) {
		this.editor = editor;
		this.sub_topologies = [];  // only data, not a concrete obj
		this.current_subtopology_id = null;
		this.elements = {};
		this.connections = {};
		this.pendingNames = [];
	},
	_getCanvas: function() {
		// SubTopology old, canvas_id
		/*
		if(canvas_id)
			return this.editor.workspace.canvas_dict[canvas_id];
		*/
		return this.editor.workspace.canvas;
	},
	// load sub-topology: add tab to tab-list, and add data to this.sub_topologies
	loadSubTopology: function(st, permitted) {
		st.elements = [];  // added when load elements
		this.sub_topologies.push(st);
		if (permitted)
			this.editor.subtopology_tab.addTab(st.id, st.name);
		return st;
	},
	loadElement: function(el) {
		var elObj;
		switch (el.type) {
			case "full":
			case "container":
			case "repy":
				elObj = new VMElement(this, el, this._getCanvas());
				break;
			case "full_interface":
			case "repy_interface":
				elObj = new VMInterfaceElement(this, el, this._getCanvas());
				break;
			case "container_interface":
				elObj = new VMConfigurableInterfaceElement(this, el, this._getCanvas());
				break;
			case "external_network":
				elObj = new ExternalNetworkElement(this, el, this._getCanvas());
				break;
			case "external_network_endpoint":
				//hide external network endpoints with external_network parent but show endpoints without parent
				elObj = el.parent ? new SwitchPortElement(this, el, this._getCanvas()) : new ExternalNetworkElement(this, el, this._getCanvas()) ;
				break;
			case "tinc_vpn":
				elObj = new VPNElement(this, el, this._getCanvas());
				break;
			case "tinc_endpoint":
				//hide tinc endpoints with tinc_vpn parent but show endpoints without parent
				elObj = el.parent ? new SwitchPortElement(this, el, this._getCanvas()) : new VPNElement(this, el, this._getCanvas()) ;
				break;
			case "vpncloud":
				elObj = new VPNElement(this, el, this._getCanvas());
				break;
			case "vpncloud_endpoint":
				//hide vpncloud endpoints with vpcloud parent but show endpoints without parent
				elObj = el.parent ? new SwitchPortElement(this, el, this._getCanvas()) : new VPNElement(this, el, this._getCanvas()) ;
				break;
			default:
				elObj = new UnknownElement(this, el, this._getCanvas());
				break;
		}
		if (el.id) {
			this.elements[el.id] = elObj;
			for (var i=0; i<this.sub_topologies.length; i++) {
				if (el.sub_topology === this.sub_topologies[i].name)
					this.sub_topologies[i].elements.push(elObj);
			}
		}
		if (el.parent) {
			//parent id is less and thus objects exists
			elObj.parent = this.elements[el.parent];
			this.elements[el.parent].children.push(elObj);
		}
		elObj.paint();
		return elObj;
	},
	loadConnection: function(con, elements) {
		var conObj = new Connection(this, con, this._getCanvas());
		// SubTopology old
		/*
		if(con.elements){
			tmp_canvas = this.elements[con.elements[0]].canvas;
		}else{
			tmp_canvas = elements[0].canvas;
		}
		var conObj = new Connection(this, con, tmp_canvas);
		*/
		if (con.id) this.connections[con.id] = conObj;
		if (con.elements) { //elements are given by id
			for (var j=0; j<con.elements.length; j++) {
				this.elements[con.elements[j]].connection = conObj;
				conObj.elements.push(this.elements[con.elements[j]]);
			}
		} else { //elements are given by object reference
			for (var j=0; j<elements.length; j++) {
				elements[j].connection = conObj;
				conObj.elements.push(elements[j]);
			}
		}
		conObj.paint();
		return conObj;
	},
	// Iterate all elements and connections, and load them
	// Add: load sub topologies as well
	load: function(data) {
		this.data = data;
		this.id = data.id;
		this.sub_topologies = [];
		var group_names = [];
		// if (this.options.user.name == this.)
		// if (this.permissions.)
		console.log(this.data.permissions[this.editor.options.user.name])
		console.log(this.editor.options.user.name)
		if (this.data.permissions[this.editor.options.user.name]) {
			for (var i=0; i<data.sub_topologies.length; i++) {
				var current = data.sub_topologies[i];
				this.loadSubTopology(current, true);
			}
		} else {
			for (var i=0; i<this.editor.options.user.groups.length; i++) {
				group_names.push(this.editor.options.user.groups[i].group)
			}
			data.sub_topologies.sort(function(a, b){return a.id > b.id ? 1 : (a.id < b.id ? -1 : 0);})
			for (var i=0; i<data.sub_topologies.length; i++) {
				var current = data.sub_topologies[i];
				// console.log("current st groups[0]: " + current.groups[0])
				// console.log("current st groups len: " + current.groups.length)
				var current_group_name = null;
				for (var j=0; j<current.groups.length; j++) {
					current_group_name = current.groups[j];
					console.log("current_group_name: " + current_group_name)
					if (group_names.indexOf(current_group_name) > -1) {
						console.log(true)
						this.loadSubTopology(current, true);
					} else {
						console.log(false)
						this.loadSubTopology(current, false);
					}
				}
			}
		}
		this.elements = {};
		//sort elements by id so parents get loaded before children
		data.elements.sort(function(a, b){return a.id > b.id ? 1 : (a.id < b.id ? -1 : 0);});
		for (var i=0; i<data.elements.length; i++) this.loadElement(data.elements[i]);
		this.connections = {};
		for (var i=0; i<data.connections.length; i++) this.loadConnection(data.connections[i]);

		this.editor.optionsManager.loadOpts();

		this.onUpdate();

		this.switchSubTopology(this.sub_topologies[0].id);
	},
	setBusy: function(busy) {
		this.busy = busy;
	},
	configWindowSettings: function() {
		return {
			order: ["name"],
			ignore: [],
			unknown: true,
			special: {}
		}
	},
	showConfigWindow: function(callback) {
		var t = this;
		var settings = this.configWindowSettings();

		this.configWindow = new AttributeWindow({
			title: gettext("Attributes"),
			width: 600,
			height: 600,
			maxHeight:800,
			buttons: {
				Save: function() {
					t.configWindow.hide();
					var values = t.configWindow.getValues();
					for (var name in values) {
						if (values[name] === t.data[name]) delete values[name];
						// Treat "" like null
						if (values[name] === "" && t.data[name] === null) delete values[name];
					}
					t.modify(values);
					t.configWindow.remove();
					t.configWindow = null;

					if(callback != null) {
						callback(t);
					}
				},
				Cancel: function() {
					t.configWindow.remove();
					t.configWindow = null;
				}
			}
		});
        this.configWindow.add(new TextElement({
				label: gettext("Name"),
				name: "name",
				value: this.data.name,
				disabled: false
		}));
		this.configWindow.add(new ChoiceElement({
			label: gettext("Site"),
			name: "site",
			choices: createMap(this.editor.sites, "name", function(site) {
				return (site.label || site.name) + (site.location ? (", " + site.location) : "");
			}, {"": "Any site"}),
			value: this.data.site,
			disabled: false
		}));
		this.configWindow.show();
	},
	modify: function(attrs) {
		this.setBusy(true);
		this.editor.triggerEvent({component: "topology", object: this, operation: "modify", phase: "begin", attrs: attrs});
		var t = this;
		ajax({
			url: 'topology/'+this.id+'/modify',
		 	data: attrs,
		 	successFn: function(result) {
				t.editor.triggerEvent({component: "topology", object: this, operation: "modify", phase: "end", attrs: attrs});
		 	},
		 	errorFn: function(error) {
		 		new errorWindow({error:error});
				t.editor.triggerEvent({component: "topology", object: this, operation: "modify", phase: "error", attrs: attrs});
		 	}
		});
		for (var name in attrs) {
		    this.data[name] = attrs[name];
    		if (name == "name") editor.workspace.updateTopologyTitle();
		}
	},
	action: function(action, options) {
		var options = options || {};
		var params = options.params || {};
		this.editor.triggerEvent({component: "topology", object: this, operation: "action", phase: "begin", action: action, params: params});
		var t = this;
		ajax({
			url: 'topology/'+this.id+'/action',
		 	data: {action: action, params: params},
		 	successFn: function(result) {
		 		var data = result[1];
		 		t.data = data;
				t.editor.triggerEvent({component: "topology", object: this, operation: "action", phase: "end", action: action, params: params});
		 	},
		 	errorFn: function(error) {
		 		new errorWindow({error:error});
				t.editor.triggerEvent({component: "topology", object: this, operation: "action", phase: "error", action: action, params: params});
		 	}
		});
	},
	modify_value: function(name, value) {
		var attrs = {};
		attrs[name] = value;
		this.modify(attrs);
		if (name == "name") editor.workspace.updateTopologyTitle();
	},
	isEmpty: function() {
		for (var id in this.elements) if (this.elements[id] != this.elements[id].constructor.prototype[id]) return false;
		return true;
		//no connections without elements
	},
	elementCount: function() {
		var count = 0;
		for (var id in this.elements) count++;
		return count;
	},
	connectionCount: function() {
		var count = 0;
		for (var id in this.connections) count++;
		return count;
	},
	nextElementName: function(data) {
		var names = [];
		for (var id in this.elements) names.push(this.elements[id].data.name);
		var base;
		switch (data.type) {
			case "external_network":
				base = data.kind || "internet";
				break;
			case "external_network_endpoint":
				base = (data.kind || "internet") + "_endpoint";
				break;
			case "tinc_vpn":
				base = data.mode || "switch";
				break;
			case "tinc_endpoint":
				base = "tinc";
				break;
			case "vpncloud":
				base = "switch";
				break;
			case "vpncloud_endpoint":
				base = "port";
				break;
			default:
				if (data && data.template) {
					base = editor.templates.get(data.type, data.template).label;
				} else {
					base = data.type;
				}
		}
		base = base+" #";
		var num = 1;
		while (names.indexOf(base+num) != -1 || this.pendingNames.indexOf(base+num) != -1) num++;
		return base+num;
	},
	createElement: function(data, callback) {
		if (!data.parent) data.name = data.name || this.nextElementName(data);
		// `sub_topology` field for a child element should be null/None
		if (!data.parent) data.sub_topology = this.current_subtopology_id;
		var obj = this.loadElement(data);
		this.editor.triggerEvent({component: "element", object: obj, operation: "create", phase: "begin", attrs: data});
		obj.setBusy(true);
		this.pendingNames.push(data.name);

		var t = this;
		ajax({
			url: "topology/" + this.id + "/create_element",
			data: data,
			successFn: function(data) {
				t.pendingNames.remove(data.name);
				t.elements[data.id] = obj;
				obj.setBusy(false);
				obj.updateData(data);

				if (callback) callback(obj);
				t.editor.triggerEvent({component: "element", object: obj, operation: "create", phase: "end", attrs: data});
				t.onUpdate();
			},
			errorFn: function(error) {
		 		new errorWindow({error:error});
				obj.paintRemove();
				t.pendingNames.remove(data.name);
				t.editor.triggerEvent({component: "element", object: obj, operation: "create", phase: "error", attrs: data});
			}
		});
		return obj;
	},
	createConnection: function(el1, el2, data) {
		if (el1 == el2) return;
		if (! el1.isConnectable()) return;
		if (! el2.isConnectable()) return;
		var ids = 0;
		var t = this;
		var obj;
		var callback = function(ready) {
			ids++;
			if (ids < 2) return;
			t.editor.triggerEvent({component: "connection", object: obj, operation: "create", phase: "begin", attrs: data});
			data.elements = [el1.id, el2.id];
			ajax({
				url: "connection/create",
				data: data,
				successFn: function(data) {
					t.connections[data.id] = obj;
					obj.updateData(data);
					t.editor.triggerEvent({component: "connection", object: obj, operation: "create", phase: "end", attrs: data});
					t.onUpdate();
					el1.onConnected();
					el2.onConnected();
				},
				errorFn: function(error) {
			 		new errorWindow({error:error});
					obj.paintRemove();
					t.editor.triggerEvent({component: "connection", object: obj, operation: "create", phase: "error", attrs: data});
				}
			});
		};
		el1 = el1.getConnectTarget(callback);
		el2 = el2.getConnectTarget(callback);
		data = data || {};
		obj = this.loadConnection(copy(data, true), [el1, el2]);
		return obj;
	},
	onOptionChanged: function(name) {
		this.onUpdate();
	},
	action_delegate: function(action, options) {
		var options = options || {};
		if ((action=="destroy"||action=="stop") && !options.noask && this.editor.options.safe_mode && ! confirm("Do you want to " + action + " this topology?")) return;
		this.editor.triggerEvent({component: "topology", object: this, operation: "action", phase: "begin", action: action});
		var ids = 0;
		var t = this;
		var cb = function() {
			ids--;
			if (ids <= 0 && options.callback) options.callback();
			t.editor.triggerEvent({component: "topology", object: this, operation: "action", phase: "end", action: action});
		}
		for (var id in options.elements||this.elements) {
			var el = this.elements[id];
			if (el.busy) continue;
			if (el.parent) continue;
			if (el.actionEnabled(action)) {
				ids++;
				el.action(action, {
					noask: true,
					callback: cb,
					noUpdate: options.noUpdate
				});
			}
		}
		if (ids <= 0 && options.callback) options.callback();
		this.onUpdate();
	},
	_twoStepPrepare: function(callback) {
		var vmids = {};
		var rest = {};
		for (var id in this.elements) {
			var element = this.elements[id];
			switch (element.data.type) {
				case 'container':
				case 'full':
				case 'repy':
					vmids[id] = element;
					break;
				default:
					rest[id] = element;
			}
		}
		var t = this;
		this.action_delegate("prepare", {
			elements: vmids,
			callback: function() {
				t.action_delegate("prepare", {
					elements: rest,
					callback: callback
				})
			}
		})
	},
	action_start: function() {
		var t = this;
		this._twoStepPrepare(function(){
			t.action_delegate("start", {});
		});
	},
	action_stop: function() {
		this.action_delegate("stop");
	},
	action_prepare: function() {
		this._twoStepPrepare();
	},
	action_destroy: function() {
		var t = this;
		if (this.editor.options.safe_mode && !confirm(gettext("Are you sure you want to completely destroy this topology?"))) return;
		this.action_delegate("stop", {
			callback: function(){
				t.action_delegate("destroy", {noask: true});
			}, noask: true
		});
	},
	remove: function() {
		if (this.editor.options.safe_mode && !confirm(gettext("Are you sure you want to completely remove this topology?"))) return;
		var t = this;
		var removeTopology = function() {
			t.editor.triggerEvent({component: "topology", object: t, operation: "remove", phase: "begin"});
			ajax({
				url: "topology/"+t.id+"/remove",
				successFn: function() {
					t.editor.triggerEvent({component: "topology", object: t, operation: "remove", phase: "end"});
					window.location = "/topology";
				}
			});
		}
		this.action_delegate("stop", {noask: true, noUpdate: true, callback: function() {
			t.action_delegate("destroy", {noask: true, noUpdate: true, callback: function() {
				if (t.elementCount()) {
					for (var elId in t.elements) {
						if (t.elements[elId].parent) continue;
						t.elements[elId].remove(function(){
							if (! t.elementCount()) removeTopology();
						}, false);
					}
				} else removeTopology();
			}});
		}});
	},
	saveAsScenario: function(data) {    // by Chang Rui
		var t = this;
		ajax({
			url: 'topology/' + this.id + '/save_as_scenario',
			data: data,
			successFn: function (result) {
				console.log("Save as scenario: Success.");
				console.log("Result: " + result)
			},
			errorFn: function (error) {
				new errorWindow({error:error});
			}
		})
	},
	showDebugInfo: function() {
		var t = this;
		ajax({
			url: 'topology/'+this.id+'/info',
		 	data: {},
		 	successFn: function(result) {
		 		var win = new Window({
		 			title: "Debug info",
		 			width: 500,
		 			buttons: {
		 				Close: function() {
		 					win.hide();
		 				}
					}
		 		});
		 		div = $('<div></div>');
		 		new PrettyJSON.view.Node({
		 			data: result,
		 			el: div
		 		});
		 		win.add(div);
		 		win.show();
		 	},
		 	errorFn: function(error) {
		 		new errorWindow({error:error});
		 	}
		});
	},
	showUsage: function() {
  		window.open('/topology/'+this.id+'/usage', '_blank', 'innerHeight=450,innerWidth=650,status=no,toolbar=no,menubar=no,location=no,hotkeys=no,scrollbars=no');
		this.editor.triggerEvent({component: "topology", object: this, operation: "usage-dialog"});
	},
	notesDialog: function() {
		var dialog = $("<div/>");
		var ta = $('<textarea cols=60 rows=20 class="notes"></textarea>');
		ta.text(this.data._notes || "");
		dialog.append(ta);
		var openWithEditor_html = $('<input type="checkbox" name="openWithEditor">' + gettext('Open Window with Editor') + '</input>');		
		var openWithEditor = openWithEditor_html[0];
		if (this.data._notes_autodisplay) {
			openWithEditor.checked = true;
		}
		dialog.append($('<br/>'))
		dialog.append(openWithEditor_html);
		var t = this;
		dialog.dialog({
			autoOpen: true,
			draggable: true,
			resizable: true,
			height: "auto",
			width: 550,
			title: gettext("Notes for Topology"),
			show: "slide",
			hide: "slide",
			modal: true,
			buttons: {
				Save: function() {
		        	dialog.dialog("close");
			      	t.modify_value("_notes", ta.val());
			      	t.modify_value("_notes_autodisplay", openWithEditor.checked)
			    },
		        Close: function() {
		        	dialog.dialog("close");
		        }
			}
		});
	},
	renameDialog: function() {
		var t = this;
		windowOptions = {
			title: gettext("Rename Topology"),
			width: 550,
			inputname: "newname",
			inputlabel: gettext("New Name:"),
			inputvalue: t.data.name,
			onChangeFct: function () {
				if(this.value == '') {
					$('#rename_topology_window_save').button('disable');
				} else {
					$('#rename_topology_window_save').button('enable');
				}
			},
			buttons: [
				{
					text: gettext("Save"),
					id: "rename_topology_window_save",
					click: function() {
						t.rename.hide();
						if(t.rename.element.getValue() != '') {
							t.modify_value("name", t.rename.element.getValue());
						}
						t.rename = null;
					}
				},
				{
					text: gettext("Cancel"),
					click: function() {
						t.rename.hide();
						t.rename = null;
					}
				}
			],
		};
		this.rename = new InputWindow(windowOptions);
		this.rename.show();
	},

	// SubTopology old
	// ================================
	// subtopology_addDialog
	// subtopology_removeDialog
	// subtopologyGroupDialog
	// subtopology_tabMenu:function(name, id){
	// 	var t = this;
	// 	// var name;
	// 	$("#subtopology_tab").append('<button type="button" class="button button-pill button-action" id ="tab_' + id + '" >' + name +'</button>');
	// 	$('#tab_' + id).click(function(){
	// 		// var canvasName = $('#tab_' + id).text();
	// 		t.editor.workspace.hideCanvas();
	// 		t.editor.workspace.tabCanvas(id);
	// 	})
	// },
	renewDialog: function() {
		var t = this;
		var dialog, timeout;
		var may_renew = this.data.permissions[this.editor.options.user.name] == "owner" || this.data.permissions[this.editor.options.user.name] == "manager"

		dialog = new AttributeWindow({
			title: gettext("Topology Timeout"),
			width: 500,
			height: 400,
			buttons: may_renew ? [
						{
							text: gettext("Save"),	
							click: function() {
								t.action("renew", {params:{
									"timeout": parseFloat(timeout.getValue())
								}});
								dialog.remove();
							}
						},
						{
							text: gettext("Close"),				
							click: function() {
								dialog.remove();
							}
						}
					] : [
						{
							text: gettext("Close"),
							click: function() {
								dialog.remove();
							}
						}
					],
		});
		var choices = {};
		var timeout_settings = t.editor.options.timeout_settings;
		for (var i = 0; i < timeout_settings.options.length; i++) choices[timeout_settings.options[i]] = formatDuration(timeout_settings.options[i]);
		var timeout_val = t.data.timeout - new Date().getTime()/1000.0;
		var text = timeout_val > 0 ? ("Your topology will time out in <strong>" + formatDuration(timeout_val)) + "</strong>" : "Your topology has timed out. You must renew it to use it.";
		if (timeout_val < timeout_settings.warning) text = '<p class="alert alert-danger">' + text + '</p>';
		dialog.addText("<center>"  + text + "</center>");
		if (may_renew) {
			// if user is allowed to renew
			timeout = dialog.add(new ChoiceElement({
				name: "timeout",
				label: gettext("New timeout"),
				choices: choices,
				value: timeout_settings["default"],
				help_text: gettext("After this time, your topology will automatically be stopped. Timeouts can be extended regularly to allow your topology to run longer without interruptions. You will receive a warning before your topology is stopped.")
			}));
		} else {
			dialog.addText("<div>You do not have permissions to renew this topology. Please contact a topology owner or manager to renew.</div>")
		}
		dialog.show();
	},
	saveAsScenarioDialog: function() {    // by Chang Rui
		var t = this;
		var dialog;
		var id, name, description, accessibility, author;
		var choices = {
			"private": "Private",
			"public": "Public",
		};
		// , name, description, timeout;
		dialog = new AttributeWindow({
			title: gettext("Save As Scenario"),
			width: 500,
			// height: 400,
			// closable: false,
			buttons: [
				{
					text: gettext("Save"),
					id: "scenario_dialog_save",
					click: function() {
						var data = {
							"topology_id": t.id,
							"name": name.getValue(),
							"description": description.getValue(),
							"accessibility": accessibility.getValue(),
							"author": author.getValue()
						};
						t.saveAsScenario(data);
						if (dialog != null) {
							dialog.remove()
						}
						dialog = null;
					}
				},
				{
					text: gettext("Close"),
					click: function() {
						dialog.remove();
					}
				}
			]
		});
		// dialog.addText("<div>123456789.</div>")
		id = dialog.add(new TextElement({
			name: "id",
			label: "ID",
			disabled: true,
			value: this.id,
		}));
		author = dialog.add(new TextElement({
			name: "author",
			label: gettext("Author"),
			disabled: true,
			value: this.editor.options.user.name,
		}));
		name = dialog.add(new TextElement({
			name: "name",
			label: gettext("Name"),
			help_text: gettext("The name of your scenario"),
			onChangeFct: function() {
				// TODO: name inspection ineffective?
				if(this.value == '') {
					$('#scenario_dialog_save').button('disable');
				} else {
					$('#scenario_dialog_save').button('enable');
				}
			},
		}));
		description = dialog.add(new TextAreaElement({
			name: "description",
			label: gettext("Description"),
			help_text: gettext("The text description of your scenario."),
		}));
		accessibility = dialog.add(new ChoiceElement({
			name: "accessibility",
			label: gettext("Accessibility"),
			// value: choices[0],
			choices: choices,
			help_text: gettext("Whether other users can use the scenario.")
		}));

		dialog.show();
	},
	tabbedConsoleWindow: function() {
	    window.open('../topology/'+this.id+'/tabbed-console', '_blank', "innerWidth=760,innerheight=483,status=no,toolbar=no,menubar=no,location=no,hotkeys=no,scrollbars=no");
	},
	initialDialog: function() {
		var t = this;
		var dialog, name, description, timeout;
		dialog = new AttributeWindow({
			title: gettext("New Topology"),
			width: 500,
			closable: false,
			buttons: [
						{
							text: gettext("Save"),
							disabled: true,
							id: "new_topology_window_save",
							click: function() {
								if (name.getValue() && timeout.getValue()) {
									t.modify({
										"name": name.getValue(),
										"_notes": description.getValue(),
										"_initialized": true
									});
									editor.workspace.updateTopologyTitle();
									t.action("renew", {params:{
										"timeout": parseFloat(timeout.getValue())
									}});
									dialog.remove();
									dialog = null;
								}
							}
						}
					],
		});
		name = dialog.add(new TextElement({
			name: "name",
			label: gettext("Name"),
			help_text: gettext("The name for your topology"),
			onChangeFct:  function () {
				if(this.value == '') {
					$('#new_topology_window_save').button('disable');
				} else {
					$('#new_topology_window_save').button('enable');
				}
			}
		}));
		var choices = {};
		var timeout_settings = t.editor.options.timeout_settings;
		for (var i = 0; i < timeout_settings.options.length; i++) choices[timeout_settings.options[i]] = formatDuration(timeout_settings.options[i]);
		timeout = dialog.add(new ChoiceElement({
			name: "timeout",
			label: gettext("Timeout"),
			choices: choices,
			value: timeout_settings["default"],
			help_text: gettext("After this time, your topology will automatically be stopped. Timeouts can be extended arbitrarily.")
		}));
		description = dialog.add(new TextAreaElement({
			name: "description",
			label: gettext("Description"),
			help_text: gettext("Description of the experiment. (Optional)"),
			value: t.data._notes
		}));
		dialog.show();
	},
	name: function() {
		return this.data.name;
	},
	onUpdate: function() {
		this.checkNetworkLoops();
		var segments = this.getNetworkSegments();
		// TODO: Check this
		// this.colorNetworkSegments(segments);
		this.editor.triggerEvent({component: "topology", object: this, operation: "update"});
	},
	getNetworkSegments: function() {
		var segments = [];
		for (var con in this.connections) {
			var found = false;
			for (var i=0; i<segments.length; i++)
			 if (segments[i].connections.indexOf(this.connections[con].id) >= 0)
			  found = true;
			if (found) continue;
			segments.push(this.connections[con].calculateSegment());
		}
		return segments;
	},
	checkNetworkLoops: function() {
		var maxCount = 1;
		this.loop_last_warn = this.loop_last_warn || 1;
		for (var i in  this.elements) {
			var el = this.elements[i];
			if (el.data.type != "external_network_endpoint") continue;
			if (! el.connection) continue; //can that happen?
			var segment = el.connection.calculateSegment([el.id], []);
			var count = 0;
			for (var j=0; j<segment.elements.length; j++) {
				var e = this.elements[segment.elements[j]];
				if (! e) continue; //brand new element
				if (e.data.type == "external_network_endpoint") count++;
			}
			maxCount = Math.max(maxCount, count);
		}
		if (maxCount > this.loop_last_warn) showError(gettext("Network segments must not contain multiple external network exits! This could lead to loops in the network and result in a total network crash."));
		this.loop_last_warn = maxCount;
	},
	colorNetworkSegments: function(segments) {
		var skips = 0;
		for (var i=0; i<segments.length; i++) {
			var cons = segments[i].connections;
			var num = (this.editor.options.colorify_segments && cons.length > 1) ? (i-skips) : NaN;
			if (cons.length == 1) skips++;
			for (var j=0; j<cons.length; j++) {
				var con = this.connections[cons[j]];
				if (! con) continue; //brand new connection
				con.setSegment(num);
			}
		}
	},
	createSubTopology: function(name) {
		var t = this;
		var data = {
			'name': name
		};
		ajax({
			url: 'topology/'+ this.editor.topology.id + '/subtopology/add',
			data: data,
			successFn: function(result){
				t.editor.subtopology_tab.addTab(result.id, result.name);
			},
			errorFn: function(error){
				new errorWindow({error: error});
			},
		});
	},
	// remove the elems in the sub-topo
	// and try to remove the sub-topo itself
	// switch to first available sub-topo after successful removing
	removeSubTopology: function (st_id) {
		if (!confirm(gettext("Are you sure you want to remove the sub topology?\nThis will DESTROY the whole topology!")))
			return;
		var t = this;
		var removeSubTopology = function () {
			ajax({
				url: 'topology/' + t.editor.topology.id + '/subtopology/' + st_id + '/remove',
				successFn: function (result) {
					t.editor.subtopology_tab.removeTabById(st_id);
					t.switchSubTopology(t.sub_topologies[0]);
				},
				errorFn: function (error) {
					new errorWindow({ error: error });
				}
			});
		};
		t.action_delegate("stop", {noask: true, noUpdate: true, callback: function() {
			t.action_delegate("destroy", {noask: true, noUpdate: true, callback: function(){
				if (t.subtpologyElementCount(st_id)) {
					for (var elId in t.elements) {
						if (t.elements[elId].parent) continue;
						console.log(t.elements[elId].data.sub_topology);
						if (t.elements[elId].data.sub_topology === st_id) {
							console.log("remove elem:" + t.elements[elId].data.id);
							t.elements[elId].remove(function(){
								if (! t.subtpologyElementCount(st_id))
								removeSubTopology(st_id);
							}, false);
						}
					}
				}
				else 
					removeSubTopology(st_id);
			}});
		}});
		
		
	},
	subTopologyAddGroup: function (st_id, group_name) {
		var t = this;
		var topo_id = this.id;
		data = { group: group_name }
		ajax({
			url: 'topology/'+ topo_id + '/subtopology/' + st_id + '/add_group',
			data: data,
			successFn: function (result) {
				console.log('Sub Topology Add Group')
				console.log(result)
			},
			errorFn: function (error) {
				new errorWindow({error:error});
			},
		})
	},
	subTopologyAddGroupDialog: function (st_id) {
		var t = this;
		var subTopology, group;
		var dialog = new AttributeWindow({
			title: gettext('SubTopology Add Group'),
			width: 500,
			buttons: [
                {
                    text: gettext("Ok"),
                    click: function(){
						t.subTopologyAddGroup(st_id, group.getValue());
						if (dialog != null) {
							dialog.remove();
						}
						dialog = null;
                    }
                },
				{
					text: gettext("Cancel"),
					click: function() {
						if (dialog != null) {
							dialog.remove();
						}
						dialog = null;
					}
				}
			]
		});
		subTopology = dialog.add(new TextElement({
			name: "sub_topology",
			label: gettext("Sub Topology Id"),
			value: st_id,
			disabled: true,
			help_text: gettext("The ID of sub topology."),
		}));
		group = dialog.add(new TextElement({
			name: "group",
			label: gettext("Group"),
			help_text: gettext("The name of group"),
		}));
		dialog.show();
	},
	// `paint()` some elements and conns in specified sub-topo
	// and `paintRemove()` other elements and conns
	switchSubTopology: function(sub_topo) {
		var t = this;

		console.log("Switch Sub-Topo: " + sub_topo);
		// in the case if sub_topo is Id or data object
		var st_id = sub_topo.id ? sub_topo.id : sub_topo;
		for (var elId in t.elements) 
			t.elements[elId].paintRemove();
		for (var connId in t.connections) 
			t.connections[connId].paintRemove();
		for (var connId in t.connections) {
			if (t.connections[connId].elements[0].data['sub_topology'] === st_id
			 || t.connections[connId].elements[1].data['sub_topology'] === st_id) {
				t.connections[connId].paint();
			 }
		}
		for (var elId in t.elements) {
			if (t.elements[elId].data['sub_topology'] === st_id)
				t.elements[elId].paint();
			else if (t.elements[elId].parent && t.elements[elId].parent.data['sub_topology'] === st_id)
				t.elements[elId].paint();
		}
		// TODO: show connections
		this.current_subtopology_id = st_id;
	},
	subtpologyElementCount: function(st_id) {
		var count = 0;
		for (var elId in this.elements){
			if (this.elements[elId].data.sub_topology === st_id)
				count ++;
		}
		console.log("count: " + count);
		return count;
	},
	subtopolgyAddDialog: function(){
		var t = this;
		var name;
		var dialog = new AttributeWindow({
			title: gettext('add subtopology'),
			width: 550,
			buttons: [
			{
				text: gettext('Save'),
				click:function(){
					st_name = name.getValue();
					t.createSubTopology(st_name);

					dialog.hide()
				}
			},
			{
				text:gettext('Cancel'),
				click:function(){
					dialog.hide()
				}
			}
			]
		});
		name = dialog.add(new TextElement({
			name: "name",
			label: gettext("Name"),
			help_text: gettext("The name of your subtopology"),
		}));
		dialog.show()
	},
});