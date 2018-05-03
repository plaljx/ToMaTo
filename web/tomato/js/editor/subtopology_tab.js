/**
 * this is only a UI thing
 * use funcs in topology.js when doing sub-topology operations 
 */
var SubTopologyTab = Class.extend({

    init: function(container, editor) {
        var t = this;
        this.container = container;
        this.editor = editor;
        this.subtopologies = {};

        this.addButton = $('<button/>');
        this.addButton.addClass('btn btn-primary');
        this.addButtonInnerSpan = $('<span/>');
        this.addButtonInnerSpan.addClass('glyphicon glyphicon-plus');
        this.addButton.append(this.addButtonInnerSpan);
        // this.addButton.text('New SubTopology');
        this.addButton.click(function() {
            t.editor.topology.subtopolgyAddDialog();
        });

        this.ul = $('<ul/>');
        this.ul.addClass('nav nav-tabs');

        this.container.append(this.addButton);
        this.container.append(this.ul);
    },

    addTab: function(id, name) {
        var t = this;
        var liTag = $('<li/>');
        var aTag = $('<a/>')
        liTag.attr('role', 'presentation');
        liTag.attr('st_id', id);
        liTag.append(aTag);
        aTag.text(name);
        aTag.attr('st_id', id);
        aTag.addClass('subtopology_tag');
        aTag.css('cursor', 'pointer');
        aTag.click(aTag.attr('st_id'), function(e) {
            t.editor.topology.switchSubTopology(e.data);  // e.data here is the sub-topo id
        });
        // aTag.contextmenu(aTag.attr('st_id'), function(e) {
        //     e.preventDefault();
        //     e.stopImmediatePropagation();
        //     t.createSubtopologyTabMenu();
        // });

        $.contextMenu({
            selector: '.subtopology_tag',
            trigger: 'right',
            build: function(trigger, e) {
                e.preventDefault();
                e.stopImmediatePropagation();
                return t.createSubtopologyTabMenu(trigger[0]);
            }
        });

        this.ul.append(liTag);

        this.subtopologies[id] = {};
        this.subtopologies[id].name = name;
        this.subtopologies[id].tab = liTag;
    },

    activeTabById: function(id) {
        Object.keys(this.subtopologies).forEach(function(key) {
            if (key === id) {
                this.subtopologies[tab].addClass('active');
            } else {
                this.subtopologies[tab].removeClass('active');
            }
        });
    },

    activeTabByName: function(name) {
        alert('sub_topology_tabs.js - activeTabByName: Not Implemented!');
    },

    removeTabById: function(id) {
        var toRemove = this.subtopologies[id];
        if (toRemove) {
            toRemove.tab.remove(); // remove the correspond <li/>
            delete this.subtopologies[id]; // remove from the subtopologies dict
        }
    },

    removeTabByName: function(name) {
        alert('sub_topology_tabs.js - removeByName: Not Implemented!');
    },

    createSubtopologyTabMenu: function(obj) {
        var t = this;
        var header, menu;
        var st_name = obj.text; // name
        var st_id = obj.getAttribute('st_id');
        header = {
            html: '<span>' + st_name + '<br/>'
                + '<small>' + st_id + '</small>'
                + '</span>',
            type: 'html'
        };

        menu = {
            callback: function(key, options) {},
            items: {
                "header": header,
                "remove": {
                    "name": gettext("Remove Subtopology"),
                    "callback": function(){
                        t.editor.topology.removeSubTopology(st_id);
                    }
                },
                "add_group": {
                    "name": gettext("Add Group"),
                    "callback": function(){
                        t.editor.topology.subTopologyAddGroupDialog(st_id);
                    }
                }
            }
        };

        return menu;
    },

});