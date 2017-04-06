var MenuTab = Class.extend({
	init: function(name) {
		// this.name = name;
		switch(name){
			case("主页"):
			this.name = "Home"
			break;
			case("设备"):
			this.name = "Devices"
			break;
			case("网络"):
			this.name = "Network"
			break;
			case('拓扑'):
			this.name = "Topology"
			break;
			case("选项"):
			this.name = "Options"
			break;
			default:
			this.name = name
		}
		console.log(this.name);
		this.div = $('<div id="menu_tab_'+this.name+'"></div>');
		this.link = $('<li><a href="'+window.location+'#menu_tab_'+this.name+'"><span><label>'+name+'</label></span></a></li>');
		this.panel = $('<ul></ul>');
		this.div.append(this.panel);
		this.groups = {};
	},
	addGroup: function(name) {
		var group = new MenuGroup(name);
		this.groups[name] = group;
		this.panel.append(group.container);
		return group;
	},
	getGroup: function(name) {
		return this.groups[name];
	}
});
