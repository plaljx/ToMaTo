



var createElementMenu = function(obj) {
	var header= {
		html:'<span>'+obj.name()+'<small><br />Element'+
		(editor.options.show_ids ? 
				" ["+obj.id+"]" :
				"")+
		(editor.options.show_sites_on_elements && obj.component_type=="element" && obj.data && "site" in obj.data ? "<br />"+
				(obj.data.host_info && obj.data.host_info.site ?
						"at "+editor.sites_dict[obj.data.host_info.site].label :
						(obj.data.site ?
								"will be at " + editor.sites_dict[obj.data.site].label :
								"no site selected")  ) : 
				"")+
		'</small></span>', 
		type:"html"
	}
	var menu;

	var topgroup_info = {}
	ajax({
		url: 'topgroup/'+ obj.topology.id+'/gettopgroupinfo',
		data: {},
		synchronous: true,
		successFn: function(result){
			// console.log(result)
			// console.log(result)
			topgroup_info = result['info']
			console.log(topgroup_info)
		},
		errorFn: function(error){
			new errorWindow({error:error});
		}
	})
	
	if (obj.busy) {
		menu={
			callback: function(key, options) {},
			items: {
				"header": header,
				"busy_indicator": {
					name:gettext('Please wait for the current action to finish and re-open this menu.'),
					icon:'loading'
				}
			}
		}
	} else {
		menu= {
			callback: function(key, options) {},
			items: {
				"header": header,
				"connect": obj.isConnectable() ? {
					name:gettext('Connect'),
					icon:'connect',
					callback: function(){
						obj.editor.onElementConnectTo(obj);
					}
				} : null,
				"start": obj.actionEnabled("start") ? {
					name:gettext('Start'),
					icon:'start',
					callback: function(){
						obj.action_start();
					}
				} : null,
				"stop": obj.actionEnabled("stop") ? {
					name:gettext("Stop"),
					icon:"stop",
					callback: function(){
						obj.action_stop();
					}
				} : null,
				"prepare": obj.actionEnabled("prepare") ? {
					name:gettext("Prepare"),
					icon:"prepare",
					callback: function(){
						obj.action_prepare();
					}
				} : null,
				"destroy": obj.actionEnabled("destroy") ? {
					name:gettext("Destroy"),
					icon:"destroy",
					callback: function(){
						obj.action_destroy();
					}
				} : null,
				"sep2": (obj.actionEnabled("destroy") || obj.actionEnabled("prepared") || obj.actionEnabled("start")) ? "---"
				: null,
				"console": obj.consoleAvailable() || obj.actionEnabled("download_log_grant") ? {
					name:gettext("Console"),
					icon:"console",
					items: {
						"console_novnc": obj.consoleAvailable() && obj.data.websocket_pid ? {
							name:"NoVNC (HTML5+JS)",
							icon:"novnc",
							callback: function(){
								obj.openConsoleNoVNC();
							}
						} : null,
						"console_java": obj.consoleAvailable() ? {
							name: "Java applet",
							icon: "java-applet",
							callback: function(){
								obj.openConsole();
							}
						} : null,
						"console_link": obj.consoleAvailable() ? {
							name:"open vnc:// link",
							icon:"console",
							callback: function(){
								obj.openVNCurl();
							}
						} : null,
						"console_info": obj.consoleAvailable() ? {
							name:"VNC Information",
							icon:"info",
							callback: function(){
								obj.showVNCinfo();
							}
						} : null,
						"sepconsole": obj.actionEnabled("download_log_grant") && obj.consoleAvailable() ? "---" : null,
						"log": obj.actionEnabled("download_log_grant") ? {
							name:gettext("Download Log"),
							icon:"console_download",
							callback: function(){
								obj.downloadLog();
							},
						} : null,
					}
				} : null,
				"used_addresses": obj.data.used_addresses ? {
					name:gettext("Used addresses"),
					icon:"info",
					callback: function(){
						obj.showUsedAddresses();
					}
				} : null,
				"usage": {
					name:gettext("Resource usage"),
					icon:"usage",
					callback: function(){
						obj.showUsage();
					}
				},
				"disk_image": (obj.actionEnabled("download_grant") || obj.actionEnabled("upload_grant")) || obj.actionEnabled("change_template") ? { 
					name: gettext("Disk image"),
					icon: "drive",
					items: {
						"change_template": obj.actionEnabled("change_template") ? {
							name:gettext("Change Template"),
							icon:"edit",
							callback: function() {
								obj.showTemplateWindow();
							}
						} : null,
						"download_image": obj.actionEnabled("download_grant") ? {
							name:gettext("Download image"),
							icon:"download",
							callback: function(){
								obj.downloadImage();
							}
						} : null,
						"upload_image_file": obj.actionEnabled("upload_grant") ? {
							name:gettext("Upload custom image from disk"),
							icon:"upload_file",
							callback: function(){
								obj.uploadImage_fromFile();
							}
						} : null,
						"upload_image_url": (obj.actionEnabled("upload_grant") && editor.web_resources.executable_archives.length > 0) ? {
							name:gettext("Upload custom image from URL"),
							icon:"upload_url",
							callback: function(){
								obj.uploadImage_byURL();
							}
						} : null,
					}
				} : null,
				"rextfv": obj.actionEnabled("rextfv_download_grant") || obj.actionEnabled("rextfv_upload_grant") || obj.rextfvStatusSupport() ? {
					name:gettext("Executable archive"),
					icon:"rextfv",
					items: {
						"download_rextfv": obj.actionEnabled("rextfv_download_grant") ? {
							name:gettext("Download Archive"),
							icon:"download",
							callback: function(){
								obj.downloadRexTFV();
							}
						} : null,
						"sep2": obj.actionEnabled("rextfv_upload_grant") && obj.actionEnabled("rextfv_download_grant") ? "---" : null,
						"upload_rextfv_file": obj.actionEnabled("rextfv_upload_grant") ? {
							name:gettext("Upload Archive from Disk"),
							icon:"upload_file",
							callback: function(){
								obj.uploadRexTFV_fromFile();
							}
						} : null,
						"upload_rextfv_url": obj.actionEnabled("rextfv_upload_grant") ? {
							name:gettext("Upload Archive from URL"),
							icon:"upload_url",
							callback: function(){
								obj.uploadRexTFV_byURL();
							}
						} : null,
						"upload_rextfv_default": obj.actionEnabled("rextfv_upload_grant") ? {
							name:gettext("Use a Default Archive"),
							icon:"upload_defaultrextfv",
							callback: function(){
								obj.uploadRexTFV_fromDefault();
							}
						} : null,
						"sep2": obj.actionEnabled("rextfv_upload_grant") && obj.rextfvStatusSupport() ? "---" : null,
						"rextfv_status": obj.rextfvStatusSupport() ? {
							name:gettext("Status"),
							icon:"info",
							callback: function(){
								obj.openRexTFVStatusWindow();
							}
						} : null,
					},
				} : null,
				"sep3": "---",
				"configure": {
					name:gettext('Configure'),
					icon:'configure',
					callback:function(){
						obj.showConfigWindow(true);
					}
				},
				"traffic_customize" : obj.trafficAvailable() ? {
					name:gettext("Traffic Customize"),
					icon:"configure",
					callback:function(){
						obj.showTrafficWindow();
					}
				}:null,
				"debug": obj.editor.options.debug_mode ? {
					name:gettext('Debug'),
					icon:'debug',
					callback: function(){
						obj.showDebugInfo();
					}
				} : null,
				"sep4": "---",
				"remove": obj.isRemovable() ? {
					name:gettext('Delete'),
					icon:'remove',
					callback: function(){
						obj.remove(null, true);
					}
				} : null,
				"sep5": "---",
				// "connect to brother topology": {
				// 	name : gettext("link to topgroup"),
				// 	icon : 'remove',
				// 	callback: function(){
				// 		obj.showConnectionWindow()
				// 	},
				// },
			}
		};
	}
	// for topgroup
	var Build_elements = function(name, icon, callback){
		this.name = name
		this.icon = icon
		this.callback = callback
	}

	var Build_tops = function(name, icon, elements){
		this.name = name
		this.icon = icon
		this.items = elements
	}

	var create_connection= function(name){
		var id = name;
		var data = {};
		console.log(obj.id)
		data.elements = [obj.id, id]
		ajax({
			url: "groupconnection/create",
			data: data,
			synchronous: true,
			successFn: function(data) {
				// t.connections[data.id] = obj;
				// obj.updateData(data);
				// t.editor.triggerEvent({component: "connection", object: obj, operation: "create", phase: "end", attrs: data});
				// t.onUpdate();
				// el1.onConnected();
				console.log('success')
				// el2.onConnected();
			},
			errorFn: function(error) {
			 	new errorWindow({error:error});
				// obj.paintRemove();
				// t.editor.triggerEvent({component: "connection", object: obj, operation: "create", phase: "error", attrs: data});
			}
		});
	};

	for (var n = 0; n < topgroup_info.length; n++){
		var elements = {}
		for(var i = 0; i < topgroup_info[n].elements.length; i++){
			elements[topgroup_info[n].elements[i]] = new Build_elements(topgroup_info[n].elements[i], 'configure', create_connection)
		}
		menu.items[topgroup_info[n].name] = new Build_tops(topgroup_info[n].name, 'configure', elements)
	}

	// menu.callback = function(key, options) {}
	
	for (var name in menu.items) {
		if (! menu.items[name]) {
			delete menu.items[name];
			continue;
		}
		var menu2 = menu.items[name];
		if (menu2.items) for (var name2 in menu2.items) if (! menu2.items[name2]) delete menu2.items[name2]; 
	}
	return menu;
};
