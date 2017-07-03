
var Mode = {
	select: "select",
	connect: "connect",
	connectOnce: "connect_once",
	remove: "remove",
	position: "position"
}

var Editor = Class.extend({
	init: function(options) {
		this.options = options;

		this.optionsManager = new OptionsManager(this);

		this.rextfv_status_updater = new RexTFV_status_updater(); //has to be created before any element.
		var t = this;

		this.allowRestrictedTemplates= false;
		this.allowRestrictedProfiles = false;
		this.allowRestrictedNetworks = false;
		this.isDebugUser = options.isDebugUser;
		for (var i=0; i<this.options.user.flags.length; i++) {
			if (this.options.user.flags[i] == "restricted_profiles") this.allowRestrictedProfiles = true;
			if (this.options.user.flags[i] == "restricted_templates") this.allowRestrictedTemplates= true;
			if (this.options.user.flags[i] == "restricted_networks") this.allowRestrictedNetworks= true;
		}

		this.options.grid_size = this.options.grid_size || 25;
		this.options.frame_size = this.options.frame_size || this.options.grid_size;
		this.listeners = [];
		this.capabilities = this.options.capabilities;
		this.menu = new Menu(this.options.menu_container);
		this.topology = new Topology(this);
		this.workspace = new Workspace(this.options.workspace_container, this);
		this.sites = this.options.sites;
		this.web_resources = this.options.web_resources;
		this.profiles = new ProfileStore(this.options.resources.profiles,this);
		this.templates = new TemplateStore(this.options.resources.templates,this);
		this.networks = new NetworkStore(this.options.resources.networks,this);
		this.buildMenu(this);
		this.setMode(Mode.select);

		// create web_resources.executable_archives_dict
		this.web_resources.executable_archives_dict = {};
		for(var i=0; i<this.web_resources.executable_archives.length; i++) {
			var archive = this.web_resources.executable_archives[i];
			if (archive.icon==undefined || archive.icon==null) archive.icon="/img/rextfv.png";
			this.web_resources.executable_archives_dict[archive.name] = archive;
		}

		this.sites_dict = {};
		for (s in this.sites) {
			this.sites_dict[this.sites[s].name] = this.sites[s];
		}

		this.workspace.setBusy(true);
		ajax ({
			url: "topology/"+options.topology+"/info",
			successFn: function(data){
				console.log(data)
				t.topology.load(data);
				t.workspace.setBusy(false);
				if (t.topology.data._initialized) {
					if (t.topology.data.timeout - new Date().getTime()/1000.0 < t.topology.editor.options.timeout_settings.warning) t.topology.renewDialog();
					if (t.topology.data._notes_autodisplay) t.topology.notesDialog();
				} else
					if (t.topology.data._tutorial_url) {
						t.topology.modify({
							"_initialized": true
						});
						t.topology.action("renew", {params:{
							"timeout": t.options.timeout_settings["default"]
						}});
					} else
						if (t.topology.data._initialized!=undefined)
							t.topology.initialDialog();
				t.workspace.updateTopologyTitle();
				t.options.onready();
			}
		});

		this.setWorkspaceContentMenu();

		setInterval(function(){t.rextfv_status_updater.updateSome(t.rextfv_status_updater)}, 1000);
	},
	triggerEvent: function(event) {
		log(event); //keep this logging
		for (var i = 0; i < this.listeners.length; i++) this.listeners[i](event);
	},
	setWorkspaceContentMenu: function() {
		var t = this;
		$('.tomato.workspace').on('contextmenu',function(e) {
			if(t.mode == Mode.connect || t.mode == Mode.connectOnce) {
				e.preventDefault();
				e.stopImmediatePropagation();

				t.setMode(Mode.select);
				t.workspace.connectPath.hide();

				$("#Modes_SelectandMove").addClass("ui-state-highlight");
				$("#Modes_Connect").removeClass("ui-state-highlight");

			}
		});

		['right', 'longclick'].forEach(
				function(trigger) {
					$.contextMenu({
						selector: '.tomato.workspace',
						trigger: trigger,
						build: function(trigger, e) {
							return createTopologyMenu(trigger[0].obj);
						}
				});
			});

	},

	setOption: function(name, value) {
		this.options[name] = value;
		this.optionsManager.saveOpt(name, this.options[name]);
		this.optionCheckboxes[name].setChecked(value);
		this.onOptionChanged(name);
		this.triggerEvent({component: "editor", object: this, operation: "option", name: name, value: value});
	},
	onOptionChanged: function(name) {
		this.topology.onOptionChanged(name);
		this.workspace.onOptionChanged(name);
		this.workspace.updateTopologyTitle();
		for(element in this.topology.elements) {
			this.topology.elements[element].paintUpdate();
		}
		for(connection in this.topology.connections) {
			this.topology.connections[connection].paintUpdate();
		}
	},
	optionMenuItem: function(options) {
		var t = this;

		return Menu.checkbox({
			name: options.name,
			label: options.label,
			tooltip: options.tooltip,
			func: function(value){
				t.setOption(options.name,value);
				t.onOptionChanged(options.name);
			},
			checked: this.options[options.name],
			enabled: (options.enabled == undefined) || options.enabled
		});
	},
	onElementConnectTo: function(el) {
		this.setMode(Mode.connectOnce);
		this.connectElement = el;
	},
	onElementSelected: function(el) {
		console.log(el)
		switch (this.mode) {
			case Mode.connectOnce:
				console.log(this.mode);
				if (! el.isConnectable()) {
					return;
				}
				this.topology.createConnection(el, this.connectElement);
				console.log("create connection")
				this.setMode(Mode.select);
				break;
			case Mode.connect:
				console.log(this.mode);
				if (! el.isConnectable()) return;
				// console.log("create connection")
				if (this.connectElement) {
					this.topology.createConnection(el, this.connectElement);
					this.connectElement = null;
				} else this.connectElement = el;
				break;
			case Mode.remove:
				if (! el.isRemovable()) return;
				el.remove();
				break;
			default:
				break;
		}
	},
	onConnectionSelected: function(con) {
		switch (this.mode) {
			case Mode.remove:
				con.remove();
				break;
			default:
				break;
		}
	},
	setMode: function(mode) {
		this.mode = mode;
		this.workspace.onModeChanged(mode);
		if (mode != Mode.position) this.positionElement = null;
		if (mode != Mode.connect && mode != Mode.connectOnce) this.connectElement = null;
		this.triggerEvent({component: "editor", object: this, operation: "mode", mode: this.mode});
	},
	setPositionElement: function(el) {
		this.positionElement = el;
		this.setMode(Mode.position);
	},
	createPositionElementFunc: function(el) {
		var t = this;
		return function() {
			t.setPositionElement(el);
		}
	},
	createModeFunc: function(mode) {
		var t = this;
		return function() {
			t.setMode(mode);
		}
	},
	createElementFunc: function(el) {
		var t = this;
		return function(pos) {
			var data = copy(el, true);
			data._pos = pos;
			if(this.workspace.canvas){
			data._pos['canvas'] = this.workspace.canvas.canvas.id;
			t.topology.createElement(data);
			t.selectBtn.click();
		}
		else{
			alert("no canvas");
		}
		}
	},
	createUploadFunc: function(type) {
		var t = this;
		return function(pos) {
			var data = {type: type, _pos: pos};
			data._pos['canvas'] = $('svg:visible').attr('id')
			t.topology.createElement(data, function(el1) {
					el1.showConfigWindow(false, function (el2) {
							el2.action("prepare", { callback: function(el3) {el3.uploadImage_fromFile();} });
						}
				);
				}
			);
			t.selectBtn.click();
		};
	},
	createTemplateFunc: function(tmpl) {
		return this.createElementFunc({type: tmpl.type, template: tmpl.name});
	},
	// addSubtopology: function(subtopologyname){

	// },
	buildMenu: function(editor) {
		var t = this;

		var toggleGroup = new ToggleGroup();

		var tab = this.menu.addTab(gettext("Home"));

		var group = tab.addGroup(gettext("Modes"));
		this.selectBtn = Menu.button({
			label: gettext("Select & Move"),
			name: "Modes_SelectandMove",
			icon: "img/select32.png",
			toggle: true,
			toggleGroup: toggleGroup,
			small: false,
			checked: true,
			func: this.createModeFunc(Mode.select)
		});
		group.addElement(this.selectBtn);
		group.addStackedElements([
			Menu.button({
				label: gettext("Connect"),
				name: "Modes_Connect",
				icon: "img/connect16.png",
				toggle: true,
				toggleGroup: toggleGroup,
				small: true,
				func: this.createModeFunc(Mode.connect)
			}),
			Menu.button({
				label: gettext("Delete"),
				name: "Modes_Delete",
				icon: "img/eraser16.png",
				toggle: true,
				toggleGroup: toggleGroup,
				small: true,
				func: this.createModeFunc(Mode.remove)
			})
		]);

		var group = tab.addGroup(gettext("Topology control"));
		group.addElement(Menu.button({
			label: gettext("Start"),
			icon: "img/start32.png",
			toggle: false,
			small: false,
			func: function() {
				t.topology.action_start();
			}
		}));
		group.addElement(Menu.button({
			label: gettext("Stop"),
			icon: "img/stop32.png",
			toggle: false,
			small: false,
			func: function() {
				t.topology.action_stop();
			}
		}));
		group.addStackedElements([
			Menu.button({
				label: gettext("Prepare"),
				icon: "img/prepare16.png",
				toggle: false,
				small: true,
				func: function() {
					t.topology.action_prepare();
				}
			}),
			Menu.button({
				label: gettext("Destroy"),
				icon: "img/destroy16.png",
				toggle: false,
				small: true,
				func: function() {
					t.topology.action_destroy();
				}
			})
		]);

		var group = tab.addGroup(gettext("Common elements"));
		var common = t.templates.getCommon();
		for (var i=0; i < common.length; i++) {
			var tmpl = common[i];
			group.addElement(tmpl.menuButton({
				label: tmpl.labelForCommon(),
				toggleGroup: toggleGroup,
				small: false,
				func: this.createPositionElementFunc(this.createTemplateFunc(tmpl))
			}));
		}
		for (var i=0; i < settings.otherCommonElements.length; i++) {
			var cel = settings.otherCommonElements[i];
			group.addElement(Menu.button({
				label: cel.label,
				name: cel.name,
				icon: cel.icon,
				toggle: true,
				toggleGroup: toggleGroup,
				small: false,
				func: this.createPositionElementFunc(this.createElementFunc(cel.data))
			}));
		}
		var common = t.networks.getCommon();
		for (var i=0; i < common.length; i++) {
			var net = common[i];
			group.addElement(Menu.button({
				label: net.label,
				name: net.name,
				icon: "img/internet32.png",
				toggleGroup: toggleGroup,
				small: false,
				func: this.createPositionElementFunc(this.createElementFunc({
					type: "external_network",
					kind: net.kind
				}))
			}));
		}

		var tab = this.menu.addTab(gettext("Devices"));

// <<<<<<< HEAD
// 		var group = tab.addGroup("Linux (OpenVZ)");
// 		var tmpls = t.templates.getAllowed("openvz");
// 		var btns = [];
// 		for (var i=0; i<tmpls.length; i++)
// 			 btns.push(tmpls[i].menuButton({
// 				toggleGroup: toggleGroup,
// 				small: true,
// 				func: this.createPositionElementFunc(this.createTemplateFunc(tmpls[i]))
// 		}));
// 		group.addStackedElements(btns);
//
// 		var group = tab.addGroup("Linux (KVM)");
// 		var tmpls = t.templates.getAllowed("kvmqm", "linux");
// 		var btns = [];
// 		for (var i=0; i<tmpls.length; i++)
// 		 if(tmpls[i].subtype == "linux")
// 			  btns.push(tmpls[i].menuButton({
// 				toggleGroup: toggleGroup,
// 				small: true,
// 				func: this.createPositionElementFunc(this.createTemplateFunc(tmpls[i]))
// 		}));
// 		group.addStackedElements(btns);
//
// 		var group = tab.addGroup("Other (KVM)");
// 		var tmpls = t.templates.getAllowed("kvmqm");
// 		var btns = [];
// 		for (var i=0; i<tmpls.length; i++)
// 		 if(tmpls[i].subtype != "linux")
// 			  btns.push(tmpls[i].menuButton({
// 			  	toggleGroup: toggleGroup,
// 				small: true,
// 			  	func: this.createPositionElementFunc(this.createTemplateFunc(tmpls[i]))
// 		}));
// 		group.addStackedElements(btns);
//
// 		var group = tab.addGroup("Scripts (Repy)");
// 		var tmpls = t.templates.getAllowed("repy");
// 		var btns = [];
// 		for (var i=0; i<tmpls.length; i++)
// 		 if(tmpls[i].subtype == "device")
// 		  btns.push(tmpls[i].menuButton({
// 		  	toggleGroup: toggleGroup,
// 		  	small: true,
// 		  	func: this.createPositionElementFunc(this.createTemplateFunc(tmpls[i]))
// 		}));
// 		group.addStackedElements(btns);
// =======
		for (var _type in this.options.vm_element_config) {
			for (var subtype in this.options.devices_config[_type]) {

				var group = tab.addGroup(this.options.devices_config[_type][subtype]);
				var tmpls = null;

				var is_any = null;
				if (subtype == "any") {
					tmpls = t.templates.getAllowed(_type);
					is_any = true;
				} else {
					tmpls = t.templates.getAllowed(_type, subtype);
					is_any = false;
				}

				var btns = [];
				for (var i=0; i<tmpls.length; i++)
					if( is_any ? !(tmpls[i].subtype in this.options.devices_config[_type]) : tmpls[i].subtype == subtype)
					  btns.push(tmpls[i].menuButton({
						toggleGroup: toggleGroup,
						small: true,
						func: this.createPositionElementFunc(this.createTemplateFunc(tmpls[i]))
						}));
				group.addStackedElements(btns);

				}
		}
//>>>>>>> glab_origin/master

		var group = tab.addGroup(gettext("Upload own images"));
		group.addStackedElements([
			Menu.button({
				label: gettext("Full Virtualization Image"),
				name: "kvm-custom",
				icon: "img/full32.png",
				toggle: true,
				toggleGroup: toggleGroup,
				small: true,
				func: this.createPositionElementFunc(this.createUploadFunc("full"))
			}),
			Menu.button({
				label: gettext("Container-Based Virtualization Image"),
				name: "openvz-custom",
				icon: "img/container32.png",
				toggle: true,
				toggleGroup: toggleGroup,
				small: true,
				func: this.createPositionElementFunc(this.createUploadFunc("container"))
			}),
			Menu.button({
				label: gettext("Repy script"),
				name: "repy-custom",
				icon: "img/repy32.png",
				toggle: true,
				toggleGroup: toggleGroup,
				small: true,
				func: this.createPositionElementFunc(this.createUploadFunc("repy"))
			})
		]);


		var tab = this.menu.addTab(gettext("Network"));

		var group = tab.addGroup(gettext("VPN Elements"));
		group.addElement(Menu.button({
			label: gettext("Switch (Tinc)"),
			name: "tinc-switch",
			icon: "img/switch32.png",
			toggle: true,
			toggleGroup: toggleGroup,
			small: false,
			func: this.createPositionElementFunc(this.createElementFunc({
				type: "tinc_vpn",
				mode: "switch"
			}))
		}));
		group.addElement(Menu.button({
			label: gettext("Hub (Tinc)"),
			name: "tinc-hub",
			icon: "img/hub32.png",
			toggle: true,
			toggleGroup: toggleGroup,
			small: false,
			func: this.createPositionElementFunc(this.createElementFunc({
				type: "tinc_vpn",
				mode: "hub"
			}))
		}));
		group.addElement(Menu.button({
			label: gettext("Switch (VpnCloud)"),
			name: "vpncloud-switch",
			icon: "img/switch32.png",
			toggle: true,
			toggleGroup: toggleGroup,
			small: false,
			func: this.createPositionElementFunc(this.createElementFunc({
				type: "vpncloud"
			}))
		}));

		var group = tab.addGroup(gettext("Scripts (Repy)"));
		group.addElement(Menu.button({
			label: gettext("Custom script"),
			name: "repy-custom",
			icon: "img/repy32.png",
			toggle: true,
			toggleGroup: toggleGroup,
			small: false,
			func: this.createPositionElementFunc(this.createUploadFunc("repy"))
		}));
		var tmpls = t.templates.getAllowed("repy");
		var btns = [];
		for (var i=0; i<tmpls.length; i++)
		 if(tmpls[i].subtype != "device")
		  btns.push(tmpls[i].menuButton({
		  	toggleGroup: toggleGroup,
		  	small: true,
		  	func: this.createPositionElementFunc(this.createTemplateFunc(tmpls[i]))
		}));
		group.addStackedElements(btns);

		var group = tab.addGroup(gettext("Networks"));
		var common = t.networks.getAllowed();
		var buttonstack = [];
		for (var i=0; i < common.length; i++) {
			var net = common[i];
			var inet_button = Menu.button({
				label: net.label,
				name: net.name,
				icon: net.icon,
				toggle: true,
				toggleGroup: toggleGroup,
				small: !net.big_icon,
				func: this.createPositionElementFunc(this.createElementFunc({
					type: "external_network",
					kind: net.kind
				}))
			});
			if (net.big_icon) {
				if(buttonstack.length>0) {
					group.addStackedElements(buttonstack);
					buttonstack=[];
				}
				group.addElement(inet_button);
			} else {
				buttonstack.push(inet_button);
			}
		}
		group.addStackedElements(buttonstack);




		var tab = this.menu.addTab(gettext("Topology"));

		var group = tab.addGroup(gettext("Functions"));

		group.addElement(Menu.button({
			label: gettext("Consoles (NoVNC)"),
			icon: "img/console32.png",
			toggle: false,
			small: false,
			func: function(){
				t.topology.tabbedConsoleWindow();
			}
		}));
		group.addElement(Menu.button({
			label: gettext("Notes"),
			icon: "img/notes32.png",
			toggle: false,
			small: false,
			func: function(){
				t.topology.notesDialog();
			}
		}));
		group.addElement(Menu.button({
			label: gettext("Resource usage"),
			icon: "img/office-chart-bar.png",
			toggle: false,
			small: false,
			func: function(){
				t.topology.showUsage();
			}
		}));


		var group = tab.addGroup(gettext("Management"));

        group.addElement(Menu.button({  // by Chang Rui
            label: gettext("Save As Scenario"),
            icon: "img/export16.png",
            toggle: false,
            small: false,
            func: function () {
                t.topology.saveAsScenarioDialog();
            }
        }));
		group.addElement(Menu.button({
			label: gettext("Renew"),
			icon: "img/renew.png",
			toggle: false,
			small: false,
			func: function(){
				t.topology.renewDialog();
			}
		}));
		group.addStackedElements([
			Menu.button({
				label: gettext("Rename"),
				icon: "img/rename.png",
				toggle: false,
				small: true,
				func: function(){
					t.topology.renameDialog();
				}
			}),
			Menu.button({
				label: gettext("Export"),
				icon: "img/export16.png",
				toggle: false,
				small: true,
				func: function() {
					window.open(document.URL+ "/export");
				}
			}),
			Menu.button({
				label: gettext("Delete"),
				name: "topology-remove",
				icon: "img/cross.png",
				toggle: false,
				small: true,
				func: function() {
					t.topology.remove();
				}
			})
		]);
		group.addElement(Menu.button({
			label: gettext("Users & Permissions"),
			icon: "img/user32.png",
			toggle: false,
			small: false,
			func: function() {
				t.workspace.permissionsWindow.createUserPermList();
				t.workspace.permissionsWindow.show();
			}
		}));


		var tab = this.menu.addTab(gettext("Options"));

		this.optionCheckboxes = {};
		this.optionsManager.buildOptionsTab(tab);

		// for topgroup
		// var tab = this.menu.addTab(gettext("Topgroup"));
		// var group = tab.addGroup(gettext("Manager"));

		// group.addElement(Menu.button({ 
  //           label: gettext("Add to topgroup"),
  //           icon: "img/repy32.png",
  //           toggle: false,
  //           small: false,
  //           func: function () {
  //               t.topology.topgroup_adddDialog();
  //           }
  //       }));
  //       group.addElement(Menu.button({  
  //           label: gettext("Create a Topgroup"),
  //           icon: "img/repy32.png",
  //           toggle: false,
  //           small: false,
  //           func: function () {
  //               t.topology.topgroup_createDialog();
  //           }
  //       }));
  //       group.addElement(Menu.button({  
  //           label: gettext("Remove from Topgroup"),
  //           icon: "img/repy32.png",
  //           toggle: false,
  //           small: false,
  //           func: function () {
  //               t.topology.topgroupDialog();
  //           }
  //       }));

        var tab = this.menu.addTab(gettext("Canvas"));
		var group = tab.addGroup(gettext("Manager"));
		group.addElement(Menu.button({  
            label: gettext("add subtopology"),
            icon: "img/repy32.png",
            toggle: false,
            small: false,
            func: function () {
                t.topology.subtopolgy_addDialog();
            }
        }));

		this.menu.paint();
	}
});