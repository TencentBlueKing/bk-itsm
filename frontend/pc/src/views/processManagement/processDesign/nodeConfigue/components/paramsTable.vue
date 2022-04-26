<template>
    <div>
        <bk-table :data="list" :disabled="true">
            <bk-table-column width="40">
                <template slot-scope="props">
                    <bk-checkbox v-model="props.row.select" :disabled="disable"></bk-checkbox>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m['字段名']`)">
                <template slot-scope="props">
                    <bk-input :behavior="'simplicity'" :disabled="disable" v-model="props.row.key" @change="changeInput(props.row, props.$index)"></bk-input>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m['值']`)">
                <template slot-scope="props">
                    <bk-popover :ref="`inputParam${props.$index}`" placement="bottom" theme="light">
                        <bk-input :behavior="'simplicity'" :disabled="disable" v-model="props.row.value" @change="changeInput(props.row, props.$index)"></bk-input>
                        <!-- <bk-button>下边</bk-button> -->
                        <div slot="content" class="params-select-value">
                            <ul class="params-select">
                                <li v-for="(item, index) in wwwFormData"
                                    :key="index"
                                    @click="handleSelectContent(item)">
                                    {{item.name}}
                                    <span class="variable-key">({{item.key}})</span>
                                </li>
                            </ul>
                        </div>
                    </bk-popover>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m['描述']`)">
                <template slot-scope="props">
                    <bk-input :behavior="'simplicity'" :disabled="disable" v-model="props.row.desc" @change="changeInput(props.row, props.$index)"></bk-input>
                </template>
            </bk-table-column>
            <bk-table-column width="40">
                <template slot-scope="props" v-if="isShowDelete !== list.indexOf(props.row)">
                    <i v-if="!disable" class="bk-itsm-icon icon-itsm-icon-three-one" @click="handleDelete(props.row)"></i>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>

<script>
    export default {
        name: 'paramsTable',
        props: {
            list: {
                type: Array,
                defalut: () => []
            },
            disable: {
                type: Boolean,
                default () {
                    return false
                }
            },
            stateList: Array
        },
        data () {
            return {
                formData: [],
                wwwFormData: [],
                curCulum: '',
                curIndex: '',
                filterParams: ''
            }
        },
        computed: {
            isShowDelete () {
                return this.list.length - 1
            },
            isShowSelect () {
                return this.wwwFormData.length === 0
            }
        },
        methods: {
            changeTab (item, index) {
                this.acticeTab = item.key
            },
            handleDelete (row) {
                const index = this.list.indexOf(row)
                if (index !== -1) {
                    this.list.splice(index, 1)
                }
            },
            handleSelectContent (item) {
                this.list[this.curIndex].value = this.list[this.curIndex].value.slice(0, -(this.filterParams.length + 2)) + `{{ ${item.key}}}`
                this.$refs['inputParam' + this.curIndex].hideHandler()
            },
            changeInput (item, rowIndex) {
                const index = item.value.lastIndexOf('\{\{')
                this.curIndex = ''
                if (index !== -1) {
                    this.$refs['inputParam' + rowIndex].showHandler()
                    const params = item.value.substring(index + 2, item.value.length) || ''
                    this.filterParams = params || ''
                    this.wwwFormData = this.stateList.filter(item => {
                        return item.name.indexOf(params) !== -1 || item.key.indexOf(params) !== -1
                    })
                    this.curIndex = rowIndex
                }
                this.curCulum = item
                // 输入清除error
                this.$emit('changeFormStatus', false)
                // this.handleSelectContent(item)
                if (!item.check) {
                    item.check = true
                    item.select = true
                    this.list.push({
                        check: false,
                        key: '',
                        value: '',
                        desc: '',
                        select: false
                    })
                } else {
                    const { key, value, desc } = item
                    const checkList = [key, value, desc]
                    if (checkList.every(item => item === '')) {
                        this.list.pop()
                        item.check = false
                        item.select = false
                    }
                }
            }
        }
    }
</script>

<style lang='scss' scoped>
@import '../../../../../scss/mixins/scroller.scss';
.icon-itsm-icon-three-one {
    font-size: 16px;
    cursor: pointer;
}
.params-select-value {
    width: 200px;
    height: 200px;
    // padding: 0;
}
.params-select {
    position: absolute;
    background-color: #fff;
    // border: 1px solid #c4c6cc;
    border-radius: 4px;
    font-size: 12px;
    z-index: 100;
    width: 200px;
    height: 200px;
    overflow: auto;
    @include scroller;
    li {
        height: 30px;
        line-height: 15px;
        cursor: pointer;
        color: #75777f;
        &:hover {
            background-color: #e1ecff;
            color: #3a84ff;
        }
    }
}
/deep/ .tippy-tooltip {
    padding: 0;
}
/deep/ .tippy-arrow {
    display: none;
}
/deep/ .bk-tooltip {
    display: block;
    .bk-tooltip-ref {
        display: block;
    }
}
</style>
