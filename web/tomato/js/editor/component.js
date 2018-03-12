
var Component = Class.extend({
	init: function(topology, data, canvas) {
		this.topology = topology;
		this.editor = topology.editor;
		this.setData(data);
		this.canvas = canvas;

		this.trafficWindow = new TrafficWindow({
			autoOpen: false,
    		draggable: true,
    		resizable: false,
    		title:"流量生成配置记录",
    		compoent:this,
    		modal: false,
    		width: 500
		});
	},	
	paint: function() {
	},
	paintUpdate: function() {
	},
	paintRemove: function() {
	},
	setBusy: function(busy) {
		this.busy = busy;
	},
	actionEnabled: function(action) {
		return (action in this.caps.actions) && (! this.caps.actions[action].allowed_states || (this.caps.actions[action].allowed_states.indexOf(this.data.state) >= 0));
	},
	attrEnabled: function(attr) {
	    if (attr[0] == "_") return true;
	    if (!(attr in this.caps.attributes)) return false;
	    var cap = this.caps.attributes[attr];
	    if (cap.read_only) return false;
	    return (!cap.states_writable || cap.states_writable.indexOf(this.data.state) >= 0);
	},
	setData: function(data) {
		this.data = data;
		this.id = data.id;
		this.caps = this.editor.capabilities[this.component_type][this.data.type];
	},
	updateData: function(data) {
		if (data) this.setData(data);
		this.topology.onUpdate();
		this.paintUpdate();
	},
	triggerEvent: function(event) {
		event.component = this.component_type;
		event.object = this;
		this.editor.triggerEvent(event);
	},
	showDebugInfo: function() {
		var t = this;
		ajax({
			url: this.component_type+'/'+this.id+'/info',
		 	data: {},
		 	successFn: function(result) {
		 		var win = new Window({
		 			title: "Debug info",
		 			width: 500,
		 			buttons: {
		 				Close: function() {
		 					win.hide();
		 					win.remove();
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
  		window.open('../'+this.component_type+'/'+this.id+'/usage', '_blank', 'innerHeight=450,innerWidth=650,status=no,toolbar=no,menubar=no,location=no,hotkeys=no,scrollbars=no');
		this.triggerEvent({operation: "usage-dialog"});
	},
	configWindowSettings: function() {
		return {
			order: ["name"],
			ignore: ["id", "parent", "connection", "host_info", "host", "state", "debug", "type", "children", "topology","info_last_sync","info_next_sync", "tech"],
			unknown: true,
			special: {}
		}
	},
	showConfigWindow: function(showTemplate,callback) {
		
		if(showTemplate == null) showTemplate=true;
		
		var absPos = this.getAbsPos();
		var wsPos = this.editor.workspace.container.position();
		var t = this;
		var settings = this.configWindowSettings();
		
		var helpTarget = undefined;
		if ($.inArray(this.data.type,settings.supported_configwindow_help_pages)) {
			helpTarget = this.helpTarget ? this.helpTarget : help_baseUrl;
		}

		
		this.configWindow = new AttributeWindow({
			title: "Attributes",
			width: 600,
			helpTarget:helpTarget,
			buttons: {
				Save: function() {
					t.configWindow.hide();
					var values = t.configWindow.getValues();
					for (var name in values) {
						if (values[name] === t.data[name]) delete values[name];
						// Tread "" like null
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
		for (var i=0; i<settings.order.length; i++) {
			var name = settings.order[i];
			if(showTemplate || !(name == 'template')) {
				if (settings.special[name]) this.configWindow.add(settings.special[name]);
				else if (this.caps.attributes[name]) {
				    var info = this.caps.attributes[name];
				    info.name = name;
				    this.configWindow.autoAdd(info, this.data[name], this.attrEnabled(name));
				}
			}
		}
		if (settings.unknown) {
			for (var name in this.caps.attributes) {
				if (settings.order.indexOf(name) >= 0) continue; //do not repeat ordered fields
				if (settings.ignore.indexOf(name) >= 0) continue;
				if (settings.special[name]) this.configWindow.add(settings.special[name]);
				else if (this.caps.attributes[name]) {
				    var info = this.caps.attributes[name];
				    info.name = name;
				    this.configWindow.autoAdd(info, this.data[name], this.attrEnabled(name));
				}
			}
		}
		this.configWindow.show();
		this.triggerEvent({operation: "attribute-dialog"});
	},
	updateSynchronous: function(fetch, callback, hide_errors) {
		this._update(fetch, callback, hide_errors, true);
	},
	update: function(fetch, callback, hide_errors) {
		this._update(fetch, callback, hide_errors, false);
	},
	_update: function(fetch, callback, hide_errors, synchronous) {
		var t = this;
		this.triggerEvent({operation: "update", phase: "begin"});
		ajax({
			url: this.component_type+'/'+this.id+'/info',
			data: {fetch: fetch},
		 	successFn: function(result) {
		 		t.updateData(result);
				t.triggerEvent({operation: "update", phase: "end"});
				if (callback) callback();
		 	},
		 	errorFn: function(error) {
		 		if (!hide_errors) new errorWindow({error:error});
				t.triggerEvent({operation: "update", phase: "error"});
		 	},
		 	synchronous: synchronous
		});
	},
	updateDependent: function() {
	},
	modify: function(attrs) {
		this.setBusy(true);
		for (var name in attrs) {
			if (this.attrEnabled(name)) this.data[name] = attrs[name];
			else delete attrs[name];
		}
		this.triggerEvent({operation: "modify", phase: "begin", attrs: attrs});
		var t = this;
		ajax({
			url: this.component_type+'/'+this.id+'/modify',
		 	data: attrs,
		 	successFn: function(result) {
		 		t.updateData(result);
		 		t.setBusy(false);
				t.triggerEvent({operation: "modify", phase: "end", attrs: attrs});
		 	},
		 	errorFn: function(error) {
		 		new errorWindow({error:error});
		 		t.update();
		 		t.setBusy(false);
				t.triggerEvent({operation: "modify", phase: "error", attrs: attrs});
		 	}
		});
	},
	modify_value: function(name, value) {
		var attrs = {};
		attrs[name] = value;
		this.modify(attrs);
	},
	action: function(action, options) {
		var options = options || {};
		if ((action=="destroy"||action=="stop") && !options.noask && this.editor.options.safe_mode && ! confirm("Do you want to " + action + " this "+this.component_type+"?")) return;
		this.setBusy(true);
		var params = options.params || {};
		this.triggerEvent({operation: "action", phase: "begin", action: action, params: params});
		var t = this;
		ajax({
			url: this.component_type+'/'+this.id+'/action',
		 	data: {action: action, params: params},
		 	successFn: function(result) {
		 		t.updateData(result[1]);
		 		t.setBusy(false);
		 		if (options.callback) options.callback(t, result[0], result[1]);
				t.triggerEvent({operation: "action", phase: "end", action: action, params: params});
				if (! options.noUpdate) t.updateDependent();
				editor.rextfv_status_updater.add(t, 5000);
		 	},
		 	errorFn: function(error) {
		 		t.onActionError(error);
		 		t.update();
		 		t.setBusy(false);
				t.triggerEvent({operation: "action", phase: "error", action: action, params: params});
				editor.rextfv_status_updater.add(t, 5000);
		 	}
		});
	},
	onConnected: function() {
	},
	onActionError: function(error) {
		if (error.parsedResponse != undefined && error.parsedResponse.error != undefined && error.parsedResponse.error.raw != undefined && error.parsedResponse.error.raw.code != undefined) {
			code = error.parsedResponse.error.raw.code;
			if (code == "timed_out") {
				this.topology.renewDialog();
				return;
			}
		}
		new errorWindow({error:error});
	},
	trafficAvailable:function(){
		var t = this;
		/*if(this.data.type != "openvz"){
			return false
		}*/
		//var settings = this.configWindowSettings();
		//if(settings.special.template.template.customize == "mgen") {
		return true;
		//}
		//return false;
	},
	//add at 2017/1/21   
	showTrafficWindow:function(choice){
		if(choice == 1) {
            this.trafficWindow.createTrafficList();
        }
        else if(choice ==2){
			//todo
			this.showMutilTrafficWindow();
		}
		//this.checkTrafficWindow();
		//this.trafficWindow.createTrafficList();
		//this.trafficWindow.show();
	},

	showMutilTrafficWindow:function(){
		var absPos = this.getAbsPos();
		var wsPos = this.editor.workspace.container.position();
		var t = this;
		mutilTraffic = new AttributeWindow({
			title: "属性配置",
           	width: 500,
           	height: 800,
            	buttons: [
                		{
                   			text: "确定",
                    			click: function () {
                       				var values = mutilTraffic.getValues();
                        			values.dest_element = t.ipToId(values.dest_ip);
                        			var ids = new Array();
                        			elements = t.topology.data.elements;
									for (var i = 0 ; i < elements.length; i++){
											var el = elements[i];
											if (el.tech == "openvz"){
												ids.push(el.id)
											}
									}
                        			console.log(values);
                        			console.log(ids);
                        			//start traffic
                        			ajax({
                            				url: 'topology/mutil_traffic_start',
                            				data: {elements:ids, attrs:values},
                            				successFn: function (data) {
                                			//to
                            				}
                        			});
                        		 mutilTraffic.remove();
                       			 mutilTraffic = null;
                   			 }
                		},
               	 		{
                    			text: "取消",
                    			click: function () {
                        			//remove the window
                        			mutilTraffic.remove();
                        			mutilTraffic = null;
                   			}
               			 }
           	 ],
        	});
		mutilTraffic.add(new TextElement({
			label:"源主机数目",
			name:"number",
			value:""
		}));
		mutilTraffic.add(new TextElement({
			label:"开始时间(s)",
			name:"start_time",
			value:"0"
		}));
		mutilTraffic.add(new TextElement({
			label:"持续时间(s)",
			name:"off_time",
			value:"20.0"
		}));
		mutilTraffic.add(new TextElement({
			label:"目的主机IP",
			name:"dest_ip",
			value:""
			//value:"10.109.241.66"
		}));
		mutilTraffic.add(new TextElement({
			label:"目的主机端口",
			name:"dest_port",
			value:"5002"
		}));
		mutilTraffic.add(new ChoiceElement({
			label:"流量协议",
			name:"protocol",
			choices:{"UDP":"UDP", "TCP":"TCP","ICMP":"ICMP", "SCTP":"SCTP","DNS":"DNS", "Telnet":"Telnet", "VoIP":"VoIP"}
		}));
		var patternChoices = {"PERIODIC":"匀速模式", "POISSON":"泊松模式", "JITTER":"抖动模式", "BRUST":"组合模式"}
		mutilTraffic.add(new ChoiceElement({
			label:"流量模式",
			name:"pattern",
			choices:patternChoices
		}));
		mutilTraffic.add(new TextElement({
			label:"数据包大小(Byte)",
			name:"packet_size",
			value:""
		}));
		mutilTraffic.add(new TextElement({
			label:"数据包速率(个／s)",
			name:"packet_rate",
			value:""
		}));
		mutilTraffic.add(new TextElement({
			label:"服务种类",
			name:"tos",
			value:""
		}));
		mutilTraffic.add(new TextElement({
			label:"TTL",
			name:"ttl",
			value:""
		}));
		mutilTraffic.show();
	},

	showDitgWindow:function(){
		var absPos = this.getAbsPos();
		var wsPos = this.editor.workspace.container.position();
		var t = this;
		this.ditgWindow = new DitgWindow({
            title: "Attributes",
            width: 500,
            buttons: {
                Apply: function () {
                	var values = t.ditgWindow.getValues();
                	values.target_host= t.ipToId(values.target_host);
                	console.log(values);
                    //start traffic
					ajax({
						url:'element/'+t.id+'/ditg_traffic_start',
						data:values,
						successFn:function(data){
							//to
						}
					});
					t.ditgWindow.remove();
					t.ditgWindow = null;
                },
                Cancel: function () {
                    //remove the window
                    t.ditgWindow.remove();
                    t.ditgWindow = null;
                }
            }
        },
        this);
		this.ditgWindow.show();
	},
	ipToId:function(ip){ //change the input ip to element's id
		for(var i = 0 ; i < this.topology.data.elements.length; i++){
			var order = this.topology.data.elements[i].data;
			if(order.tech == "openvz_interface"){
				if(order.ip4address == ip||order.ip4address == (ip+"/24")||order.ip4address == (ip+"/22")){
					return order.parent;
				}
			}
		}
		alert("Not available target host!");
	}
});
