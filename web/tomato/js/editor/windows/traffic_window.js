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
		ajax({
	 		url:'element/'+t.compoent.id+'/traffic_list',
	 		//async :false,
	 		successFn:function(data){
	 			res = data;
	 			
	 		}
	 	});
	 	this.traffics = res;
	},
	createTrafficList:function(){
		var t = this ;
		ajax({
	 		url:'element/'+t.compoent.id+'/traffic_list',
	 		successFn:function(data){
	 			var res = data ;
	 			for(var i = 0 ; i < res.length ; i++){
	 				t.traffics[res[i].traffic_name] = res[i];
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
		var tableHeader = $('<div class="row"><div class="col-sm-1" /><div class="col-sm-5"><h4>Name</h4></div><div class="col-sm-3"><h4>Destination IP</h4></div><div class="col-sm-3" /></div>');
		this.trafficTable.append(tableHeader); 
		this.trafficList.empty();
		this.trafficList.append(this.trafficTable);

		var perm = this.traffics;
		for(u in perm){
			this.addTrafficToList(u);
		}
	},
	addTrafficToList:function(trafficname){
		var t = this;
		var tr = $('<div class="row" />');
		var td_name = $('<div class="col-sm-5" />');
		var td_perm = $('<div class="col-sm-3" />');
		var td_buttons = $('<div class="col-sm-3" />');
		var td_icon = $('<div class="col-sm-1" />');

		tr.append(td_icon);
		tr.append(td_name);
		tr.append(td_perm);
		tr.append(td_buttons);

		this.trafficListFinder[trafficname] = {
				td_icon: td_icon,
				td_name: td_name,
				td_perm: td_perm,
				td_buttons: td_buttons,
				tr: tr
		};
		this.trafficTable.append(tr);
		this.drawView(trafficname);
	
	},
	drawView:function(trafficname){
		var t = this;
		var dest_ip = '<div class="hoverdescription">'+this.traffics[trafficname].dest_ip+'</div>';//show the destination ip address of the traffic
		var td_perm = this.trafficListFinder[trafficname].td_perm;
		var td_buttons = this.trafficListFinder[trafficname].td_buttons;
		var td_name = this.trafficListFinder[trafficname].td_name;

		td_perm.empty();
		td_buttons.empty();
		td_name.append(trafficname);
		td_perm.append(dest_ip);
		var editButton = $('<img src="/img/pencil.png" title="modify traffic" style="cursor:pointer;" />');
		editButton.click(function(){
				//todo
				t.modifyTraffic(trafficname);
			});
		td_buttons.append(editButton);
		var removeButton = $('<img src="/img/cross.png" title="remove from list" style="cursor:pointer;" />');
		removeButton.click(function(){
				//todo
				t.removeTraffic(trafficname);
			})
		td_buttons.append(removeButton);
	},
	modifyTraffic:function(trafficname){
		var t = this;
		t.addNewTraffic();
	},
	removeTraffic:function(trafficname){
		this.trafficListFinder[trafficname].tr.remove();
		ajax({
			url:'element/'+this.traffics[trafficname].id+'/traffic_remove',
			successFn:function(data){
				//todo
			}
		});
		delete this.traffics[trafficname];
		delete this.userListFinder[trafficname];  
	},

	addNewTraffic:function(){
		var t = this;
		var traffic;
		traffic = new AttributeWindow({
			title:"Attributes",
			width: 500,
			height: 700,
            buttons: [
						{ 
							text:"Save",
							click: function() {
								var values =  traffic.getValues();
								if(t.traffics[values.traffic_name]){
									alert("The name of traffic is existing,please change the name!");
								}
								else{
								ajax({
									url:'element/'+t.compoent.id+'/traffic_create',
									data:values,
									successFn:function(data){
										t.traffics[data.traffic_name] = data;
										t.addTrafficToList(data.traffic_name);
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
			label:"Off time",
			name:"off_time",
			value:"10.0"
		}));

		var choices = {"10.109.241.100":"10.109.241.100","10.109.241.66":"10.109.241.100"};
		traffic.add(new ChoiceElement({
			label:"Dstination IP",
			name:"dest_ip",
			choices: choices
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
			choices:{"TCP":"TCP" , "UDP":"UDP"}
		}));
		traffic.add(new TextElement({
			label:"Pattern",
			name:"pattern",
			value:"PERIODIC [1 1024]"
		}));
		traffic.show();
	}
});