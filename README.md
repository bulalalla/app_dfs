1. 为什么要使用ui2？
   因为，ui2在动态界面中依然能够较快的捕获当前屏幕的元素，Android自带的uiautomator工具在页面有动画/视频时，不工作，appium-uiautomator-driver在界面有视频时（动画不知是否会等待动画加载完毕），也是会等待视频加载完毕后再执行，所以时间会比较慢。


### 核心理念
前提：不同的组件要有不同的content-desc和text描述
1. 若发现某个xml树的node属性是不可点击，但实际是可以点击的，那么在此xml树此node网上找，一定有一个是可点击的，而且不会往上找很多即可找到
2. 对于两个界面，如果他们的resource-id大部分相同，则认为是相同界面（可以附带 bounds 来一起判别两个界面是否相同）
3. 对于一个组件，id 可以是 resource-id + bounds or+ text or+ content-desc，双描述id (resource-id + bounds, resource-id + text + content-desc) 前者弱判定，后者强判定
resource-id + bounds: 决定了这个组件的类别以及出现的位置
resource-id + content-desc + text: 决定了这个组件的类别和内容
弱判定相同的组件，希望认为是同一类，强判定相同的，就是同一个组件，对于同一类/个组件，操作后应该记录在一起，如 某个位置每次加载会改变内容，这是应判定为同一类，操作应该记录在一起；某个位置每次加载内容都不变，这应该判定为同一个，操作也应该记录在一起

4. 执行操作后，无论如何都要dump，都要进行是否进入新界面，当前可操作元素判断等
5. 关于概率问题 双描述id 重复在50%以上认为界面相同，否则认为不同，因为：
    a. 若两个组件时同一个，那么它的强判定id必然相同，因此至少有强判定id会匹配50%（不那么严谨，因为此时只考虑了组件位置会改变，没考虑组件可能会跑到屏幕外面）
6. 去除layout：因为核心在组件

### 设计

包括类设计和操作算法设计

#### 类
类设计应该尽可能的承揽所有计算操作，减少操作算法设计中的计算

界面类 UI：表示一个屏幕所容纳的界面

    id_set or id_list: 双id列表/集合，表示此界面所包含的组件信息（可以考虑是xml树上的所有叶子节点）
    clickable_elements, scrollable_elements, ... : 表示各种类型的元素
    __eq__函数：判断两个屏幕是否相等
    
界面元素类 UIElement：表示一个界面元素

    id: 一个双id
    attributes ...
    bounds: 边界 tuple((x1, y1), (x2, y2))
    center: 中心
    xpath: 此element的xpath路径



#### 操作算法设计
操作算法设计应该仅专注于如何根据数据产生操作对象


#### 问题日志
1. 发现有限组件无法获取到：抖音搜索页面无法获取推荐的那些条目，文字