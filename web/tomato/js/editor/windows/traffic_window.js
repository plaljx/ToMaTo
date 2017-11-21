var TrafficWindow = Window.extend({
	init:function(options){
		var t = this;
		this.options = options;
		this.compoent = options.compoent;
		this.traffics = {};

		var closebutton = {
			text:"Close",
			id:"trawindow-close-button",
			click:function(){
				t.remove();
			}
		};
		var addbutton = {
			text:"Add Traffic",
			id:"trawindow-add-button",
			click:function(){
				t.addNewTraffic();
			}
		};
		var startbutton = {
			text:"Start Selected",
			id:"trawindow-start-button",
			click:function(){
				t.startSelected();
				//todo
			}
		};

		this.options.buttons = [closebutton,addbutton,startbutton];
		this._super(this.options);

		this.trafficList = $('<div />');
		this.trafficListFinder = {};
		this.div.append(this.trafficList);

		this.buttons = $('<div />');
		this.div.append(this.buttons);

		this.closebutton = $("#trawindow-close-button");
		this.addbutton = $("#trawindow-add-button");
		this.startbutton = $("#trawindow-start-button");

	},
	getTraffics:function(){
		var t = this;
		var res = [];
		topology_id = this.compoent.topology.id
		ajax({
	 		url:'topology/'+topology_id+'/traffic_list',
	 		//async :false,
	 		successFn:function(data){
	 			res = data;

	 		}
	 	});
	 	this.traffics = res;
	},
	startSelected:function(){
		var t = this;
		var selected = new Array();
		for(var temp in this.traffics){
			if(this.traffics[temp].state == "selected"){
				selected.push(temp);
			}
		}
		ajax({
			url:'topology/traffic_start',
			data:{selected:selected},
			successFn:function(data){
				//todo
			},
			errorFn:function(error){
				new errorWindow({error:error});
			}
		});
	},
	createTrafficList:function(){
		var t = this ;
		topology_id = this.compoent.topology.id
		ajax({
	 		url:'topology/'+topology_id+'/traffic_list',
	 		successFn:function(data){
	 			var res = data ;
	 			for(var i = 0 ; i < res.length ; i++){
	 				t.traffics[res[i].id] = res[i];
	 				t.traffics[res[i].id].state = "unselected";
	 			}
	 			t.createTrafficListTwo();
	 			t.show();
			},
			errorFn: function(error) {
				new errorWindow({error:error});
			}
	 	});
	},
	createTrafficListTwo:function(){
		var t = this;
		this.trafficTable =  $('<div />');
		var tableHeader = $('<div class="row"><div class="col-sm-1" /><div class="col-sm-5"><h4>Name</h4></div><div class="col-sm-3"><h4>Source IP</h4></div><div class="col-sm-3"><h4>Destination IP</h4></div><div class="col-sm-3" /></div>');
		this.trafficTable.append(tableHeader);
		this.trafficList.empty();
		this.trafficList.append(this.trafficTable);

		for(var u in this.traffics){
			this.addTrafficToList(u);
		}
	},
	addTrafficToList:function(trafficId){
		var t = this;
		var tr = $('<div class="row" />');
		var td_name = $('<div class="col-sm-5" />');
		var td_source = $('<div class="col-sm-3" />');
		var td_perm = $('<div class="col-sm-3" />');
		var td_buttons = $('<div class="col-sm-3" />');
		var td_icon = $('<div class="col-sm-1" />');

		tr.append(td_icon);
		tr.append(td_name);
		tr.append(td_source);
		tr.append(td_perm);
		tr.append(td_buttons);

		this.trafficListFinder[trafficId] = {
				td_icon: td_icon,
				td_name: td_name,
				td_source: td_source,
				td_perm: td_perm,
				td_buttons: td_buttons,
				tr: tr
		};
		this.trafficTable.append(tr);
		this.drawView(trafficId);

	},
	drawView:function(trafficId){
		var t = this;
		var dest_ip = '<div class="hoverdescription">'+this.traffics[trafficId].dest_ip+'</div>';//show the destination ip address of the traffic
		var td_source = this.trafficListFinder[trafficId].td_source
		var td_perm = this.trafficListFinder[trafficId].td_perm;
		var td_buttons = this.trafficListFinder[trafficId].td_buttons;
		var td_name = this.trafficListFinder[trafficId].td_name;

		td_perm.empty();;
		td_source.empty()
		td_buttons.empty();
		td_name.append(this.traffics[trafficId].traffic_name);
		td_source.append(this.traffics[trafficId].source_ip);
		td_perm.append(dest_ip);
		var editButton = $('<img src="/img/pencil.png" title="modify the traffic" style="cursor:pointer;" />');
		editButton.click(function(){
				//todo
				t.modifyTraffic(trafficId);
			});
		td_buttons.append(editButton);
		var removeButton = $('<img src="/img/cross.png" title="remove from list" style="cursor:pointer;" />');
		removeButton.click(function(){
				//todo
				t.removeTraffic(trafficId);
			});
		td_buttons.append(removeButton);

		var selectButton = $('<img src="/img/select.png" title="select the traffic"  style="cursor:pointer;" />');
		selectButton.click(function(){
			//changebutton
			t.changeButton(trafficId);
		});
		td_buttons.append(selectButton);
	},
	changeButton:function(trafficId){
		var t = this;
		var td_buttons = this.trafficListFinder[trafficId].td_buttons;
		td_buttons.empty();
		var editButton = $('<img src="/img/pencil.png" title="modify the traffic" style="cursor:pointer;" />');
		editButton.click(function(){
				//todo
				t.modifyTraffic(trafficId);
			});
		td_buttons.append(editButton);
		var removeButton = $('<img src="/img/cross.png" title="remove from list" style="cursor:pointer;" />');
		removeButton.click(function(){
				//todo
				t.removeTraffic(trafficId);
			});
		td_buttons.append(removeButton);

		if (t.traffics[trafficId].state == "unselected") {
			t.traffics[trafficId].state = "selected";
			var unselectButton = $('<img src="/img/unselect.png" title="unselect the traffic"  style="cursor:pointer;" />');
			unselectButton.click(function(){
				//changebutton
				t.changeButton(trafficId);
			});
			td_buttons.append(unselectButton);
		}
		else{
			t.traffics[trafficId].state ="unselected";
			var selectButton = $('<img src="/img/select.png" title="select the traffic"  style="cursor:pointer;" />');
			selectButton.click(function(){
			//changebutton
				t.changeButton(trafficId);
			});
			td_buttons.append(selectButton);
		}
	},
	modifyTraffic:function(trafficId){
		var t = this;
		var modifyWindow;
		modifyWindow = new AttributeWindow({
			title :"Attributes",
			width:500,
			height:800,
			buttons:[{
				text:"Modify",
				click:function(){
					//todo:modify
					modifyWindow.remove();
					}
				},
				{
					text:"Close",
					click:function(){
						modifyWindow.remove();
					}
				}
			],

		});
		modifyWindow.add(new TextElement({
			label:"Start time",
			name:"start_time",
			value:this.traffics[trafficId].start_time
		}));
		modifyWindow.add(new TextElement({
			label:"Off time",
			name:"off_time",
			value:this.traffics[trafficId].off_time
		}));
		modifyWindow.add(new TextElement({
			label:"Source ip",
			name:"source_ip",
			value:this.traffics[trafficId].source_ip
		}));
		modifyWindow.add(new TextElement({
			label:"Source port",
			name:"src_port",
			value:this.traffics[trafficId].src_port
		}));
		modifyWindow.add(new TextElement({
			label:"Destination IP",
			name:"dest_ip",
			value:this.traffics[trafficId].dest_ip
		}));
		modifyWindow.add(new TextElement({
			label:"Destination Port",
			name:"dest_port",
			value:this.traffics[trafficId].dest_port
		}));
		modifyWindow.add(new TextElement({
			label:"Type of Server",
			name:"tos",
			value:this.traffics[trafficId].tos
		}));
		var protocolChoices = {"TCP":"TCP", "UDP":"UDP"};
		modifyWindow.add(new ChoiceElement({
			label:"Protocal",
			name:"protocol",
			choices:protocolChoices
		}));
		var patternChoices = {"PERIODIC [1.0 125]":"1kbps" , "PERIODIC [10.0 125]":"10kbps",
		"PERIODIC [10.0 1250]":"100kbps" ,"PERIODIC [50.0 1280]":"512kbps",
		"POISSON [10.0 125]":"POISSON 10 kbps","POISSON [10.0 1250]":"POISSON 100 kbps",
		"JITTER [10.0 125 0.5]":"JITTER 10kbps 0.05-0.15s"};
		modifyWindow.add(new ChoiceElement({
			label:"Pattern",
			name:"pattern",
			choices:patternChoices
		}));
		modifyWindow.add(new TextElement({
			label:"Extra Param",
			name:"extra_param",
			value:this.traffics[trafficId].extra_param
		}));
		modifyWindow.show();
	},
	removeTraffic:function(trafficId){
		this.trafficListFinder[trafficId].tr.remove();
		ajax({
			url:'topology/'+this.traffics[trafficId].id+'/traffic_remove',
			successFn:function(data){
				//todo
			}
		});
		delete this.traffics[trafficId];
		delete this.userListFinder[trafficId];
	},
	addNewTraffic:function(){
		var t = this;
		var traffic;
		topology_id = this.compoent.topology.id
		traffic = new AttributeWindow({
			title:"Attributes",
			width: 500,
			height: 800,
            buttons: [
						{
							text:"Save",
							click: function() {
								var values =  traffic.getValues();
								values.element_id = t.compoent.ipToId(values.source_ip)
								if(t.traffics[values.traffic_name]){
									alert("The name of traffic is existing,please change the name!");
								}
								else{
								ajax({
									url:'topology/'+topology_id+'/traffic_create',
									data:values,
									successFn:function(data){
										t.traffics[data.id] = data;
										t.traffics[data.id].state ="unselected";
										t.addTrafficToList(data.id);
									}
								});
								traffic.remove();
							}}
						},
						{
							text:"Close",
							click: function() {
								traffic.remove();
							}
						}
					],


		});
		traffic.add(new TextElement({
			label:"Name",
			name:"traffic_name",
			value:"instance"
		}));
		traffic.add(new TextElement({
			label:"Start time",
			name:"start_time",
			value:"0"
		}));
		traffic.add(new TextElement({
			label:"Off time",
			name:"off_time",
			value:"20.0"
		}));
		traffic.add(new TextElement({
			label:"Source IP",
			name:"source_ip",
			value:""
		}));
		traffic.add(new TextElement({
			label:"Source port",
			name:"src_port",
			value:"5001"
		}));
		traffic.add(new TextElement({
			label:"Destination IP",
			name:"dest_ip",
			value:""
			//value:"10.109.241.66"
		}));
		traffic.add(new TextElement({
			label:"Destination Port",
			name:"dest_port",
			value:"5001"
		}));
		traffic.add(new ChoiceElement({
			label:"Protocal",
			name:"protocol",
			choices:{"UDP":"UDP" , "TCP":"TCP","SINK":"SINK"}
		}));
		traffic.add(new TextElement({
			label:"Type of Server",
			name:"tos",
			value:"0"
		}));
		var patternChoices = {"PERIODIC [1.0 125]":"1kbps" , "PERIODIC [10.0 125]":"10kbps",
		"PERIODIC [10.0 1250]":"100kbps" ,"PERIODIC [50.0 1280]":"512kbps",
		"POISSON [10.0 125]":"POISSON 10 kbps","POISSON [10.0 1250]":"POISSON 100 kbps",
		"JITTER [10.0 125 0.5]":"JITTER 10kbps 0.05-0.15s"};
		traffic.add(new ChoiceElement({
			label:"Pattern",
			name:"pattern",
			choices:patternChoices
		}));
		traffic.add(new TextElement({
			label:"Extra Param",
			name:"extra_param",
			value:""
		}));
		traffic.show();
	}
});