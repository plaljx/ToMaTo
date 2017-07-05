var SubtopologyMenu = Class.extend({
	init: function(name){
		this.div = $('#subtopology_tab');
		// this.link = $('<li><a href="'+window.location+'#menu_tab_'+this.name+'"><span><label>'+name+'</label></span></a></li>');
		this.panel = $('<ul></ul>');
		this.div.append(this.panel);
		this.groups = {};
	},
	addButton: function(options){

	},

})