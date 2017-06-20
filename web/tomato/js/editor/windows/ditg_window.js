var DitgWindow = AttributeWindow.extend({
	init: function(options,component) {
		this._super(options);

		var panels = $('<ul class="nav nav-tabs" style="margin-bottom: 1pt;"></ul>');
		this.table.append($('<div class="form-group" />').append(panels));

		var tab_content = $('<div class="tab-content" />');
        var t = this;
        var common_setting = $('<div class="tab-pane active" id="Common_Setting" />');
        //simple fields
        var order = ["Duration", "Start Delay","Target Host" , "TTL","Protocol", "Destination Port", "Source Port",
					  "Packets Per Sec", "Packet's Size"];
        for (var i = 0; i < order.length; i++) {
        	var el = new TextElement({label: order[i], name: order[i], value: ""});
        	if(order[i] == "Duration"){
        		el.name = "duration";
			}
			else if(order[i] == "Start Delay"){
        		el.name = "start_delay";
			}
            else if(order[i] == "Target Host"){
            	el.name = "target_host";
			}
			else if(order[i] == "TTL"){
            	el.name = "ttl";
			}
			else if(order[i] == "Protocol"){
				var choices = {"UDP":"UDP", "TCP":"TCP","ICMP":"ICMP","SCTP":"SCTP"};
				el = new ChoiceElement({label:"Protocol",name:"protocol",choices:choices});
			}
			else if(order[i] == "Destination Port"){
				el.name = "destination_port";
			}
			else if(order[i] == "Source Port"){
				el.name ="source_port";
			}
			else if(order[i] == "Packets Per Sec"){
				el.name = "pps";
            }
            else if(order[i] == "Packet's Size"){
				el.name = "packet_size";
			}
            this.elements.push(el)
            common_setting.append($('<div class="form-group" />')
					.append($('<label class="col-sm-4 control-label" style="padding: 0;" />').append(el.label))
					.append($('<div class="col-sm-6" style="padding: 0;" />').append(el.getElement()))
				);
        }

        tab_content.append(common_setting);
        this.table.append(tab_content);
        panels.append($('<li class="active"><a href="#Common_Setting" data-toggle="tab">Common Setting</a></li>'));



		var dns_setting = $('<div class="tab-pane" id="DNS_Setting" />');
		var el = new CheckboxElement({
				name: "dns_enable",
				value: false
			});
		this.elements.push(el);
		dns_setting.append($('<div class="form-group" />')
					.append($('<label class="col-sm-4 control-label">Enabled</label>'))
					.append($('<div class="col-sm-6" />')
					.append(el.getElement())));

		var order = ["Time Option", "Number", "Size Option", "Size"];
		for (var i = 0; i < order.length; i++) {
			var el = new TextElement({label:order[i],name:order[i],value:""});
			if(order[i] == "Time Option"){
				el.name = "time_option";
			}
			else if(order[i] == "Number"){
				el.name = "number";
			}
			else if(order[i] == "Size Option"){
				el.name = "size_option"
			}
			else if(order[i] == "Size"){
				el.name = "size";
			}
			this.elements.push(el);
			dns_setting.append($('<div class="form-group" />')
					.append($('<label class="col-sm-4 control-label">').append(el.label))
					.append($('<div class="col-sm-6" />').append(el.getElement()))
				);
		}
		tab_content.append(dns_setting);
		this.table.append(tab_content);
		panels.append($('<li><a href="#DNS_Setting" data-toggle="tab">DNS Setting</a></li>'));

		var game_setting= $('<div class="tab-pane" id="Game_Setting" />');
		var el = new CheckboxElement({
				name: "game_enable",
				value: false
			});
		this.elements.push(el);
		game_setting.append($('<div class="form-group" />')
					.append($('<label class="col-sm-4 control-label">Enabled</label>'))
					.append($('<div class="col-sm-6" />')
					.append(el.getElement())));

		var el = new TextElement({label:"Game Pattern",name:"game_pattern",value:"" });
		this.elements.push(el);
		game_setting.append($('<div class="form-group" />')
					.append($('<label class="col-sm-4 control-label">').append(el.label))
					.append($('<div class="col-sm-6" />').append(el.getElement()))
					);
		tab_content.append(game_setting);
		this.table.append(tab_content);
		panels.append($('<li><a href="#Game_Setting" data-toggle="tab">Game Setting</a></li>'));
	}
});
