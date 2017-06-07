var GroupWindow = Window.extend({

    init: function (options) {

        options.modal = true;
        options.close_keep = true;

        var t = this;
        this.options = options;
        this.topology = options.topology;

        this.options.allowChange = this.options.isGlobalOwner;

        var closeButton = {
            text: "Close",
            id: "groupwindow-close-button",
            click: function () {
                t.hide();
            }
        };
        var addButton = {
            text: "Add Group",
            id: "groupwindow-add-button",
            click: function () {
                t.addNewGroup();
            }
        };

        this.options.buttons = [closeButton, addButton];

        this._super(this.options);

        this.groupList = $('<div />');
        this.groupListFinder = {};
        this.div.append(this.groupList);

        this.buttons = $('<div />');
        this.div.append(this.buttons);

        this.closeButton = $("#groupwindow-close-button");
        this.addButton = $("#groupwindow-add-button");
    },

    // show a new group dialog, which contains a group name label and buttons
    addNewGroup: function () {
        var t = this;
        this.groupName = new InputWindow({
            title: "New Group",
            width: 550,
            height: 200,
            zIndex: 1000,
            inputname: "newgroup",
            inputlabel: "Group:",
            infotext: "Please enter the group's name:",
            inputvalue: "",
            buttons: [
                {
                    text: "Add Group",
                    click: function() {
                        t.groupName.hide();
                        if (t.groupName.element.getValue() !== '')
                            ajax({
                                url:	'group/' + t.groupName.element.getValue() + '/info',
                                successFn: function(data) {
                                    if (!(data.name in t.groupListFinder)) {
                                        if (window.confirm("Found the group: \n\tName:"
                                                + data.name + '\n\tLabel:' + data.label
                                                + "\nIs this correct?"))
                                        {
                                            t.addGroupToList(data.name);
                                            t.addGroup(data.name);
                                        }
                                    }
                                    else {
                                        showError("This group is already in the list.");
                                    }
                                },
                                errorFn: function(error) {
                                    new errorWindow({error:error});
                                },
                            });
                        t.groupName = null;
                    }
                },
                {
                    text: "Cancel",
                    click: function() {
                        t.groupName.hide();
                        t.groupName = null;
                    }
                }
            ],
        });
        this.groupName.show();
    },

    createGroupList: function () {
        var t = this;

        if (!this.options.allowChange) {
            this.options.allowChange = (this.topology.data.permissions[this.options.ownUserId] === "owner");
        }
        if (!this.options.allowChange) {
            this.addButton.attr("disabled",true);
        }

        this.groupTable = $('<div />');
        var tableHeader = $(
            '<div class="row">' +
            // '   <div class="col-sm-1" />' +
            '   <div class="col-sm-5"><h4>Group</h4></div>' +
            '   <div class="col-sm-3"><h4>Edit</h4><div/>' +
            '</div>');
        this.groupTable.append(tableHeader);
        this.groupList.empty();
        this.groupList.append(this.groupTable);

        var groupInfo = this.topology.data.group_info; // groupInfo is an Array here
        for (var i=0; i<groupInfo.length; i++) {
            this.addGroupToList(groupInfo[i]);
        }
    },

    addGroupToList: function (groupName) {
        var t = this;
        var tr = $('<div class="row" />');
        var td_name = $('<div class="col-sm-5" />');
        var td_buttons = $('<div class="col-sm-3" />');

        ajax({
            url:	'group/'+groupName+'/info',
            successFn: function(data) {
                td_name.append(''+data['name']);
            }
        });

        tr.append(td_name);
        if (this.options.allowChange)
            tr.append(td_buttons);

        this.groupListFinder[groupName] = {
            // td_icon: td_icon,
            td_name: td_name,
            // td_perm: td_perm,
            td_buttons: td_buttons,
            tr: tr
        };
        this.groupTable.append(tr);

        this.drawView(groupName);
    },

    drawView: function (groupName) {
        var t = this;

        var td_buttons = this.groupListFinder[groupName].td_buttons;
        td_buttons.empty();

        /* Do not need a edit button, a remove button is enough */
        // var editButton = $('<img src="/img/pencil.png" title="edit groups" style="cursor:pointer;" />');
        // editButton.click(function(){
        //     t.makeGroupEditable(username);
        // });
        // td_buttons.append(editButton);
        var removeButton = $('<img src="/img/cross.png" title="remove from list" style="cursor:pointer;" />');
        removeButton.click(function(){
            if (window.confirm("Are you sure to remove the group " + groupName + " ?")) {
                // t.removeGroupFromList(groupName);    // This is done in the func 'removeGroup'
                t.removeGroup(groupName);
            }

        });
        td_buttons.append(removeButton);
    },

    // ajax request for add a group
    addGroup: function (groupName) {
        if (!this.options.allowChange)
            return;
        var t = this;
        ajax({
            url: 'topology/' + this.topology.id + '/group_info/' + groupName + '/add',
            data: {group: groupName},
            successFn: function(){
                t.topology.data.group_info.push(groupName);
                t.backToView(groupName);
            },
            errorFn: function(error){
                new errorWindow({error:error});
                t.backToView(groupName);
            }
        })
    },

    // ajax request for remove a group
    removeGroup: function (groupName) {
        if (!this.options.allowChange)
            return;
        var t = this;
        ajax({
            url: 'topology/' + this.topology.id + '/group_info/' + groupName + '/remove',
            data: {group: groupName},
            successFn: function () {
                var index = t.topology.data.group_info.indexOf(groupName);
                if (index > -1) {
                    t.topology.data.group_info.splice(index, 1);
                }
                t.removeGroupFromList(groupName);
            },
            errorFn: function (error) {
                new errorWindow({error:error});
                t.backToView(groupName);
            }
        })
    },

    // TODO
    backToView: function(groupName) {
        if ($.inArray(groupName, this.topology.data.group_info) && this.topology.data.group_info !== null) {
            this.drawView(groupName);
        } else {
            this.removeGroupFromList(groupName);
        }
    },

    // TODO
    // Remove the group row on the dialog
    removeGroupFromList: function(groupName) {
        this.groupListFinder[groupName].tr.remove();
        delete this.groupListFinder[groupName];
    },

    toType: function (obj) {
        return ({}).toString.call(obj).match(/\s([a-zA-Z]+)/)[1].toLowerCase();
    }
});