## Now Doing

* [ ] 子拓扑功能相关的URL和参数中，使用子拓扑ID，而非名字
    * [x] 部分实现
* [x] 建立element <-> sub_topo和connection <-> sub_topo的关系
    * [x] 在element和connection中加入对sub topo的外键引用
* [ ] 实现子拓扑删除功能
    * [x] 先删除其中的元素、链接，参考Topology删除
    * [x] 删除子拓扑后，也一并删除主拓扑的`sub_topoloies`中的引用
    * [x] created，非prepared状态下的拓扑，已经能够删除子拓扑及其下的元素
    * [ ] **重要限制**：**至少保留一个子拓扑**
    * [ ] 前端未完成：成功后不能自动从底部tab删除子拓扑按钮，需要刷新
    * [ ] 测试更复杂条件下的子拓扑删除
        * [ ] prepared，started状态下测试删除子拓扑
        * [ ] 有跨子拓扑连接的情况下测试删除子拓扑

## Bug List

* [ ] 跨子拓扑连接会出错
    * [ ] 修复后测试有跨子拓扑连接的情况下，删除一个子拓扑
* [ ] 删除主拓扑时，不会顺带删除其下的子拓扑
    * 导致"游离"的子拓扑保留对已删除拓扑的空引用
    * 此时导致`get_topology_by_sub_topology`抛出`DoesNotExist`错误
    * 可能需要手动处理
* [ ] Topology List by Sub Topology会显示全部拓扑

## Test List

* 测试重新实现的Group Topology List (All)

## Todo List

#### 紧急or易于实现

* 完成sub topology相关的前端部分功能
    * 按钮、对话框等
    * 查看已有的 Group <=> SubTopology 关系
* 目前删除子拓扑先destroy整个拓扑的元素
    * 能否stop而非destroy？
* 完成子拓扑相关的基本权限验证功能
    * 创建、删除、更名子拓扑的权限
* 考虑在子拓扑功能相关的URL和参数中，使用子拓扑ID，而非名字

#### 难于实现

* 完成子拓扑相关的高级权限验证功能
    * 涉及到topology, element, connection
* 只能访问部分 sub topo 时的ajax数据交互
    * 现在会传回完整topology info，包括所有的元素、链接、子拓扑
    * 每个子拓扑有`permitted`字段，决定是否加入底部的sub topo tab
    * 不安全
    * 设法只传回不要的信息


