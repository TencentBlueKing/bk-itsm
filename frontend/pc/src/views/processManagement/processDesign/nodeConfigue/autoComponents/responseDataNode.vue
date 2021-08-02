<!--
  - Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
  -
  - License for BK-ITSM 蓝鲸流程服务:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
    <div class="bk-get-param">
        <bk-table
            :data="tableList"
            :size="'small'">
            <bk-table-column :label="$t(`m.treeinfo['名称']`)" min-width="200">
                <template slot-scope="props">
                    <div class="bk-more">
                        <span :style="{ paddingLeft: 20 * props.row.level + 'px' }">
                            <span
                                v-if="props.row.has_children"
                                :class="['bk-icon', 'tree-expanded-icon', props.row.showChildren ? 'icon-down-shape' : 'icon-right-shape']"
                                @click="changeState(props.row)">
                                </span>
                            <span class="bk-icon bk-more-icon" v-else> </span>
                            <span>{{props.row.key || '--'}}</span>
                        </span>
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.treeinfo['类型']`)" prop="type"></bk-table-column>
            <bk-table-column :label="$t(`m.treeinfo['是否必须']`)">
                <template slot-scope="props">
                    {{ props.row.is_necessary ? $t(`m.treeinfo["是"]`) : $t(`m.treeinfo["否"]`) }}
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.treeinfo['备注']`)" width="100">
                <template slot-scope="props">
                    <span :title="props.row.desc">{{props.row.desc || '--'}}</span>
                </template>
            </bk-table-column>
            <bk-table-column v-if="isStatic" :label="$t(`m.treeinfo['参数值']`)" width="270">
                <template slot-scope="props">
                    {{ props.row.customValue || '--' }}
                </template>
            </bk-table-column>
            <bk-table-column v-else-if="isCustom" :label="$t(`m.treeinfo['参数值']`)" width="270">
                <template slot-scope="props">
                    <bk-input
                        class="bk-respone-input"
                        :clearable="true"
                        :type="'text'"
                        :placeholder="$t(`m.treeinfo['请输入参数值']`)"
                        v-model="props.row.customValue">
                    </bk-input>
                </template>
            </bk-table-column>
            <bk-table-column v-else :label="$t(`m.treeinfo['引用为全局变量']`)" width="300">
                <template slot-scope="props">
                    <template v-if="props.row.isSelectAbled">
                        <bk-checkbox style="width: 40px; position: absolute; top: 12px; left: 15px;"
                            :true-value="trueStatus"
                            :false-value="falseStatus"
                            v-model="props.row.isSelectedKey"
                            :disabled="props.row.isSelectedKeyDisabled"
                            @change="selectOneKey(props.row)">
                        </bk-checkbox>
                        <bk-input :class="{ 'bk-border-error': props.row.isCheck && !props.row.isSelectedValue.toString() }"
                            class="bk-respone-input"
                            :clearable="true"
                            :type="'text'"
                            :placeholder="$t(`m.treeinfo['请输入变量名']`)"
                            :disabled="props.row.isSelectedValueDisabled"
                            v-model="props.row.isSelectedValue">
                        </bk-input>
                    </template>
                    <template v-else>
                        <span>--</span>
                    </template>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>

<script>
    import mixins from '../../../../commonMix/mixins_api.js'

    export default {
        name: 'responseDataNode',
        components: {
            
        },
        mixins: [mixins],
        props: {
            changeInfo: {
                type: Object,
                default () {
                    return {}
                }
            },
            apiDetail: {
                type: Object,
                default: () => {
                }
            },
            stateList: {
                type: Array,
                default () {
                    return []
                }
            },
            isCustom: {
                type: Boolean,
                default: false
            },
            isStatic: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                trueStatus: true,
                falseStatus: false,
                cascaderData: [],
                // 组织架构
                organization: {
                    processorPerson: [],
                    processorTree: {},
                    assignorPerson: [],
                    assignorTree: {}
                },
                organizaInfo: {
                    assignorShow: false
                },
                bodyTableData: [],
                responseTableData: [],
                paramTableData: [],
                // 校验
                checkInfo: {
                    name: '',
                    road: ''
                },
                sourceTypeList: [
                    {
                        id: 1,
                        key: 'CUSTOM',
                        name: this.$t(`m.treeinfo["自定义"]`)
                    },
                    {
                        id: 2,
                        key: 'FIELDS',
                        name: this.$t(`m.treeinfo["引用变量"]`)
                    }
                ],
                paramTableInfo: {
                    value: '',
                    placeholder: this.$t(`m.treeinfo["请选择数据来源"]`)
                },
                selectInfo: {
                    selectkeylist: [],
                    selectkey: '',
                    selectvaluelist: [],
                    selectvalue: ''
                },
                isShow: false,
                // 是否可选取非对象作为全局变量
                objIsCanUse: false
            }
        },
        computed: {
            tableList () {
                return this.responseTableData.filter(item => item.isShow)
            }
        },
        watch: {
            apiDetail (newVal, oldVal) {
                this.initData()
            }
        },
        mounted () {
            this.initData()
        },
        methods: {
            initData () {
                this.responseTableDataChange()
            },
            async responseTableDataChange () {
                if (!Object.keys(this.apiDetail.rsp_data).length) {
                    this.apiDetail['responseTreeDataList'] = [{
                        has_children: false,
                        showChildren: false,
                        checkInfo: false,
                        key: 'root',
                        is_necessary: true,
                        type: 'object',
                        desc: this.$t(`m.treeinfo["初始化数据"]`),
                        parentInfo: '',
                        children: []
                    }]
                    this.apiDetail['responseTableData'] = []
                } else {
                    this.apiDetail['responseTreeDataList'] = await this.jsonschemaToList(
                        {
                            root: JSON.parse(JSON.stringify(this.apiDetail.rsp_data)) // root初始 Jsonschema数据结构
                        }
                    )
                    this.apiDetail['responseTableData'] = await this.treeToTableList(
                        JSON.parse(JSON.stringify(this.apiDetail['responseTreeDataList'][0].children))
                    )
                }
                const responseTableData = await JSON.parse(JSON.stringify(this.apiDetail['responseTableData']))
                await responseTableData.forEach(
                    item => {
                        // 校验数据
                        item['isCheck'] = false
                        item['isSatisfied'] = false
                        // 定位
                        item['el'] = null

                        item['children'] = []
                        item['source_type'] = ''
                        item['customValue'] = item.value
                        item['value'] = ''
                        item['name'] = item['key']
                        // 是否可选
                        item['isSelectAbled'] = false
                        // 选取变量
                        item['isSelectedKey'] = false
                        // item['isSelectedKeyDisabled'] = false
                        // 变量名
                        item['isSelectedValue'] = ''
                        item['isSelectedValueDisabled'] = true
                    }
                )
                // 多层列表数据 关联 table表格数据
                await this.recordChildren(responseTableData)
                // 标记父级元素 方便数据处理
                await this.recordParent(responseTableData)
                // 标记数据
                await this.showSelectAbled(responseTableData)
                // 标记可选数据
                await responseTableData.filter(
                    item => (item.isSelectAbled)
                ).forEach(
                    async item => {
                        await this.markCanUseArray(item)
                    }
                )
                this.responseTableData = await responseTableData
                // 拼接可用数据 table表格数据 --> 多层列表数据
                this.cascaderData = await this.makeArrayTree(
                    this.responseTableData.filter(
                        item => (!item.level)
                    )
                )
                // 派单人组织架构
                this.organization.assignorPerson = JSON.parse(JSON.stringify(this.cascaderData))
                await this.organization.assignorPerson.forEach(tree => {
                    this.treeData(tree, 'assignors')
                })
                if (this.isCustom) {
                    // 自定义参数值得情况没有 changeInfo
                    return
                }
                if (this.changeInfo.api_info && this.changeInfo.api_info.remote_api_id === this.apiDetail.id) {
                    // 赋值 -- res
                    await this.changeInfo.variables.outputs.filter(
                        item_ => {
                            return item_.source === 'global'
                        }
                    ).forEach(
                        async item => {
                            let rspData = await item.ref_path.split('.')
                            let rspDataList = await rspData.map(
                                (ite, index) => {
                                    ite = index + '_' + ite
                                    return ite
                                }
                            )
                            this.responseTableData.filter(
                                ite => {
                                    return ite.ancestorsList_str === rspDataList.toString()
                                }
                            ).forEach(
                                it => {
                                    it['isSelectedKey'] = true
                                    // it['isSelectedValue'] = item.key
                                    it['isSelectedValue'] = item.name
                                    it['isSelectedValueDisabled'] = false
                                }
                            )
                        }
                    )
                    this.$parent.$parent.lineInfo.between = this.changeInfo.api_info.succeed_conditions.type
                }
                if (this.changeInfo.api_info && this.changeInfo.api_info.remote_api_id === this.apiDetail.id &&
                    this.changeInfo.api_info.succeed_conditions && this.changeInfo.api_info.succeed_conditions.expressions
                    && this.changeInfo.api_info.succeed_conditions.expressions.length) {
                    this.$parent.$parent.lineInfo.expressions = await this.changeInfo.api_info.succeed_conditions.expressions.map(
                        item => {
                            let objz = {
                                'type': item.type,
                                'expressions': []
                            }
                            objz.expressions = item.expressions.map(
                                ite => {
                                    let ancestorsListStr = ite.key.split('.').map(
                                        (ite, index) => {
                                            ite = index + '_' + ite
                                            return ite
                                        }
                                    ).toString()
                                    let selectObj = this.responseTableData.filter(
                                        it => {
                                            return it.ancestorsList_str === ancestorsListStr
                                        }
                                    )[0]
                                    let obj = {
                                        condition: ite.condition,
                                        key: ancestorsListStr,
                                        name: '',
                                        choiceList: '',
                                        value: ite.value,
                                        type: selectObj ? selectObj.type : 'string',
                                        // 组织架构
                                        organization: {
                                            assignorPerson: [],
                                            assignorTree: {}
                                        },
                                        organizaInfo: {
                                            assignorShow: false
                                        }
                                    }
                                    if (
                                        obj.type === 'boolean'
                                    ) {
                                        obj.value = obj.value ? '1' : '0'
                                    }
                                    obj.organization.assignorPerson = JSON.parse(JSON.stringify(this.cascaderData))
                                    obj.organization.assignorPerson.forEach(tree => {
                                        this.treeData(tree, 'assignors', obj, ancestorsListStr)
                                    })
                                    return obj
                                }
                            )
                            return objz
                        }
                    )
                } else {
                    await this.$parent.$parent.lineInfo.expressions.forEach(
                        item => {
                            item.expressions.forEach(
                                async ite => {
                                    let cascaderDataCopy = JSON.parse(JSON.stringify(this.cascaderData))
                                    await cascaderDataCopy.forEach(tree => {
                                        this.treeData(tree, 'assignors')
                                    })
                                    ite.organization.assignorPerson = cascaderDataCopy
                                }
                            )
                        }
                    )
                }
            },
            treeData (tree, type, organizationOri, ancestorsListStr) {
                tree.checkInfo = false
                tree.has_children = !!(tree.children && tree.children.length)
                tree.showChildren = false
                // 选中操作角色
                if (ancestorsListStr === String(tree.ancestorsList_str) && organizationOri && ancestorsListStr) {
                    tree.checkInfo = true
                    organizationOri.organization.assignorTree = tree
                }
                if (!tree.has_children) {
                    return
                }
                tree.children.forEach(item => {
                    this.treeData(item, type, organizationOri, ancestorsListStr)
                })
            },
            // 多层列表数据 关联 table表格数据
            recordChildren (tableData, levelInitial) {
                const levelList = tableData.map(
                    item => {
                        return item['level']
                    }
                )
                const maxLevel = Math.max(...levelList)
                const recordChildrenStep = function (tableData, item) {
                    tableData.filter(ite => {
                        return (ite.level === item.level - 1 && ite.primaryKey === item.parentPrimaryKey && ite.ancestorsList.toString() === item.ancestorsList.slice(0, -1).toString())
                    })[0].children.push(item)
                }
                for (let i = maxLevel; i > (levelInitial || 0); i--) {
                    tableData.filter(item => {
                        return item.level === i
                    }).forEach(
                        ite => {
                            recordChildrenStep(tableData, ite)
                        }
                    )
                }
            },
            // 标记父级元素 方便数据处理
            recordParent (tableData, levelInitial) {
                const levelList = tableData.map(
                    item => {
                        return item['level']
                    }
                )
                const maxLevel = Math.max(...levelList)
                const recordParentStep = function (tableData, item) {
                    // tree.parentInfo = parentInfo
                    if (!item.level) {
                        item.parentInfo = ''
                    } else {
                        item.parentInfo = tableData.filter(ite => {
                            return (ite.level === item.level - 1 && ite.primaryKey === item.parentPrimaryKey && ite.ancestorsList.toString() === item.ancestorsList.slice(0, -1).toString())
                        })[0]
                    }
                }
                for (let i = 0; i <= (levelInitial || maxLevel); i++) {
                    tableData.filter(item => {
                        return item.level === i
                    }).forEach(
                        ite => {
                            recordParentStep(tableData, ite)
                        }
                    )
                }
            },
            // 标记可选数据
            markCanUseArray (data) {
                data['isCanUseArray'] = true
                if (data.level) {
                    this.markCanUseArray(data.parentInfo)
                }
            },
            // 拼接可用数据
            makeArrayTree (dataOri, isAll) {
                let treeList = []
                let makeArrayTreeStep = function (treeListOri, data) {
                    data.forEach(
                        item => {
                            if (item.isCanUseArray || !!isAll) {
                                let data = {
                                    isCheck: false,
                                    isShow: false,
                                    isShowChildren: false,
                                    isSelect: false
                                }
                                data['name'] = item['name']
                                data['type'] = item['type']
                                data['isSelect'] = false
                                data['ancestorsList_str'] = item['ancestorsList_str']
                                let children = item.children
                                data.children = []
                                treeListOri.push(data)
                                if (children && children.length) {
                                    makeArrayTreeStep(data.children, children)
                                }
                            }
                        }
                    )
                }
                makeArrayTreeStep(treeList, dataOri)
                return treeList
            },
            changeState (item) {
                item.showChildren = !item.showChildren
                item.children.forEach(
                    ite => {
                        ite['isShow'] = item.showChildren
                        // this.$set(ite, 'isShow', item.showChildren)
                    }
                )
                if (!item.showChildren) {
                    this.closeChildren(item)
                }
            },
            closeChildren (item) {
                item.children.forEach(
                    ite => {
                        ite['isShow'] = false
                        // this.$set(ite, 'isShow', item.showChildren)
                        if (ite.has_children) {
                            ite['showChildren'] = false
                            this.closeChildren(ite)
                        }
                    }
                )
            },
            selectOneKey (itemData) {
                // 自动填充 名字
                itemData.isSelectedValue = itemData.isSelectedValue || itemData.key
                itemData.isSelectedValueDisabled = !itemData.isSelectedKey
            },
            // 计算祖先元素有几个是Array
            countArrayAncestors (data) {
                let ids = []
                const countArrayAncestorsStep = function (item) {
                    if (item.parentInfo.type === 'array') {
                        ids.push(item.parentInfo)
                        countArrayAncestorsStep(item.parentInfo)
                    }
                    if (item.parentInfo.type === 'object') {
                        countArrayAncestorsStep(item.parentInfo)
                    }
                }
                countArrayAncestorsStep(data)
                return ids
            },
            // 标记可用数据
            async showSelectAbled (responseTableData) {
                let isArrayList = []
                if (this.objIsCanUse) {
                    // 除数组内元素不可选
                    isArrayList = responseTableData.filter(item => (
                        !this.countArrayAncestors(item).length
                    ))
                } else {
                    // 数组内元素不可选
                    isArrayList = responseTableData.filter(item => (
                        !this.countArrayAncestors(item).length && item.type !== 'object' && item.type !== 'array'
                    ))
                }
                isArrayList.forEach(
                    item => {
                        item['isSelectAbled'] = true
                    }
                )
            }
        }
    }
</script>

<style lang="scss" scoped>
    .bk-more {
        &.bk-value {
            // padding-right: 72px;
            position: relative;
            justify-content: space-between;
        }

        overflow: visible;
        display: flex;
        align-items: center;

        .bk-icon {
            padding-right: 5px;
            color: #c0c4cc;
            cursor: pointer;
        }

        .bk-more-icon {
            width: 17px;
        }
    }

    .bk-body-value {
        width: 100%;
        background: white;
        display: flex;
        justify-content: flex-start;

        .bk-form-radio:nth-child(1) {
            // margin: 0 10px;
            margin-right: 10px;
        }
        & > div {
            display: inherit;
        }
        .bk-form-radio {
            display: inherit;
            margin: 0;
        }
    }

    .bk-between-operat {
        font-size: 18px;
        position: absolute;
        top: 7px;
        right: 10px;
        .bk-itsm-icon {
            color: #C4C6CC;
            margin-right: 5px;

            &:hover {
                color: #979BA5;
            }

            &.bk-no-delete {
                color: #DCDEE5;
                cursor: not-allowed;

                &:hover {
                    color: #DCDEE5;
                }
            }

            cursor: pointer;
        }
    }
    .bk-respone-input {
        width: 240px;
        position: absolute;
        top: 4px;
        right: 15px;
    }
</style>
