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
                    <bk-input :behavior="'simplicity'" :disabled="disable" v-model="props.row.key" @change="changeInput(props.row)"></bk-input>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m['值']`)">
                <template slot-scope="props">
                    <bk-input :behavior="'simplicity'" :disabled="disable" v-model="props.row.value" @change="changeInput(props.row)"></bk-input>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m['描述']`)">
                <template slot-scope="props">
                    <bk-input :behavior="'simplicity'" :disabled="disable" v-model="props.row.desc" @change="changeInput(props.row)"></bk-input>
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
            }
        },
        computed: {
            isShowDelete () {
                return this.list.length - 1
            }
        },
        methods: {
            changeTab (item, index) {
                this.acticeTab = item.key
            },
            handleDelete (row) {
                const index = this.list.indexOf(row)
                console.log(index)
                if (index !== -1) {
                    this.list.splice(index, 1)
                }
            },
            changeInput (val) {
                // 输入清除error
                this.$emit('changeFormStatus', false)
                if (!val.check) {
                    val.check = true
                    val.select = true
                    this.list.push({
                        check: false,
                        key: '',
                        value: '',
                        desc: '',
                        select: false
                    })
                } else {
                    const { key, value, desc } = val
                    const checkList = [key, value, desc]
                    if (checkList.every(item => item === '')) {
                        this.list.pop()
                        val.check = false
                        val.select = false
                    }
                }
            }
        }
    }
</script>

<style lang='scss' scoped>
.icon-itsm-icon-three-one {
    font-size: 16px;
    cursor: pointer;
}
</style>
