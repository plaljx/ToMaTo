/********************************************************************************
 * Browser quirks:
 * - IE8 does not like a komma after the last function in a class
 * - IE8 does not like colors defined as words, so only traditional colors
 ********************************************************************************/ 

var NetElement = Class.extend({
  init: function(editor){
    this.editor = editor;
  },
  paint: function(){
  },
  paintUpdate: function(){
  },
  getX: function() {
    return this.getPos().x;
  },
  getY: function() {
    return this.getPos().y;
  }
});

var IconElement = NetElement.extend({
  init: function(editor, name, iconsrc, iconsize, pos) {
    this._super(editor);
    this.name = name;
    this.iconsrc = iconsrc;
    this.iconsize = iconsize;
    this.pos = pos;
    this.paletteItem = false;
  },
  paint: function(){
    this._super();
    if (this.text) this.text.remove();
    this.text = this.editor.g.text(this.pos.x, this.pos.y+this.iconsize.y/2+5, this.name);
    if (this.icon) this.icon.remove();
    this.icon = this.editor.g.image(this.iconsrc, this.pos.x-this.iconsize.x/2, this.pos.y-this.iconsize.y/2, this.iconsize.x, this.iconsize.y);
    this.icon.parent = this;
    this.icon.drag(function (dx, dy) {
      //move
      if (this.parent.paletteItem) this.shadow.attr({x: this.opos.x + dx-this.parent.iconsize.x/2, y: this.opos.y + dy-this.parent.iconsize.y/2});
      else this.parent.move({x: this.opos.x + dx, y: this.opos.y + dy});
    }, function () {
      //start
      this.opos = this.parent.pos;
      if (this.parent.paletteItem) this.shadow = this.clone().attr({opacity:0.5});
    }, function () {
      //stop
      if (this.parent.paletteItem) {
	element = this.parent.createAnother({x: this.shadow.attr("x")+this.parent.iconsize.x/2, y: this.shadow.attr("y")+this.parent.iconsize.y/2});
        this.shadow.remove();
      }
      if (this.parent.pos != this.opos) this.parent.lastMoved = new Date();
    });
    this.icon.click(function(event){
      this.parent.onclick();
    });
  },
  paintUpdate: function() {
    this._super();
    this.icon.attr({x: this.pos.x-this.iconsize.x/2, y: this.pos.y-this.iconsize.y/2});
    this.text.attr({x: this.pos.x, y: this.pos.y+this.iconsize.y/2+5});
  },
  move: function(pos) {
    if (pos.x + this.iconsize.x/2 > this.editor.g.width) pos.x = this.editor.g.width - this.iconsize.x/2;
    if (pos.y + this.iconsize.y/2 + 10 > this.editor.g.height) pos.y = this.editor.g.height - this.iconsize.y/2 - 10;
    if (pos.x - this.iconsize.x/2 < this.editor.paletteWidth) pos.x = this.editor.paletteWidth + this.iconsize.x/2;
    if (pos.y - this.iconsize.y/2 < 0) pos.y = this.iconsize.y/2;
    this.pos = pos;
    this.paintUpdate();
  },
  getPos: function() {
    return this.pos;
  },
  createAnother: function(pos) {
  },
  onclick: function() {
    if (this.lastMoved && this.lastMoved.getTime() + 1 > new Date().getTime()) return;
    alert(this.name+" clicked");
  }
});

var Connection = NetElement.extend({
  init: function(editor, con, dev) {
    this._super(editor);
    this.con = con;
    this.dev = dev;
    this.paint();
  },
  getPos: function(){
    return {x: (this.con.getX()+this.dev.getX())/2, y: (this.con.getY()+this.dev.getY())/2};
  },
  getPath: function(){
    return "M"+this.con.getX()+" "+this.con.getY()+"L"+this.dev.getX()+" "+this.dev.getY();
  },
  paintUpdate: function(){
    this._super();
    this.path.attr({path: this.getPath()});
    this.handle.attr({x: this.getX()-8, y: this.getY()-8});
  },
  paint: function(){
    this._super();
    if (this.path) this.path.remove();
    this.path = this.editor.g.path(this.getPath());
    this.path.toBack();
    if (this.handle) this.handle.remove();
    this.handle = this.editor.g.rect(this.getX()-8, this.getY()-8, 16, 16).attr({fill: "#A0A0A0"});
    this.handle.parent = this;
    this.handle.click(function(event){
      this.parent.onclick();
    });
  },
  onclick: function() {
    alert(this.con.name+"<->"+this.dev.name+" clicked");
  }
});

var Interface = NetElement.extend({
  init: function(editor, dev, con){
    this._super(editor);
    this.dev = dev;
    this.con = con;
    this.paint();
  },
  getPos: function() {
    xd = this.con.getX() - this.dev.getX();
    yd = this.con.getY() - this.dev.getY();
    magSquared = (xd * xd + yd * yd);
    mag = 14.0 / Math.sqrt(magSquared);
    return {x: this.dev.getX() + (xd * mag), y: this.dev.getY() + (yd * mag)};
  },
  paint: function(){
    if (this.circle) this.circle.remove();
    this.circle = this.editor.g.circle(this.getX(), this.getY(), 8).attr({fill: "#CDCDB3"});
    this.circle.parent = this;
    this.circle.click(function(event){
      this.parent.onclick();
    });
  },
  paintUpdate: function(){
    this._super();
    this.circle.attr({cx: this.getX(), cy: this.getY()});
  },
  onclick: function() {
    //alert("Interface of "+this.dev.name+" clicked");
    this.showAttributes();
  },
  showAttributes: function() {
    alert("Interface of " + this.dev.name + " clicked");
    //this.editor.disable();
  }
});

var Connector = IconElement.extend({
  init: function(editor, name, iconsrc, iconsize, pos) {
    this._super(editor, name, iconsrc, iconsize, pos);
    this.connections = [];
    this.paint();
  },
  move: function(pos) {
    this._super(pos);
    for (var i in this.connections) {
      this.connections[i].paintUpdate();
      this.connections[i].dev.paintUpdateInterfaces();
    }    
  },
  addConnection: function(con) {
    this.connections.push(con);
  }
});

var HubConnector = Connector.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/hub.png", {x: 32, y: 16}, pos);
  },
  createAnother: function(pos) {
    return new HubConnector(this.editor, "hub", pos);
  }
});

var SwitchConnector = Connector.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/switch.png", {x: 32, y: 16}, pos);
  },
  createAnother: function(pos) {
    return new SwitchConnector(this.editor, "switch", pos);
  }
});

var RouterConnector = Connector.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/router.png", {x: 32, y: 16}, pos);
  },
  createAnother: function(pos) {
    return new RouterConnector(this.editor, "router", pos);
  }
});


var Device = IconElement.extend({
  init: function(editor, name, iconsrc, iconsize, pos) {
    this._super(editor, name, iconsrc, iconsize, pos);
    this.interfaces = [];
    this.paint();
  },
  move: function(pos) {
    this._super(pos);
    for (var i in this.interfaces) this.interfaces[i].con.paintUpdate();
    this.paintUpdateInterfaces();   
  },
  paint: function() {
    this._super();
    for (var i in this.interfaces) this.interfaces[i].paint();    
  },
  paintUpdateInterfaces: function() {
    for (var i in this.interfaces) this.interfaces[i].paintUpdate();
  },
  addInterface: function(iface) {
    this.interfaces.push(iface);
  }
});

var OpenVZDevice = Device.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/computer.png", {x: 32, y: 32}, pos);
  },
  createAnother: function(pos) {
    return new OpenVZDevice(this.editor, "openvz", pos);
  }
});

var KVMDevice = Device.extend({
  init: function(editor, name, pos) {
    this._super(editor, name, "images/pc_green.png", {x: 32, y: 32}, pos);
  },
  createAnother: function(pos) {
    return new KVMDevice(this.editor, "kvm", pos);
  }
});

var Editor = Class.extend({
  init: function(size) {
    this.g = Raphael("editor", size.x, size.y);
    this.size = size;
    this.paletteWidth = 100;
    this.glabColor = "#911A20";
    this.paintPalette();
  },
  paintPalette: function() {
    this.g.path("M"+this.paletteWidth+" 0L"+this.paletteWidth+" "+this.g.height).attr({"stroke-width": 2, stroke: this.glabColor});
    this.openVZPrototype = new OpenVZDevice(this, "OpenVZ", {x: this.paletteWidth/2, y: 50});
    this.openVZPrototype.paletteItem = true;
    this.kvmPrototype = new KVMDevice(this, "KVM", {x: this.paletteWidth/2, y: 100});
    this.kvmPrototype.paletteItem = true;
    this.hubPrototype = new HubConnector(this, "Hub", {x: this.paletteWidth/2, y: 200});
    this.hubPrototype.paletteItem = true;
    this.switchPrototype = new SwitchConnector(this, "Switch", {x: this.paletteWidth/2, y: 250});
    this.switchPrototype.paletteItem = true;
    this.routerPrototype = new RouterConnector(this, "Router", {x: this.paletteWidth/2, y: 300});
    this.routerPrototype.paletteItem = true;
  },
  connect: function(connector, device) {
    con = new Connection(editor, connector, device);
    connector.addConnection(con);
    iface = new Interface(editor, device, con);
    device.addInterface(iface);
  },
  disable: function() {
    this.disableRect = this.g.rect(0, 0, this.size.x,this.size.y).attr({fill:"#FFFFFF", opacity:.8});
  },
  enable: function() {
    if (this.disableRect) this.disableRect.remove();
  }
});