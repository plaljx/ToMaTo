## Bug List

* 删除主拓扑时，不会顺带删除其下的子拓扑
    * 导致"游离"的子拓扑保留对已删除拓扑的空引用
    * 此时导致`get_topology_by_sub_topology`抛出`DoesNotExist`错误

## Test List

* 测试子拓扑、主拓扑的删除
    * 删除主拓扑后，其下子拓扑应同时被删除（已测试无法实现，已加入Bug List）
    * 删除子拓扑后，主拓扑应从`sub_topologies`中删除对其的引用
* 测试重新实现的Group Topology List (All)

## Todo List

#### 紧急or易于实现

* Group Info页面中的Topology List by Sub Topology，并测试
* 完成sub topology相关的前端部分功能
    * 按钮、对话框等
    * 查看已有的 Group <=> SubTopology 关系
* 设计并实现子拓扑的删除功能
    * 删除子拓扑后其上的元素如何处理？
* 完成子拓扑相关的基本权限验证功能
    * 创建、删除、更名子拓扑的权限

#### 难于实现

* 完成子拓扑相关的高级权限验证功能
    * 涉及到topology, element, connection
* 只能访问部分 sub topo 时的ajax数据交互
    * 现在会传回完整topology info，包括所有的元素、链接、子拓扑
    * 每个子拓扑有`permitted`字段，决定是否加入底部的sub topo tab
    * 不安全
    * 设法只传回不要的信息


