<template>
    <div>
        <bk-table :data="list">
            <bk-table-column width="40">
                <template slot-scope="props">
                    <bk-checkbox v-model="props.row.select"></bk-checkbox>
                </template>
            </bk-table-column>
            <bk-table-column label="字段名">
                <template slot-scope="props">
                    <bk-input :behavior="'simplicity'" v-model="props.row.name" @change="changeInput(props.row)"></bk-input>
                </template>
            </bk-table-column>
            <bk-table-column label="值">
                <template slot-scope="props">
                    <bk-input :behavior="'simplicity'" v-model="props.row.value" @change="changeInput(props.row)"></bk-input>
                </template>
            </bk-table-column>
            <bk-table-column label="描述">
                <template slot-scope="props">
                    <bk-input :behavior="'simplicity'" v-model="props.row.desc" @change="changeInput(props.row)"></bk-input>
                </template>
            </bk-table-column>
            <bk-table-column width="40">
                <template slot-scope="props">
                    <i class="bk-itsm-icon icon-itsm-icon-three-one" @click="handleDelete(props.row)"></i>
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
            }
        },
        methods: {
            changeTab (item, index) {
                this.acticeTab = item.name
            },
            handleDelete (row) {
                const index = this.list.indexOf(row)
                if (index !== -1) {
                    this.list.splice(index, 1)
                }
            },
            changeInput (val) {
                if (!val.check) {
                    val.check = true
                    val.select = true
                    this.list.push({
                        check: false,
                        name: '',
                        value: '',
                        desc: '',
                        select: false
                    })
                } else {
                    const { name, value, desc } = val
                    const checkList = [name, value, desc]
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

<style>

</style>
