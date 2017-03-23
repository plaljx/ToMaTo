
var createTopologyMenu = function(obj) {
	var menu = {
		callback: function(key, options) {},
		items: {
			"header": {
				html:"<span>"+obj.name()+"<small><br />Topology "+(editor.options.show_ids ? ' ['+obj.id+']' : "")+'</small></span>',
				type:"html"
			},
			"actions": {
				name:gettext('Global actions'),
				icon:'control',
				items: {
					"start": {
						name:gettext('Start'),
						icon:'start',
						callback: function(){
							obj.action_start();
						}
					},
					"stop": {
						name:gettext("Stop"),
						icon:"stop",
						callback: function(){
							obj.action_stop();
						}
					},
					"prepare": {
						name:gettext("Prepare"),
						icon:"prepare",
						callback: function(){
							obj.action_prepare();
						}
					},
					"destroy": {
						name:gettext("Destroy"),
						icon:"destroy",
						callback:function(){
							obj.action_destroy();
						}
					}
				}
			},
			"sep1": "---",
			"tabbedConsoleWindow": {
				name:gettext("Tabbed Console (NoVNC)"),
				icon:"console",
				callback: function() {
					obj.tabbedConsoleWindow();
				}
			},
			"notes": {
				name:gettext("Notes"),
				icon:"notes",
				callback: function(){
					obj.notesDialog();
				}
			},
			"usage": {
				name:gettext("Resource usage"),
				icon:"usage",
				callback: function(){
					obj.showUsage();
				}
			},
			"sep2": "---",
			"configure": {
				name:gettext('Configure'),
				icon:'configure',
				callback: function(){
					obj.showConfigWindow();
				}
			},
			"debug": obj.editor.options.debug_mode ? {
				name:gettext('Debug'),
				icon:'debug',
				callback: function(){
					obj.showDebugInfo();
				}
			} : null,
			"sep3": "---",
			"remove": {
				name:gettext('Delete'),
				icon:'remove',
				callback: function(){
					obj.remove();
				}
			}
		}
	};	
	for (var name in menu.items) {
		if (! menu.items[name]) delete menu.items[name]; 
	}
	return menu;
};
